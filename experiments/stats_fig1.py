"""Paired McNemar tests on the Fig.1 data: same instance, same observations, two notions.
   Plus Wilson CIs and Holm-Bonferroni correction."""
import numpy as np, json, sys, os, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from core import *
from math import comb

def sweep_paired(m, T_list, eps, n_seed, frozen, sigma=0.25, seed0=7):
    d=m//2; lo=3/16; hi=3/16+(3/16)*(2/m); gap=hi-lo
    rng=np.random.default_rng(seed0+int(frozen))
    tab={T: np.zeros((2,2),int) for T in T_list}   # rows: EF1 (0/1), cols: EFX (0/1)
    rate={T: np.zeros(3) for T in T_list}
    for s in range(n_seed):
        theta,S_theta=make_instance(m,rng)
        for T in T_list:
            if T<=0:
                S=np.zeros(m,bool); S[0]=True
            else:
                Smat=rng.random((int(T),m))<0.5
                c=(Smat & S_theta).sum(axis=1); v=3/16*Smat.any(axis=1)+(3/16)*np.minimum(1.0,2*c/m)
                y=(rng.random(int(T))<v).astype(float)
                even=Smat[:,0::2]; odd=Smat[:,1::2]; plus=odd&~even; minus=even&~odd
                cp=plus.sum(axis=0); cm=minus.sum(axis=0)
                yp=np.where(cp>0,(y[:,None]*plus).sum(axis=0)/np.maximum(cp,1),0.5)
                ym=np.where(cm>0,(y[:,None]*minus).sum(axis=0)/np.maximum(cm,1),0.5)
                S=np.zeros(m,bool); S[2*np.arange(d)+(yp>ym).astype(int)]=True
            r=check_frozen(S,S_theta,m,eps) if frozen else check_unfrozen(True,S,S_theta,m,eps)
            tab[T][int(r[0]),int(r[1])]+=1; rate[T]+=r
    return tab,{T:v/n_seed for T,v in rate.items()}

from scipy.stats import binomtest
def mcnemar_exact(b,c):
    b,c=int(b),int(c)                      # numpy ints overflow under **
    if b+c==0: return 1.0
    return float(binomtest(min(b,c), b+c, 0.5, alternative='two-sided').pvalue)

def wilson(p,n,z=1.96):
    d=1+z*z/n; c=(p+z*z/(2*n))/d
    h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0,c-h),min(1,c+h)

m,eps,n=32,0.0078125,300
Ts=[0,769,8577,36467,95709]   # actual grid points of Fig.1
tabF,rF=sweep_paired(m,Ts,eps,n,True)
tabU,rU=sweep_paired(m,Ts,eps,n,False)

rows=[]
print(f"{'setting':9s} {'T':>7s} {'EF1':>7s} {'EFX':>7s} {'diff':>7s} {'95% CI of diff':>20s} {'b':>5s} {'c':>5s} {'p (exact)':>11s}")
for tag,tab,rt in (('frozen',tabF,rF),('unfrozen',tabU,rU)):
    for T in Ts:
        t=tab[T]; b=t[1,0]; c=t[0,1]          # EF1 yes/EFX no ; EF1 no/EFX yes
        p1,p2=rt[T][0],rt[T][1]; diff=p1-p2
        se=np.sqrt(max(b+c,1))/n; ci=(max(-1,diff-1.96*se), min(1,diff+1.96*se))
        pv=mcnemar_exact(b,c); rows.append((tag,T,pv))
        print(f"{tag:9s} {T:7d} {p1:7.3f} {p2:7.3f} {diff:7.3f}  [{ci[0]:6.3f},{ci[1]:6.3f}] {b:5d} {c:5d} {pv:11.3g}")
# Holm-Bonferroni
order=sorted(range(len(rows)),key=lambda i:rows[i][2]); M=len(rows)
adj={}
prev=0
for rank,i in enumerate(order):
    a=min(1.0,max(prev,(M-rank)*rows[i][2])); adj[i]=a; prev=a
print("\nHolm-Bonferroni adjusted p-values:")
for i,(tag,T,pv) in enumerate(rows):
    print(f"  {tag:9s} T={T:7d}: raw={pv:.3g}  adj={adj[i]:.3g}  {'significant' if adj[i]<0.05 else 'n.s.'}")
json.dump({'Ts':Ts,
           'frozen':{str(T):tabF[T].tolist() for T in Ts},
           'unfrozen':{str(T):tabU[T].tolist() for T in Ts},
           'rateF':{str(T):list(rF[T]) for T in Ts},
           'rateU':{str(T):list(rU[T]) for T in Ts},
           'raw':{str(i):rows[i][2] for i in range(len(rows))},
           'rowkey':[(t,T) for t,T,_ in rows],
           'adj':{str(i):adj[i] for i in adj}}, open('stats_fig1.json','w'))
