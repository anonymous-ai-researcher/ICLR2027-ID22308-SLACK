"""Real-preference experiments.  Rankings -> Borda scores in [0,1] -> monotone valuations.
   AGH (146 students x 9 courses, PrefLib 00009): n-agent EF1 via margin ECE (Thm 4.2), and the
   frozen-vs-unfrozen EF1/EFX comparison on real preferences.
   Cleanweb (4-5 rankers x 240 items, PrefLib 00015): two-agent EFX via the epoch cutter (Thm 4.3), m-scaling."""
import numpy as np, json, random, re, itertools

def load_soc(path):
    alts=None; orders=[]
    for line in open(path):
        if line.startswith('#'):
            if 'NUMBER ALTERNATIVES' in line: alts=int(line.split(':')[1])
            continue
        if ':' not in line: continue
        cnt,rest=line.split(':',1); cnt=int(cnt)
        order=[int(x)-1 for x in re.findall(r'\d+',rest)]
        if len(order)==alts: orders += [order]*cnt
    return alts, orders

def borda(order, m):
    w=np.zeros(m)
    for r,item in enumerate(order): w[item]=(m-r)/m          # top item -> 1, bottom -> 1/m
    return w/ w.sum() if w.sum()>0 else w                     # normalised additive weights, sum 1

def make_val(w, kind):
    if kind=='additive':       return lambda S: float(sum(w[i] for i in S))
    if kind=='budget':         B=0.5; return lambda S: float(min(sum(w[i] for i in S),B))/B
    if kind=='unit':           M=w.max(); return lambda S: (max((w[i] for i in S),default=0.0))/M
    raise ValueError(kind)

def check_ef1(vals,B,eps):
    A=list(B.keys())
    for a in A:
        for b in A:
            if a==b or not B[b]: continue
            if not any(vals[a](B[a])>=vals[a](B[b]-{g})-eps for g in B[b]): return False
    return True
def check_efx(vals,B,eps):
    A=list(B.keys())
    for a in A:
        for b in A:
            if a==b or not B[b]: continue
            if not all(vals[a](B[a])>=vals[a](B[b]-{g})-eps for g in B[b]): return False
    return True
def check_ef(vals,B,eps):
    A=list(B.keys())
    return all(vals[a](B[a])>=vals[a](B[b])-eps for a in A for b in A if a!=b)

# ---------------- margin ECE (Alg.2) with noisy estimates ----------------
def margin_ece(vals, items, eps, rng, reps, noise_sd):
    e0=eps/8; tau=3*e0; cache={}; agents=list(vals.keys())
    def hv(a,S):
        k=(a,frozenset(S))
        if k not in cache:
            t=vals[a](frozenset(S)); cache[k]=float(np.mean(t+rng.uniform(-noise_sd,noise_sd,reps)))
        return cache[k]
    B={a:frozenset() for a in agents}
    for g in items:
        # eliminate estimated envy cycles
        while True:
            edges={a:[b for b in agents if b!=a and hv(a,B[b])-hv(a,B[a])>tau] for a in agents}
            # find a cycle by DFS
            cyc=None; color={a:0 for a in agents}
            def dfs(u,path):
                nonlocal cyc
                color[u]=1; path.append(u)
                for v in edges[u]:
                    if cyc: return
                    if color[v]==1: cyc=path[path.index(v):]+[]; return
                    if color[v]==0: dfs(v,path)
                path.pop(); color[u]=2
            for a in agents:
                if color[a]==0 and not cyc: dfs(a,[])
            if not cyc: break
            old={a:B[a] for a in cyc}
            for i,a in enumerate(cyc): B[a]=old[cyc[(i+1)%len(cyc)]]
        src=[a for a in agents if not any(a in edges[b] for b in agents)]
        a=src[0]; B[a]=B[a]|{g}
    return B, len(cache)

