"""Core: the hard family I_m(theta), frozen (EEAG) and unfrozen (standard), plus the
   noisy observation model and one generic budget-T algorithm whose single output is
   then checked against eps-EF1 / eps-EFX / eps-EF under the TRUE valuations."""
import numpy as np
ETA = 1.0/1024

def make_instance(m, rng):
    """theta in {0,1}^{m/2}; S_theta picks one pool item per pair."""
    d = m//2
    theta = rng.integers(0, 2, size=d)
    S_theta = np.zeros(m, dtype=bool)
    S_theta[2*np.arange(d) + theta] = True
    return theta, S_theta

def v1(S_mask, S_theta, m, has_gstar, has_gcirc):
    """S_mask: bool array over the m pool items."""
    c = int(np.sum(S_mask & S_theta))
    pool_nonempty = bool(np.any(S_mask))
    return (3/16)*pool_nonempty + (3/16)*min(1.0, 2*c/m) \
           + (3/8 - ETA)*has_gstar + ETA*has_gcirc

def v2(has_gstar, has_gcirc):
    return 0.5*has_gstar + 0.5*has_gcirc

def observe(true_val, rng, noise='uniform', sigma=0.25):
    """E[X] = true_val, X in [0,1] for the in-theory model."""
    if noise == 'uniform':
        lo, hi = max(0.0, true_val-sigma), min(1.0, true_val+sigma)
        return rng.uniform(lo, hi) + (true_val - (lo+hi)/2)
    if noise == 'bernoulli':
        return float(rng.random() < min(1.0, max(0.0, true_val)))
    if noise == 'gauss':
        return true_val + rng.normal(0, sigma)
    raise ValueError(noise)

# ---------- fairness checks under TRUE valuations ----------
def check_frozen(S_mask, S_theta, m, eps):
    """EEAG: sigma(a1)=empty, sigma(a2)={g*,g0}; extension gives a1 the set S_mask."""
    B1_v1 = v1(S_mask, S_theta, m, False, False)
    # a1's view of a2's bundle {g*,g0} and its single-item removals
    full  = v1(np.zeros(m, bool), S_theta, m, True,  True)
    rm_gs = v1(np.zeros(m, bool), S_theta, m, False, True)
    rm_gc = v1(np.zeros(m, bool), S_theta, m, True,  False)
    ef  = B1_v1 >= full  - eps
    efx = B1_v1 >= max(rm_gs, rm_gc) - eps
    ef1 = B1_v1 >= min(rm_gs, rm_gc) - eps
    # a2 never envies a1 (a1 holds only pool items, worth 0 to a2)
    return ef1, efx, ef

def check_unfrozen(assign_gstar_to_a1, S_mask, S_theta, m, eps):
    """Standard setting: algorithm also decides who gets g* and g0.
       a1 gets (g* or g0) + S_mask ; a2 gets the other special item + the rest of the pool."""
    a1_gs, a1_gc = assign_gstar_to_a1, not assign_gstar_to_a1
    B1 = v1(S_mask, S_theta, m, a1_gs, a1_gc)
    rest = ~S_mask
    B2_items = [(rest, not a1_gs, not a1_gc)]
    full = v1(*B2_items[0][0:1], S_theta, m, B2_items[0][1], B2_items[0][2]) if False else \
           v1(rest, S_theta, m, not a1_gs, not a1_gc)
    rms = [v1(rest, S_theta, m, False, not a1_gc) if not a1_gs else None,
           v1(rest, S_theta, m, not a1_gs, False) if not a1_gc else None]
    for j in np.where(rest)[0]:
        r2 = rest.copy(); r2[j] = False
        rms.append(v1(r2, S_theta, m, not a1_gs, not a1_gc))
    rms = [r for r in rms if r is not None]
    ef  = B1 >= full - eps
    efx = B1 >= max(rms) - eps
    ef1 = B1 >= min(rms) - eps
    # a2's side
    B2 = v2(not a1_gs, not a1_gc); B1_2 = v2(a1_gs, a1_gc)
    rms2 = [0.0]  # removing a1's special item leaves pool items, worth 0 to a2
    ef2  = B2 >= B1_2 - eps
    efx2 = B2 >= max(rms2) - eps
    ef12 = B2 >= min(rms2) - eps
    return (ef1 and ef12), (efx and efx2), (ef and ef2)
