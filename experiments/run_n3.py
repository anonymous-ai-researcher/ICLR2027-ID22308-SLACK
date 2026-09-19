"""n>=3 in the standard setting, additive valuations (EFX guaranteed to exist for n=3 by Chaudhury-Garg-Mehlhorn).
   One generic budget-T algorithm: estimate every (agent,bundle) value, exhaustive search for the allocation
   with the largest minimum estimated EF slack, check EF1/EFX/EF under the truth."""
import numpy as np, itertools, json
def run(n,m,eps,Ts,seeds,rng):
    out={}
    for T in Ts:
        c=np.zeros(3)
        for s in range(seeds):
            w=rng.dirichlet(np.ones(m),size=n)                     # additive, each agent sums to 1
            bundles=[frozenset(S) for r in range(m+1) for S in itertools.combinations(range(m),r)]
            NB=n*len(bundles); per=max(1,T//NB) if T>0 else 0
            est={}
            def v(a,S): return float(sum(w[a][i] for i in S))
            def hv(a,S):
                k=(a,S)
                if k not in est: est[k]= v(a,S) if per==0 else float(np.mean(v(a,S)+rng.uniform(-0.25,0.25,per)))
                return est[k]
            best=None; bg=-9
            if T==0:
                alloc=[frozenset(range(m)[a::n]) for a in range(n)]      # information-free round-robin by index
            else:
                for assign in itertools.product(range(n),repeat=m):
                    alloc=[frozenset(i for i in range(m) if assign[i]==a) for a in range(n)]
                    gap=min(hv(a,alloc[a])-hv(a,alloc[b]) for a in range(n) for b in range(n) if a!=b)
                    if gap>bg: bg=gap; best=alloc
                alloc=best
            ef1=all(any(v(a,alloc[a])>=v(a,alloc[b]-{g})-eps for g in alloc[b]) for a in range(n) for b in range(n) if a!=b and alloc[b])
            efx=all(all(v(a,alloc[a])>=v(a,alloc[b]-{g})-eps for g in alloc[b]) for a in range(n) for b in range(n) if a!=b and alloc[b])
            ef =all(v(a,alloc[a])>=v(a,alloc[b])-eps for a in range(n) for b in range(n) if a!=b)
            c+=[ef1,efx,ef]
        out[str(T)]=(c/seeds).tolist(); print(f"  n={n} m={m} T={T:6d}: EF1={out[str(T)][0]:.3f} EFX={out[str(T)][1]:.3f} EF={out[str(T)][2]:.3f}")
    return out
rng=np.random.default_rng(0); eps=0.1; Ts=[0,300,1000,3000,10000,30000]
res={}
for n,m,seeds in ((2,6,150),(3,6,150),(4,6,100)):
    res[f"n{n}m{m}"]=run(n,m,eps,Ts,seeds,rng)
json.dump(res,open('n3_data.json','w')); print("saved")
