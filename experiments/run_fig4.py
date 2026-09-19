"""Fig.4: does Thm 4.3's guarantee survive outside its assumptions?
   noise models x valuation classes ; same per-bundle sample budget everywhere."""
import numpy as np, json, random

# ---------- valuation classes (all monotone, normalised to [0,1]) ----------
def f_coverage(m,rng,U=14):
    w=np.array([rng.random() for _ in range(U)]); w/=w.sum()
    T=[frozenset(u for u in range(U) if rng.random()<0.35) for _ in range(m)]
    return lambda S: float(sum(w[u] for u in set().union(*[T[i] for i in S]))) if S else 0.0
def f_matroid_rank(m,rng,parts=5):
    lab=[rng.randrange(parts) for _ in range(m)]; cap=[rng.randint(1,3) for _ in range(parts)]
    tot=sum(cap)
    return lambda S: sum(min(cap[p],sum(1 for i in S if lab[i]==p)) for p in range(parts))/tot
def f_budget_additive(m,rng):
    w=np.array([rng.random() for _ in range(m)]); B=0.45*w.sum()
    return lambda S: float(min(sum(w[i] for i in S),B))/B
def f_unit_demand(m,rng):
    w=[rng.random() for _ in range(m)]; M=max(w)
    return lambda S: (max((w[i] for i in S),default=0.0))/M
def f_xos(m,rng,k=4):                      # XOS, generally NOT submodular
    A=[np.array([rng.random() for _ in range(m)]) for _ in range(k)]
    sc=max(a.sum() for a in A)
    return lambda S: float(max(sum(a[i] for i in S) for a in A))/sc if S else 0.0
def f_random_monotone(m,rng):
    keys=[frozenset(rng.sample(range(m),rng.randint(1,max(1,m//3)))) for _ in range(6)]
    val=[rng.random() for _ in keys]
    return lambda S: (max([v for k_,v in zip(keys,val) if k_<=set(S)],default=0)+0.5*len(S)/m)/1.5

CLASSES=[('coverage',f_coverage),('matroid rank',f_matroid_rank),('budget-add.',f_budget_additive),
         ('unit-demand',f_unit_demand),('XOS',f_xos),('rand. monotone',f_random_monotone)]

# ---------- noise models ----------
def n_uniform(v,rng,s):  return v+rng.uniform(-s,s)                 # in theory: bounded
def n_bernoulli(v,rng,s):return float(rng.random()<min(1,max(0,v))) # in theory: bounded
def n_truncgauss(v,rng,s):
    x=v+rng.normal(0,s); return min(1.0,max(0.0,x))                 # in theory: bounded
def n_gauss(v,rng,s):    return v+rng.normal(0,s)                   # VIOLATES boundedness
def n_t3(v,rng,s):       return v+s*rng.standard_t(3)               # VIOLATES sub-Gaussian
NOISE=[('uniform',n_uniform,True),('Bernoulli',n_bernoulli,True),('trunc. Gauss',n_truncgauss,True),
       ('Gaussian',n_gauss,False),(r'$t_3$ heavy tail',n_t3,False)]

def epoch_cutter(f,m,eps,nz,rng,reps,s):
    e0=eps/8; tau=6*e0; cache={}; consult=0
    def hv(S):
        nonlocal consult
        S=frozenset(S)
        if S not in cache:
            consult+=1; t=f(S); cache[S]=float(np.mean([nz(t,rng,s) for _ in range(reps)]))
        return cache[S]
    A=set(range(m)); B=set()
    while True:
        restart=False
        for X,Y in ((A,B),(B,A)):
            moved=False
            for g in sorted(X):
                if g not in X: continue
                hY=hv(Y); hXg=hv(X-{g})
                if hXg>hY+tau:
                    st=hv(Y|{g})>=hXg-2*e0
                    X.remove(g); Y.add(g); moved=True
                    if st: restart=True; break
            if restart: break
            if moved: break
        if restart: continue
        return A,B,consult

def true_efx(f,A,B,eps):
    return all(f(B)>=f(A-{g})-eps for g in A) and all(f(A)>=f(B-{g})-eps for g in B)

m,eps,sigma,n_seed=24,0.10,0.25,300
reps=int(np.ceil(2*np.log(2*200/0.05)/( (eps/8)**2 )/100))  # modest, identical for every cell
reps=max(30,min(reps,400))
print(f"m={m} eps={eps} sigma={sigma} reps/bundle={reps} seeds={n_seed}")
S=np.zeros((len(NOISE),len(CLASSES))); Cn=np.zeros_like(S)
for i,(nn,nz,inth) in enumerate(NOISE):
    row=[]
    for j,(cn,mk) in enumerate(CLASSES):
        ok=0; cons=[]
        for s_ in range(n_seed):
            pr=random.Random(7919*i+131*j+s_); npr=np.random.default_rng(7919*i+131*j+s_)
            f=mk(m,pr)
            A,B,c=epoch_cutter(f,m,eps,nz,npr,reps,sigma)
            ok+=true_efx(f,A,B,eps); cons.append(c)
        S[i,j]=ok/n_seed; Cn[i,j]=np.median(cons); row.append(f"{S[i,j]:.3f}")
    print(f"  {nn:18s} "+" ".join(f"{v:>6s}" for v in row))
json.dump({'S':S.tolist(),'C':Cn.tolist(),'noise':[n[0] for n in NOISE],
           'inth':[n[2] for n in NOISE],'classes':[c[0] for c in CLASSES],
           'm':m,'eps':eps,'reps':reps,'n_seed':n_seed},open('fig4_data.json','w'))
print("saved fig4_data.json")
