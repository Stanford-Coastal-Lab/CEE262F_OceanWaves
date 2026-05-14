#!/usr/bin/env python3
"""
plot_longshore_current.py
Time- and alongshore-averaged cross-shore profiles  U(x)  and  V(x).

This is the canonical diagnostic for the oblique-wave longshore-current case:
    V_LH(x) = <v(x, y, t)>_{y, t}        with t > T_SPINUP
              and y averaged over the full periodic domain.

Reads:
    vel.mat   — SWASH BLOCK output (LAYOUT 3, VEL)
    bot.txt   — 2D bottom level

Notes:
- The first T_SPINUP seconds of snapshots are discarded so that wave
  startup and the IG-wave reflection at the shoreline don't pollute
  the mean.
- Edit T_SPINUP if your run is shorter / longer.
"""
#%%
import re
import numpy as np
import matplotlib.pyplot as plt
from scipy.io import loadmat

# -------------------------------------------------------------- params
T_SPINUP = 600.0          # discard everything before this time     [s]
DX, DY   = 2.0, 2.0
L_DOM    = 600.0
X_SHR    = 500.0
VELFILE  = "vel.mat"
BOTFILE  = "bot.txt"

# -------------------------------------------------------------- helpers
def parse_swash_time(key):
    m = re.search(r"_(\d{2})(\d{2})(\d{2})(?:_(\d{1,3}))?$", key)
    if not m:
        return None
    h, mn, s, sub = m.groups()
    t = int(h)*3600 + int(mn)*60 + int(s)
    if sub:
        t += int(sub) / 10**len(sub)
    return t

def collect_snapshots(matfile, prefixes, t_min):
    """Return (times, keys, data_dict) for snapshots after t_min."""
    data = loadmat(matfile)
    keys = [k for k in data.keys()
            if any(k.lower().startswith(p.lower()) for p in prefixes)]
    keys = sorted(keys, key=parse_swash_time)
    keys = [k for k in keys if parse_swash_time(k) >= t_min]
    times = np.array([parse_swash_time(k) for k in keys])
    return times, keys, data

# -------------------------------------------------------------- load
zb = np.loadtxt(BOTFILE)
ny, nx = zb.shape
x = np.arange(nx) * DX

t_u, keys_u, data = collect_snapshots(VELFILE,
    ("vel_x_", "Velkx", "Velx_", "Vksix", "Vx_"), T_SPINUP)
t_v, keys_v, _    = collect_snapshots(VELFILE,
    ("vel_y_", "Velky", "Vely_", "Vksiy", "Vy_"), T_SPINUP)

if not keys_u or not keys_v:
    raise SystemExit(f"No velocity snapshots past T_SPINUP = {T_SPINUP} s")

print(f"averaging {len(keys_u)} u-snapshots and {len(keys_v)} v-snapshots "
      f"from t ∈ [{t_u.min():.0f}, {t_u.max():.0f}] s")

# -------------------------------------------------------------- average
# For each snapshot: average over y; then average over time.
def reduce_yt(keys, data, shape):
    accum = np.zeros(shape[1])
    n = 0
    for k in keys:
        arr = np.array(data[k])
        if arr.shape != shape:
            arr = arr.reshape(shape)
        # mask dry cells (bed above SWL) before averaging
        m = np.ma.masked_where(-zb < 0., arr)
        accum += m.mean(axis=0).filled(0.)
        n += 1
    return accum / n

U_mean = reduce_yt(keys_u, data, zb.shape)
V_mean = reduce_yt(keys_v, data, zb.shape)

print(f"V_max = {V_mean.max():.2f} m/s  at  x = {x[np.argmax(V_mean)]:.0f} m")
print(f"U_max = {abs(U_mean).max():.2f} m/s  (cross-shore mean — undertow + setup)")

# -------------------------------------------------------------- plot
fig, ax_v = plt.subplots(1,1, figsize=(6, 3), dpi=300,
                                  gridspec_kw={"hspace": 0.08})

# longshore current — the main quantity
ax_v.plot(x, V_mean, color="#E76F51", lw=2.0,
          label=r"$\langle v \rangle_{y,t}$  (longshore)")
ax_v.set_xlabel("x  (cross-shore)  [m]")
ax_v.set_ylabel(r"$\langle v \rangle$   [m/s]")
ax_v.grid(alpha=0.3)
ax_v.legend(loc="upper left", fontsize=9)

for a in (ax_v,):
    a.axvline(X_SHR, color="#5B6B7C", lw=0.8, ls=":", alpha=0.7)
    a.set_xlim(0., L_DOM)
ax_v.text(X_SHR + 4, ax_v.get_ylim()[1] * 0.9, "shoreline",
          color="#5B6B7C", fontsize=8, style="italic")

fig.tight_layout()
fig.savefig("longshore_current.png", dpi=140)
print("wrote longshore_current.png")
plt.show()

# %%
