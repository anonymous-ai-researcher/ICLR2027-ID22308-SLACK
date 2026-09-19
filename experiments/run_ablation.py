"""Hyperparameter ablation for Alg.3 (epoch cutter): margin tau and accuracy eps0 relative to eps,
   plus delta-scaling of the sample count.  Random monotone instances, uniform bounded noise."""
import numpy as np, random, json
exec(open('cutter_ls.py').read().split("def local_search")[0])   # make_coverage, make_monotone

def cutter(f,m,eps,e0,tau,rng,reps,sd):
    cache={}
    def hv(S):
        S=frozenset(S)
        if S not in cache: cache[S]=float(np.mean(f(S)+rng.uniform(-sd,sd,reps)))
        return cache[S]
    A=set(range(m)); B=set(); epochs=0
    while True:
        epochs+=1; restart=False
        for X,Y in ((A,B),(B,A)):
            moved=False
            for g in sorted(X):
                if g not in X: continue
                hY=hv(Y); hXg=hv(X-{g})
                if hXg>hY+tau:
                    st=hv(Y|{g})>=hXg-2*e0; X.remove(g); Y.add(g); moved=True
                    if st: restart=True; break
            if restart: break
            if moved: break
        if restart:
            if epochs>500: break
            continue
        break
    ok=all(f(B)>=f(A-{g})-eps for g in A) and all(f(A)>=f(B-{g})-eps for g in B)
    return ok,len(cache),epochs

m,eps,sd,seeds=20,0.1,0.25,150
out={}
print("=== (i) margin tau, with eps0 = eps/8 fixed (proof: tau = 6 eps0 = 0.75 eps) ===")
rows=[]
for tau_f in (0.25,0.5,0.75,1.0,1.25):
    tau=tau_f*eps; e0=eps/8; reps=int(np.ceil(np.log(2*200/0.05)/(2*e0**2)/50)); reps=max(20,min(reps,400))
    ok=0; cons=[]; ep=[]
    for s in range(seeds):
        rng=np.random.default_rng(100+s); f=make_coverage(m) if s%2==0 else make_monotone(m)
        random.seed(100+s); f=make_coverage(m) if s%2==0 else make_monotone(m)
        o,c,e=cutter(f,m,eps,e0,tau,rng,reps,sd); ok+=o; cons.append(c); ep.append(e)
    rows.append((tau_f,ok/seeds,float(np.median(cons)),float(np.median(ep))))
    print(f"  tau={tau_f:.2f}eps: eps-EFX rate={ok/seeds:.3f}  consulted={np.median(cons):.0f}  epochs={np.median(ep):.0f}")
out['tau']=rows
print("=== (ii) accuracy eps0, with tau = 6 eps0 (proof relation kept) ===")
rows=[]
for e0_f in (1/32,1/16,1/8,1/4,1/2):
    e0=e0_f*eps; tau=6*e0; reps=int(np.ceil(np.log(2*200/0.05)/(2*e0**2)/50)); reps=max(20,min(reps,2000))
    ok=0; cons=[]
    for s in range(seeds):
        rng=np.random.default_rng(200+s); random.seed(200+s); f=make_coverage(m) if s%2==0 else make_monotone(m)
        o,c,e=cutter(f,m,eps,e0,tau,rng,reps,sd); ok+=o; cons.append(c)
    rows.append((e0_f,ok/seeds,float(np.median(cons)),reps))
    print(f"  eps0={e0_f:.4f}eps (tau={6*e0_f:.3f}eps): rate={ok/seeds:.3f}  consulted={np.median(cons):.0f}  samples/bundle={reps}")
out['eps0']=rows
print("=== (iii) delta scaling: samples per bundle to hit failure <= delta over N=100 bundles ===")
rows=[]
for delta in (1e-1,1e-2,1e-3,1e-4):
    e0=eps/8; T0=int(np.ceil(32*np.log(2*100/delta)/eps**2))
    rows.append((delta,T0)); print(f"  delta={delta:.0e}: T0 = ceil(32 eps^-2 ln(2N/delta)) = {T0}   ratio to delta=0.1: {T0/rows[0][1]:.2f}")
out['delta']=rows
json.dump(out,open('ablation.json','w')); print("saved ablation.json")
