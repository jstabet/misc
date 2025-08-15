import argparse
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider, Button

# -------- CLI --------
def parse_args():
    p = argparse.ArgumentParser(description="Interactive gradient descent demo (1D or 2D linear regression)")
    # core mode
    p.add_argument("--num-params", type=int, default=2, choices=[1, 2],
                   help="2 -> y≈m*x+b, 1 -> y≈m*x (through origin)")
    p.add_argument("--seed", type=int, default=None, help="Random seed (None for randomness)")
    # data gen
    p.add_argument("--n", type=int, default=100, help="Number of data points")
    p.add_argument("--true-m", type=float, default=2.5, help="Ground-truth slope for data")
    p.add_argument("--true-b", type=float, default=-1.0, help="Ground-truth intercept (ignored if num-params=1)")
    p.add_argument("--noise-std", type=float, default=1.2, help="Gaussian noise std dev")
    p.add_argument("--x-min", type=float, default=-5.0, help="Domain start for x")
    p.add_argument("--x-max", type=float, default=7.0, help="Domain end for x")
    # GD run
    p.add_argument("--lr", type=float, default=0.01, help="Learning rate")
    p.add_argument("--steps", type=int, default=500, help="Number of GD iterations")
    p.add_argument("--m-init", type=float, default=None, help="Initial m (None -> random)")
    p.add_argument("--b-init", type=float, default=None, help="Initial b (None -> random; ignored if num-params=1)")
    # UI/animation
    p.add_argument("--history-max", type=int, default=None, help="Max snapshots in history panel (default: number of iterations)")
    p.add_argument("--history-stride", type=int, default=10, help="Plot every k-th line in history")
    p.add_argument("--dynamic-limits", action="store_true", help="Enable dynamic axis limits")
    p.add_argument("--play-interval-ms", type=int, default=5, help="Animation interval in ms (smaller=faster)")
    return p.parse_args()

args = parse_args()

# ======== CONFIG (derived from CLI) ========
SEED = args.seed
NUM_PARAMS = args.num_params
assert NUM_PARAMS in (1, 2), "NUM_PARAMS must be 1 or 2"

n = args.n
TRUE_M = args.true_m
TRUE_B = args.true_b
NOISE_STD = args.noise_std
X_MIN, X_MAX = float(args.x_min), float(args.x_max)

M_INIT = args.m_init
B_INIT = args.b_init
lr = args.lr
steps = args.steps

HISTORY_MAX = steps if args.history_max is None else int(args.history_max)
HISTORY_STRIDE = max(1, int(args.history_stride))
DYNAMIC_LIMITS = bool(args.dynamic_limits)
PLAY_INTERVAL_MS = int(args.play_interval_ms)
# ==========================================

# ----- Data -----
rng = np.random.default_rng(SEED)
x = np.linspace(X_MIN, X_MAX, n)
y = TRUE_M * x + (TRUE_B if NUM_PARAMS == 2 else 0.0) + rng.normal(0, NOISE_STD, n)

# ----- Helpers -----
def padded_limits(lo, hi, pad_frac=0.1, min_pad=1.0):
    span = hi - lo
    pad = max(pad_frac * max(span, 1e-12), min_pad)
    return lo - pad, hi + pad

def make_data_limits(x, y):
    xlim = padded_limits(np.min(x), np.max(x), pad_frac=0.03, min_pad=0.5)
    ylim = padded_limits(np.min(y), np.max(y), pad_frac=0.10, min_pad=1.0)
    return xlim, ylim

def make_contour_limits(x, y, m0, b0, m_star, b_star):
    x_rng = max(np.ptp(x), 1e-6)
    y_rng = max(np.ptp(y), 1e-6)
    slope_scale = y_rng / x_rng
    m_lo, m_hi = min(m0, m_star), max(m0, m_star)
    b_lo, b_hi = min(b0, b_star), max(b0, b_star)
    m_pad = max(0.3 * (m_hi - m_lo), 0.8 * slope_scale)
    b_pad = max(0.3 * (b_hi - b_lo), 0.8 * y_rng)
    return (m_lo - m_pad, m_hi + m_pad), (b_lo - b_pad, b_hi + b_pad)

