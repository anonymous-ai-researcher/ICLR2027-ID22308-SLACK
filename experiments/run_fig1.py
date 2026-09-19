"""D1/D3 (vectorised): success rate vs observation budget T, frozen (EEAG) vs unfrozen (standard)."""
import numpy as np, json, sys, os, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from core import *

def sweep(m, T_list, eps, n_seed, frozen, noise='uniform', sigma=0.25, seed0=0):
    d = m//2
    # true singleton values: v1({r}) = 3/16 + (3/16)(2/m) if r in S_theta else 3/16
    lo = 3/16; hi = 3/16 + (3/16)*(2/m); gap = hi - lo
    counts = np.zeros((len(T_list), 3))
    rng = np.random.default_rng(seed0 + int(frozen))
    for s in range(n_seed):
        theta, S_theta = make_instance(m, rng)
        for ti, T in enumerate(T_list):
            if T <= 0:
                S = np.zeros(m, bool); S[0] = True
            else:
                # bit-sharing estimator of Prop. family_upper: random half-sets, conditional means per pair
                Smat = rng.random((T, m)) < 0.5
                c = (Smat & S_theta).sum(axis=1)
                v = 3/16*Smat.any(axis=1) + (3/16)*np.minimum(1.0, 2*c/m)
                y = (rng.random(T) < v).astype(float)
                even = Smat[:, 0::2]; odd = Smat[:, 1::2]
                plus = odd & ~even; minus = even & ~odd
                cp = plus.sum(axis=0); cm = minus.sum(axis=0)
                yp = np.where(cp > 0, (y[:, None]*plus).sum(axis=0)/np.maximum(cp, 1), 0.5)
                ym = np.where(cm > 0, (y[:, None]*minus).sum(axis=0)/np.maximum(cm, 1), 0.5)
                th = (yp > ym).astype(int)
                S = np.zeros(m, bool); S[2*np.arange(d) + th] = True
            r = check_frozen(S, S_theta, m, eps) if frozen else check_unfrozen(True, S, S_theta, m, eps)
            counts[ti] += r
    return counts / n_seed

m, eps, n_seed = 32, 0.0078125, 300
T_list = [0] + [int(x) for x in np.unique(np.round(np.logspace(1.0, 5.4, 22)).astype(int))]
res = {}
for frozen in (True, False):
    key = 'frozen' if frozen else 'unfrozen'
    res[key] = sweep(m, T_list, eps, n_seed, frozen, noise='bernoulli').tolist()
    print(f"--- {key}, m={m}, eps={eps}, seeds={n_seed} ---")
    for i in [0,1,5,10,15,20,len(T_list)-1]:
        a = res[key][i]; print(f"  T={T_list[i]:9d}: EF1={a[0]:.3f} EFX={a[1]:.3f} EF={a[2]:.3f}")
json.dump({'m':m,'eps':eps,'n_seed':n_seed,'T_list':T_list,'res':res,'noise':'bernoulli','algorithm':'conditional-mean (Prop. family_upper)'}, open('fig1_data.json','w'))
print("saved")