# ---------------- epoch cutter (Alg.3) with noisy estimates, two agents ----------------
def epoch_cutter(v1,v2,items,eps,rng,reps,noise_sd):
    e0=eps/8; tau=6*e0; c1={}; c2={}
    def hv(cache,f,S):
        S=frozenset(S)
        if S not in cache: cache[S]=float(np.mean(f(S)+rng.uniform(-noise_sd,noise_sd,reps)))
        return cache[S]
    A=set(items); B=set()
    while True:
        restart=False
        for X,Y in ((A,B),(B,A)):
            moved=False
            for g in sorted(X):
                if g not in X: continue
                hY=hv(c1,v1,Y); hXg=hv(c1,v1,X-{g})
                if hXg>hY+tau:
                    st=hv(c1,v1,Y|{g})>=hXg-2*e0; X.remove(g); Y.add(g); moved=True
                    if st: restart=True; break
            if restart: break
            if moved: break
        if restart: continue
        break
    if hv(c2,v2,A)>=hv(c2,v2,B): B2,B1=frozenset(A),frozenset(B)
    else: B2,B1=frozenset(B),frozenset(A)
    return {0:B1,1:B2}, len(c1)+len(c2)

if __name__=='__main__' and False:
    rng=np.random.default_rng(0); pr=random.Random(0)
    m,orders=load_soc('data/agh2003.soc'); W=[borda(o,m) for o in orders]
    print(f"AGH 2003: {len(W)} students, {m} courses")
    eps=0.1; reps=200; sd=0.25
    out={'agh':{}, 'cleanweb':{}}
    # ---- E2: n-agent EF1 on real preferences, all three inductions ----
    for kind in ('additive','budget','unit'):
        res=[]
        for n in (2,3,4,5,6):
            ok=0; cons=[]
            for t in range(200):
                ids=pr.sample(range(len(W)),n); vals={i:make_val(W[i],kind) for i in ids}
                B,N=margin_ece(vals,list(range(m)),eps,rng,reps,sd)
                ok+=check_ef1(vals,B,eps); cons.append(N)
            res.append((n,ok/200,float(np.median(cons)),n*(m+1)))
            print(f"  EF1 {kind:8s} n={n}: success={ok/200:.3f}  consulted median={np.median(cons):.0f}  bound n(m+1)={n*(m+1)}")
        out['agh']['ef1_'+kind]=res
    # ---- E1: frozen vs unfrozen, pairs of students, additive Borda ----
    for setting in ('frozen','unfrozen'):
        rates={}
        for T in (0,50,200,800,3200,12800):
            c=np.zeros(3)
            for t in range(300):
                i,j=pr.sample(range(len(W)),2); v={0:make_val(W[i],'additive'),1:make_val(W[j],'additive')}
                if setting=='frozen':
                    top0=int(np.argmax(W[i])); top1=int(np.argmax(W[j]))
                    if top0==top1: top1=int(np.argsort(W[j])[-2])
                    sigma={0:frozenset({top0}),1:frozenset({top1})}; pool=[g for g in range(m) if g not in (top0,top1)]
                else:
                    sigma={0:frozenset(),1:frozenset()}; pool=list(range(m))
                # generic budget-T algorithm: estimate every bundle value with T/|bundles| samples, search for best eps-EF ext
                cache={}
                bundles=[frozenset(S) for r in range(len(pool)+1) for S in itertools.combinations(pool,r)]
                per=max(1,T//(2*len(bundles))) if T>0 else 0
                def est(a,S):
                    k=(a,S)
                    if k not in cache: cache[k]= v[a](S) if per==0 else float(np.mean(v[a](S)+rng.uniform(-sd,sd,per)))
                    return cache[k]
                best=None; bestgap=-9
                for S0 in bundles:
                    S1=frozenset(pool)-S0
                    B={0:sigma[0]|S0,1:sigma[1]|S1}
                    if per==0 and T==0:
                        # zero observations: the natural information-free rule splits the pool in half
                        h=len(pool)//2; B={0:sigma[0]|frozenset(pool[:h]),1:sigma[1]|frozenset(pool[h:])}; best=B; break
                    gap=min(est(0,B[0])-est(0,B[1]), est(1,B[1])-est(1,B[0]))
                    if gap>bestgap: bestgap=gap; best=B
                c+=[check_ef1(v,best,eps),check_efx(v,best,eps),check_ef(v,best,eps)]
            rates[T]=(c/300).tolist(); print(f"  {setting:8s} T={T:5d}: EF1={rates[T][0]:.3f} EFX={rates[T][1]:.3f} EF={rates[T][2]:.3f}")
        out['agh'][setting]=rates
    # ---- E3: cleanweb two-agent EFX, m-scaling ----
    m2,orders2=load_soc('data/cleanweb1.soc'); print(f"cleanweb capitals: {len(orders2)} rankers, {m2} items")
    res=[]
    for mm in (16,32,64,128,240):
        ok=0; cons=[]
        for (i,j) in itertools.combinations(range(len(orders2)),2):
            for rep in range(6):
                items=pr.sample(range(m2),mm)
                sub=lambda o: [x for x in o if x in set(items)]
                idx={it:k for k,it in enumerate(items)}
                w1=borda([idx[x] for x in sub(orders2[i])],mm); w2=borda([idx[x] for x in sub(orders2[j])],mm)
                v1=make_val(w1,'budget'); v2=make_val(w2,'budget')
                B,N=epoch_cutter(v1,v2,list(range(mm)),eps,rng,reps,sd)
                ok+=check_efx({0:v1,1:v2},B,eps); cons.append(N)
            pass
        tot=len(list(itertools.combinations(range(len(orders2)),2)))*6
        res.append((mm,ok/tot,float(np.median(cons)))); print(f"  EFX cleanweb m={mm:3d}: success={ok/tot:.3f} consulted median={np.median(cons):.0f} ({np.median(cons)/mm:.2f}m)")
    out['cleanweb']['efx']=res
    json.dump(out,open('realdata.json','w')); print("saved realdata.json")

if __name__=='__main__':
    rng=np.random.default_rng(0); pr=random.Random(0)
    m,orders=load_soc('data/agh2003.soc'); W=[borda(o,m) for o in orders]
    eps=0.1; sd=0.25
    out=json.load(open('realdata.json'))
    for setting in ('frozen','unfrozen'):
        rates={}
        for T in (0,50,200,800,3200,12800):
            c=np.zeros(3)
            for t in range(300):
                i,j=pr.sample(range(len(W)),2); v={0:make_val(W[i],'additive'),1:make_val(W[j],'additive')}
                if setting=='frozen':
                    top0=int(np.argmax(W[i])); top1=int(np.argmax(W[j]))
                    if top0==top1: top1=int(np.argsort(W[j])[-2])
                    sigma={0:frozenset({top0}),1:frozenset({top1})}; pool=[g for g in range(m) if g not in (top0,top1)]
                else:
                    sigma={0:frozenset(),1:frozenset()}; pool=list(range(m))
                cache={}
                bundles=[frozenset(S) for r in range(len(pool)+1) for S in itertools.combinations(pool,r)]
                per=max(1,T//(2*len(bundles))) if T>0 else 0
                def est(a,S):
                    k=(a,S)
                    if k not in cache: cache[k]= v[a](S) if per==0 else float(np.mean(v[a](S)+rng.uniform(-sd,sd,per)))
                    return cache[k]
                best=None; bestgap=-9
                if T==0:
                    h=len(pool)//2; best={0:sigma[0]|frozenset(pool[:h]),1:sigma[1]|frozenset(pool[h:])}
                else:
                    for S0 in bundles:
                        S1=frozenset(pool)-S0; B={0:sigma[0]|S0,1:sigma[1]|S1}
                        gap=min(est(0,B[0])-est(0,B[1]), est(1,B[1])-est(1,B[0]))
                        if gap>bestgap: bestgap=gap; best=B
                c+=[check_ef1(v,best,eps),check_efx(v,best,eps),check_ef(v,best,eps)]
            rates[str(T)]=(c/300).tolist(); print(f"  {setting:8s} T={T:5d}: EF1={rates[str(T)][0]:.3f} EFX={rates[str(T)][1]:.3f} EF={rates[str(T)][2]:.3f}")
        out['agh'][setting]=rates
    json.dump(out,open('realdata.json','w')); print("saved")
