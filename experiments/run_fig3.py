"""Fig.3 phase surface: observations needed for eps-EFX at 95% success, over the (m, eps) plane.
   Tests Thm 3.1 (growth in m) and Prop 3.5 (barrier vanishes for eps > 3/32 - eta)."""
import numpy as np, json, sys, os, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from core import *

def success(m, eps, T, n_seed, rng, sigma=0.25):
    d=m//2; ok=0
    for _ in range(n_seed):
        theta,S_theta=make_instance(m,rng)
        if T<=0:
            S=np.zeros(m,bool); S[0]=True
        else:
            # bit-sharing estimator of Prop. family_upper (Bernoulli observations)
            Smat=rng.random((int(T),m))<0.5
            c=(Smat & S_theta).sum(axis=1); v=3/16*Smat.any(axis=1)+(3/16)*np.minimum(1.0,2*c/m)
            y=(rng.random(int(T))<v).astype(float)
            even=Smat[:,0::2]; odd=Smat[:,1::2]; plus=odd&~even; minus=even&~odd
            cp=plus.sum(axis=0); cm=minus.sum(axis=0)
            yp=np.where(cp>0,(y[:,None]*plus).sum(axis=0)/np.maximum(cp,1),0.5)
            ym=np.where(cm>0,(y[:,None]*minus).sum(axis=0)/np.maximum(cm,1),0.5)
            S=np.zeros(m,bool); S[2*np.arange(d)+(yp>ym).astype(int)]=True
        ok += check_frozen(S,S_theta,m,eps)[1]
    return ok/n_seed

def threshold_T(m, eps, n_seed, rng, target=0.95):
    if success(m,eps,0,200,rng) >= target: return 0.0
    lo,hi=1,1
    while success(m,eps,hi,n_seed,rng) < target:
        hi*=4
        if hi>4e8: return np.nan
    while hi/max(lo,1) > 1.45:
        mid=int(np.sqrt(max(lo,1)*hi))
        if success(m,eps,mid,n_seed,rng) >= target: hi=mid
        else: lo=mid
    return float(hi)

ms   = [8,12,16,24,32,48]
epss = [0.002,0.008,0.031,0.062,0.078,0.093,0.100,0.120,0.150]
import os, sys
Z=np.full((len(epss),len(ms)), np.nan)
if os.path.exists('fig3_partial.json'):
    P=json.load(open('fig3_partial.json'))
    for k,v in P.items(): Z[int(k)]=v
rows_todo=[i for i in range(len(epss)) if np.isnan(Z[i]).any()]
for i in rows_todo[:int(sys.argv[1]) if len(sys.argv)>1 else 2]:
    e=epss[i]; rng=np.random.default_rng(3+i); row=[]
    for j,m in enumerate(ms):
        Z[i,j]=threshold_T(m,e,60,rng); row.append(f"{Z[i,j]:.0f}" if Z[i,j]>0 else "0")
    print(f"  eps={e:.3f}: "+" ".join(f"{v:>9s}" for v in row))
    P={str(k):Z[k].tolist() for k in range(len(epss)) if not np.isnan(Z[k]).any()}
    json.dump(P,open('fig3_partial.json','w'))
if np.isnan(Z).any(): print("partial; rerun to continue"); sys.exit(0)
json.dump({'ms':ms,'epss':epss,'Z':Z.tolist(),'eta':1/1024,'noise':'bernoulli','algorithm':'conditional-mean',
           'eps_star':3/32-1/1024}, open('fig3_data.json','w'))
print("theoretical vanishing threshold eps* = 3/32 - eta =", 3/32-1/1024)
