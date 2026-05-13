#!/opt/anaconda3/bin/python3
"""
plot_zeta.py  –  Instantaneous free surface snapshot from SWASH output
Usage:  python plot_zeta.py [time_index]   (default: last time step)
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

DIR = Path(__file__).resolve().parent


def parse_time(hhmmss, ms):
    h, m, s = int(hhmmss[:2]), int(hhmmss[2:4]), int(hhmmss[4:6])
    return h * 3600 + m * 60 + s + int(ms) / 1000


data = scipy.io.loadmat(DIR / 'zeta.mat')

x    = data['Xp'].squeeze()
botl = data['Botlev'].squeeze()

# Collect and sort time steps
steps = {}
for k in data:
    m = re.match(r'Watlev_(\d{6})_(\d{3})$', k)
    if m:
        t = parse_time(m.group(1), m.group(2))
        steps[t] = k
times = sorted(steps)

tidx = int(sys.argv[1]) if len(sys.argv) > 1 else len(times) - 1
tidx = max(0, min(tidx, len(times) - 1))
t    = times[tidx]
eta  = data[steps[t]].squeeze()

print(f'Snapshot t={t:.3f} s  (index {tidx}/{len(times)-1})')

fig, ax = plt.subplots(figsize=(11, 4))

ax.fill_between(x, botl, botl.min() - 0.5, color='wheat', zorder=1)
ax.plot(x, botl, 'k-', lw=1.5, label='Bed', zorder=2)
ax.fill_between(x, botl, eta, color='lightsteelblue', alpha=0.6, zorder=3)
ax.plot(x, eta, color='steelblue', lw=1.5, label='Free surface', zorder=4)

ax.set_xlabel('x (m)')
ax.set_ylabel('z (m)')
ax.set_title(f'Instantaneous free surface  –  t = {t:.2f} s')
ax.legend(loc='upper left')
ax.grid(True, alpha=0.3)
ax.set_xlim(x.min(), x.max())

plt.tight_layout()
outpath = DIR / f'zeta_t{t:.2f}s.png'
plt.savefig(outpath, dpi=150)
print(f'Saved → {outpath}')
plt.show()

# %%