def make_curve_limits(vals):
    lo, hi = float(np.min(vals)), float(np.max(vals))
    return padded_limits(lo, hi, pad_frac=0.08, min_pad=0.6)

# ----- OLS Target -----
if NUM_PARAMS == 2:
    X = np.column_stack([np.ones_like(x), x])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    b_ols, m_ols = beta
else:
    m_ols = float(np.dot(x, y) / max(np.dot(x, x), 1e-12))
    b_ols = 0.0
loss_ols = float(np.mean((m_ols * x + b_ols - y) ** 2))

# ----- Init -----
x_rng = max(np.ptp(x), 1e-6)
y_rng = max(np.ptp(y), 1e-6)
slope_scale = y_rng / x_rng
m_init = float(M_INIT) if M_INIT is not None else rng.uniform(-3.0 * slope_scale, 3.0 * slope_scale)
b_init = 0.0 if NUM_PARAMS == 1 else (float(B_INIT) if B_INIT is not None else rng.uniform(y.min() - 1.5 * y_rng, y.max() + 1.5 * y_rng))

# ----- Precompute GD path -----
m_path = np.empty(steps); b_path = np.empty(steps); loss_path = np.empty(steps)
m, b = float(m_init), float(b_init)
for t in range(steps):
    y_pred = m * x + b
    Dm = (-2.0 / len(x)) * np.sum(x * (y - y_pred))
    m -= lr * Dm
    if NUM_PARAMS == 2:
        Db = (-2.0 / len(x)) * np.sum(y - y_pred)
        b -= lr * Db
    else:
        b = 0.0
    m_path[t] = m; b_path[t] = b
    loss_path[t] = np.mean((y - (m * x + b)) ** 2)

# ----- Static limits (used when DYNAMIC_LIMITS=False) -----
data_xlim_fixed, data_ylim_fixed = make_data_limits(x, y)

if NUM_PARAMS == 2:
    m_all = np.concatenate([m_path, [m_ols, m_init]])
    b_all = np.concatenate([b_path, [b_ols, b_init]])
    cont_mlim_global, cont_blim_global = make_contour_limits(
        x, y, np.min(m_all), np.min(b_all), np.max(m_all), np.max(b_all)
    )
    mg = np.linspace(cont_mlim_global[0], cont_mlim_global[1], 220)
    bg = np.linspace(cont_blim_global[0], cont_blim_global[1], 220)
    MM, BB = np.meshgrid(mg, bg)
    ZZ = np.mean(((MM[..., None] * x) + BB[..., None] - y) ** 2, axis=-1)
else:
    m_all = np.concatenate([m_path, [m_ols, m_init]])
    mlim_global = make_curve_limits(m_all)
    mg = np.linspace(mlim_global[0], mlim_global[1], 400)
    ZZ = np.mean(((mg[:, None] * x) - y) ** 2, axis=1)
    loss_curve_ylim_fixed = make_curve_limits(ZZ)

mse_y_fixed = padded_limits(np.min(loss_path), np.max(loss_path), pad_frac=0.08, min_pad=0.0)

# ----- Figure & axes -----
fig = plt.figure(figsize=(10, 10))
gs = fig.add_gridspec(3, 2, height_ratios=[1, 1, 0.12], hspace=0.30, wspace=0.25)
ax_fit  = fig.add_subplot(gs[0, 0])
ax_hist = fig.add_subplot(gs[0, 1])
ax_loss = fig.add_subplot(gs[1, 0])
ax_mse  = fig.add_subplot(gs[1, 1])

ctrl = gs[2, :].subgridspec(1, 3, width_ratios=[10, 1.2, 1.2])
slider_ax = fig.add_subplot(ctrl[0, 0]); slider_ax.set_xticks([]); slider_ax.set_yticks([])
play_ax   = fig.add_subplot(ctrl[0, 1]); play_ax.set_xticks([]);   play_ax.set_yticks([])
reset_ax  = fig.add_subplot(ctrl[0, 2]); reset_ax.set_xticks([]);  reset_ax.set_yticks([])

