#!/opt/anaconda3/bin/python3
"""
plot_u.py  –  Instantaneous cross-shore velocity snapshot from SWASH output
Usage:  python plot_u.py [time_index]   (default: last time step)
"""
#%%
import sys
import re
import warnings
import numpy as np
import matplotlib.pyplot as plt
import scipy.io
from pathlib import Path

warnings.filterwarnings('ignore')

DIR  = Path(__file__).resolve().parent
NLEV = 20   # VERT 20 in input.sws


def parse_time(hhmmss, ms):
    h, m, s = int(hhmmss[:2]), int(hhmmss[2:4]), int(hhmmss[4:6])
    return h * 3600 + m * 60 + s + int(ms) / 1000


data_u    = scipy.io.loadmat(DIR / 'u.mat')
data_zeta = scipy.io.loadmat(DIR / 'zeta.mat')

x    = data_u['Xp'].squeeze()
botl = data_u['Botlev'].squeeze()

# Collect time steps (from layer 1 keys)
steps = {}
for k in data_u:
    m = re.match(r'Vksi_k01_(\d{6})_(\d{3})$', k)
    if m:
        t = parse_time(m.group(1), m.group(2))
        steps[t] = m.group(1) + '_' + m.group(2)
times = sorted(steps)

tidx = int(sys.argv[1]) if len(sys.argv) > 1 else len(times) - 1
tidx = max(0, min(tidx, len(times) - 1))
t    = times[tidx]
ts   = steps[t]

print(f'Snapshot t={t:.3f} s  (index {tidx}/{len(times)-1})')

# Assemble velocity array  (NLEV, nx)
nx = len(x)
u  = np.full((NLEV, nx), np.nan)
for k_lay in range(1, NLEV + 1):
    key = f'Vksi_k{k_lay:02d}_{ts}'
    if key in data_u:
        u[k_lay - 1] = data_u[key].squeeze()

# Free surface from zeta.mat
zeta_key = f'Watlev_{ts}'
eta = data_zeta[zeta_key].squeeze() if zeta_key in data_zeta else botl * 0

# Layer-centre z coordinates  (NLEV, nx), equidistant between bed and surface
D   = eta - botl                              # total depth (nx,)
z   = botl[np.newaxis, :] + (np.arange(1, NLEV + 1)[:, np.newaxis] - 0.5) / NLEV * D[np.newaxis, :]

# Mask dry cells
dry = D < 0.005
u[:, dry] = np.nan

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 5))

vlim = np.nanpercentile(np.abs(u), 98)
vlim = max(vlim, 0.01)

pcm = ax.pcolormesh(
    np.tile(x, (NLEV, 1)), z, u,
    cmap='RdBu_r', vmin=-vlim, vmax=vlim, shading='auto'
)
plt.colorbar(pcm, ax=ax, label='u (m/s)')

ax.fill_between(x, botl, botl.min() - 0.5, color='wheat', zorder=3)
ax.plot(x, botl, 'k-', lw=1.5, label='Bed', zorder=4)
ax.plot(x, eta,  color='steelblue', lw=1.2, label='Free surface', zorder=4)

ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')
ax.set_title(f'Instantaneous cross-shore velocity  –  t = {t:.2f} s')
ax.legend(loc='upper left')
ax.set_xlim(x.min(), x.max())
ax.set_ylim(botl.min() - 0.3, eta.max() + 0.3)

plt.tight_layout()
outpath = DIR / f'u_t{t:.2f}s.png'
plt.savefig(outpath, dpi=150)
print(f'Saved → {outpath}')
plt.show()

# %%
