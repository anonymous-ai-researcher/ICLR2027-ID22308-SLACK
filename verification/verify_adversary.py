"""Exhaustive adversary for the epoch cutter (Alg. 3).
At every consultation the estimate is allowed either extreme of its
accuracy interval [f-eps0, f+eps0]; we branch on both and follow all paths.
Counts complete paths (leaves) and checks every leaf output is two-sided eps-EFX.
"""
import random, sys
sys.setrecursionlimit(100000)

def make_coverage(m, rng, U=10):
    w=[rng.random() for _ in range(U)]
    sets=[frozenset(u for u in range(U) if rng.random()<0.35) for _ in range(m)]
    tot=sum(w)
    def f(S):
        cov=set().union(*[sets[i] for i in S]) if S else set()
        return sum(w[u] for u in cov)/tot
    return f

def make_monotone(m, rng):
    keys=[frozenset(rng.sample(range(m), rng.randint(1,max(1,m//3)))) for _ in range(6)]
    vals=[rng.random() for _ in keys]
    def f(S):
        S=frozenset(S); best=0.0
        for k,v in zip(keys,vals):
            if k<=S: best=max(best,v)
        return (best + 0.5*len(S)/m)/1.5
    return f

def anchor(m):
    # the Prop. D.2 style instance: one heavy item, rest light
    def f(S):
        return min(1.0, (0.5 if 0 in S else 0.0) + 0.5*len([x for x in S if x])/max(1,m-1))
    return f

def run(f, m, eps0, tau, cap):
    """Branch on every consultation; return (#leaves, all_ok, max_consults)."""
    leaves=0; allok=True; maxc=0
    def rec(A, B, consults, depth):
        nonlocal leaves, allok, maxc
        if consults>cap or depth>3*m: return
        branched=False
        for X,Y,isA in ((A,B,True),(B,A,False)):
            for g in sorted(X):
                vx, vy = f(X-{g}), f(Y)
                for ex_x in (vx-eps0, vx+eps0):
                    for ex_y in (vy-eps0, vy+eps0):
                        if ex_x > ex_y + tau:
                            branched=True
                            nx, ny = set(X-{g}), set(Y|{g})
                            if isA: rec(nx, ny, consults+2, depth+1)
                            else:   rec(ny, nx, consults+2, depth+1)
            if branched: break
        if branched: return
        leaves+=1; maxc=max(maxc,consults)
        ok = all(f(B) >= f(A-{g})-tau-2*eps0 for g in A) and \
             all(f(A) >= f(B-{g})-tau-2*eps0 for g in B)
        allok &= ok
    rec(set(range(m)), set(), 0, 0)
    return leaves, allok, maxc

if __name__=='__main__':
    eps=0.1; eps0=eps/8; tau=6*eps0
    total=0; allok=True
    for name, mk in (("coverage", make_coverage), ("monotone", make_monotone), ("anchor", None)):
        for m in (2,4,6):
            for s in range(4):
                rng=random.Random(1000*m+s)
                f = anchor(m) if mk is None else mk(m, rng)
                lv, ok, mc = run(f, m, eps0, tau, cap=60)
                total+=lv; allok &= ok
            print(f"  {name:9s} m={m}: cumulative leaves={total}, all eps-EFX={allok}")
    print(f"\nTOTAL complete adversarial paths: {total:,}")
    print(f"every leaf two-sided eps-EFX: {allok}")