# ----- Static drawings -----
ax_fit.set_title("Current fit (GD)", pad=3)
ax_fit.scatter(x, y, s=18)
ax_fit.plot(x, m_ols * x + b_ols, linestyle="--", alpha=0.8)
ax_fit.set_xlabel("x", labelpad=1); ax_fit.set_ylabel("y", labelpad=1)
fit_line, = ax_fit.plot([], [], linewidth=2)

ax_hist.set_title("History of lines", pad=3)
ax_hist.scatter(x, y, s=8, alpha=0.4)
ax_hist.set_xlabel("x", labelpad=1); ax_hist.set_ylabel("y", labelpad=1)

if NUM_PARAMS == 2:
    ax_loss.set_title("Loss contours (m,b)", pad=3)
    ax_loss.contour(MM, BB, ZZ, levels=30)
    ax_loss.plot(m_ols, b_ols, marker='x', markersize=6, linestyle='None')
    ax_loss.set_xlabel("slope m", labelpad=1); ax_loss.set_ylabel("intercept b", labelpad=1)
    path_line_loss, = ax_loss.plot([], [], marker="o", markersize=2, linestyle='-')
else:
    ax_loss.set_title("Loss curve vs slope m", pad=3)
    ax_loss.plot(mg, ZZ, linewidth=1.5, alpha=0.9)
    ax_loss.plot(m_ols, loss_ols, marker='x', markersize=6, linestyle='None')  # mark OLS min
    ax_loss.set_xlabel("slope m", labelpad=1); ax_loss.set_ylabel("MSE", labelpad=1)
    path_line_loss, = ax_loss.plot([], [], marker="o", markersize=2, linestyle='-')

ax_mse.set_title("MSE vs. iteration", pad=3)
ax_mse.set_xlabel("iteration", labelpad=1); ax_mse.set_ylabel("MSE", labelpad=1)
mse_line, = ax_mse.plot([], [], linewidth=2)

iter_slider = Slider(ax=slider_ax, label="iteration", valmin=1, valmax=steps, valinit=1, valstep=1)
play_btn    = Button(play_ax,  "Play")
reset_btn   = Button(reset_ax, "Reset")

# ----- Title -----
header_width = len(f"iter {steps}/{steps}")
def set_title(k, m_k, b_k):
    tag = "m,b" if NUM_PARAMS == 2 else "m"
    cur = f"({m_k:>7.3f}, {b_k:>7.3f})" if NUM_PARAMS == 2 else f"({m_k:>7.3f})"
    tgt = f"({m_ols:>7.3f}, {b_ols:>7.3f})" if NUM_PARAMS == 2 else f"({m_ols:>7.3f})"
    line1 = f"{('iter ' + str(k) + '/' + str(steps)):<{header_width}} | {tag} = {cur}"
    line2 = f"{'target (OLS)':<{header_width}} | {tag} = {tgt}"
    fig.suptitle(line1 + "\n" + line2, fontfamily='monospace')

# ----- Limit helpers -----
x_lo, x_hi = np.min(x), np.max(x)

def dynamic_fit_ylim(m_k, b_k):
    yy = m_k * np.array([x_lo, x_hi]) + b_k
    y_lo = min(y.min(), yy.min()); y_hi = max(y.max(), yy.max())
    return padded_limits(y_lo, y_hi, pad_frac=0.08, min_pad=0.6)

def dynamic_loss_limits_2d(k):
    m_seen = np.concatenate([m_path[:k], [m_ols]])
    b_seen = np.concatenate([b_path[:k], [b_ols]])
    (m_lo, m_hi), (b_lo, b_hi) = make_contour_limits(
        x, y, np.min(m_seen), np.min(b_seen), np.max(m_seen), np.max(b_seen)
    )
    m_lo = max(m_lo, cont_mlim_global[0]); m_hi = min(m_hi, cont_mlim_global[1])
    b_lo = max(b_lo, cont_blim_global[0]); b_hi = min(b_hi, cont_blim_global[1])
    return (m_lo, m_hi), (b_lo, b_hi)

