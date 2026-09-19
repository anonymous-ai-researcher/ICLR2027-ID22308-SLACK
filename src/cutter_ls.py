"""
Cutter's local search for a two-sided eps-EFX partition under ONE monotone f.
Move rule: if exists g in A with f(A\g) > f(B)+tau, move g to B (symmetric for B).
Claim: #moves <= (2/tau + 1)(m+1);  output is tau-EFX from f's view on both sides.
Tested on random coverage functions and random monotone (non-submodular) functions.
"""
import random, itertools
from functools import lru_cache
random.seed(7)

def make_coverage(m, U=12):
    # random weighted coverage on m items
    w=[random.random() for _ in range(U)]
    sets=[frozenset(u for u in range(U) if random.random()<0.35) for _ in range(m)]
    tot=sum(w)
    def f(S):
        cov=set().union(*[sets[i] for i in S]) if S else set()
        return sum(w[u] for u in cov)/tot
    return f

def make_monotone(m):
    # random monotone (not submodular): f(S) = max over a few random "dictionaries"
    keys=[frozenset(random.sample(range(m), random.randint(1,max(1,m//3)))) for _ in range(6)]
    vals=[random.random() for _ in keys]
    def f(S):
        S=frozenset(S)
        best=0.0
        for k,v in zip(keys,vals):
            if k<=S: best=max(best,v)
        return best + 0.5*len(S)/m   # + modular part to break ties, still monotone, cap<=1.5 -> rescale
    return lambda S: f(S)/1.5

def local_search(f, m, tau):
    A=set(range(m)); B=set()
    moves=0; strict=0; weak=0
    while True:
        moved=False
        for X,Y in ((A,B),(B,A)):
            fY=f(Y)
            for g in sorted(X):
                if f(X-{g}) > fY + tau:
                    # classify before moving
                    if f(Y|{g}) >= f(X-{g}): strict+=1
                    else: weak+=1
                    X.remove(g); Y.add(g); moves+=1; moved=True
                    break
            if moved: break
        if not moved: break
        assert moves <= (2/tau+2)*(m+2), "move bound violated"
    # verify two-sided tau-EFX
    ok = all(f(B) >= f(A-{g}) - tau for g in A) and all(f(A) >= f(B-{g}) - tau for g in B)
    return moves, strict, weak, ok

for name,mk in (("coverage",make_coverage),("monotone",make_monotone)):
    print(f"=== {name} ===")
    for m in (8,12,16):
        for tau in (0.05,0.1,0.2):
            worst=0; allok=True; sw=(0,0)
            for _ in range(60):
                f=mk(m); mv,st,wk,ok=local_search(f,m,tau)
                worst=max(worst,mv); allok&=ok; sw=(max(sw[0],st),max(sw[1],wk))
            bound=int((2/tau+1)*(m+1))
            print(f"  m={m:2d} tau={tau}: max moves={worst:4d} (bound {bound:4d}), max strict={sw[0]} (<= {int(2/tau)}), all outputs tau-EFX both sides: {allok}")