def dynamic_loss_limits_1d(k):
    m_seen = np.concatenate([m_path[:k], [m_ols]])
    y_seen = np.concatenate([loss_path[:k], [loss_ols]])
    mx = make_curve_limits(m_seen)
    my = make_curve_limits(y_seen)
    mx = (max(mx[0], mlim_global[0]), min(mx[1], mlim_global[1]))
    my = (max(my[0], loss_curve_ylim_fixed[0]), min(my[1], loss_curve_ylim_fixed[1]))
    return mx, my

# ----- Draw state -----
def draw_state(k: int):
    m_k, b_k = m_path[k-1], b_path[k-1]

    fit_line.set_data(x, m_k * x + b_k)
    ax_fit.set_xlim(x_lo, x_hi)

    ax_hist.cla()
    ax_hist.set_title("History of lines", pad=3)
    ax_hist.set_xlabel("x", labelpad=1); ax_hist.set_ylabel("y", labelpad=1)
    ax_hist.set_xlim(x_lo, x_hi)
    ax_hist.scatter(x, y, s=8, alpha=0.4)
    snaps_idx = list(range(1, k+1, HISTORY_STRIDE))
    if snaps_idx[-1] != k: snaps_idx.append(k)
    snaps_idx = snaps_idx[-HISTORY_MAX:]
    L = len(snaps_idx)
    for i, idx in enumerate(snaps_idx):
        alpha = 0.15 + 0.8 * (i + 1) / max(L, 1)
        ax_hist.plot(x, m_path[idx-1] * x + b_path[idx-1], alpha=alpha, linewidth=1.5)

    if NUM_PARAMS == 2:
        path_line_loss.set_data(m_path[:k], b_path[:k])
    else:
        path_line_loss.set_data(m_path[:k], loss_path[:k])

    mse_line.set_data(np.arange(1, k + 1), loss_path[:k])

    if DYNAMIC_LIMITS:
        yl = dynamic_fit_ylim(m_k, b_k)
        ax_fit.set_ylim(*yl); ax_hist.set_ylim(*yl)
        if NUM_PARAMS == 2:
            (m_lo, m_hi), (b_lo, b_hi) = dynamic_loss_limits_2d(k)
            ax_loss.set_xlim(m_lo, m_hi); ax_loss.set_ylim(b_lo, b_hi)
        else:
            (mx0, mx1), (my0, my1) = dynamic_loss_limits_1d(k)
            ax_loss.set_xlim(mx0, mx1); ax_loss.set_ylim(my0, my1)
        ax_mse.set_xlim(1, max(2, k)); ax_mse.relim(); ax_mse.autoscale_view(scalex=False, scaley=True)
    else:
        ax_fit.set_ylim(*data_ylim_fixed); ax_hist.set_ylim(*data_ylim_fixed)
        if NUM_PARAMS == 2:
            ax_loss.set_xlim(*cont_mlim_global); ax_loss.set_ylim(*cont_blim_global)
        else:
            ax_loss.set_xlim(*mlim_global);     ax_loss.set_ylim(*loss_curve_ylim_fixed)
        ax_mse.set_xlim(1, steps); ax_mse.set_ylim(*mse_y_fixed)

    set_title(k, m_k, b_k)
    fig.canvas.draw_idle()

iter_slider.on_changed(lambda val: draw_state(int(val)))

# ----- Play/Pause -----
state = {"running": False}
timer = fig.canvas.new_timer(interval=PLAY_INTERVAL_MS)

def set_running(flag: bool):
    state["running"] = bool(flag)
    play_btn.label.set_text("Pause" if state["running"] else "Play")
    (timer.start if state["running"] else timer.stop)()

def tick():
    k = int(iter_slider.val)
    if k < steps: iter_slider.set_val(k + 1)
    else: set_running(False)

timer.add_callback(tick)
play_btn.on_clicked(lambda event: set_running(not state["running"]))
reset_btn.on_clicked(lambda event: (set_running(False), iter_slider.set_val(1)))

# ----- Go -----
draw_state(1)
plt.show()
