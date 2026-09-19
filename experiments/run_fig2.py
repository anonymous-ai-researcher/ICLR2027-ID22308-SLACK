"""Fig.2: consultation count of the epoch cutter (Alg.3) vs the re-examination variant.
   (a) the adversarial anchor instance of Prop. D.1   (b) random monotone/coverage instances."""
import numpy as np, json, random

def anchor_f(m, eps):
    e0=eps/8; tau=6*e0; A={0,1}
    return lambda S: (tau+e0)*(A<=set(S)), A

def rand_coverage(m, rng, U=12):
    w=[rng.random() for _ in range(U)]
    sets=[frozenset(u for u in range(U) if rng.random()<0.35) for _ in range(m)]
    tot=sum(w)
    return lambda S: (sum(w[u] for u in set().union(*[sets[i] for i in S]))/tot if S else 0.0)

def rand_monotone(m, rng):
    keys=[frozenset(rng.sample(range(m), rng.randint(1,max(1,m//3)))) for _ in range(6)]
    vals=[rng.random() for _ in keys]
    return lambda S: (max([v for k,v in zip(keys,vals) if k<=set(S)],default=0)+0.5*len(S)/m)/1.5

def run(f, m, eps, mode, adversary=None):
    """mode='epoch' (Alg.3) or 'rescan' (re-examine all of X after every move)."""
    e0=eps/8; tau=6*e0; cache={}
    def hv(S, g=None, X=None):
        S=frozenset(S)
        if S in cache: return cache[S]
        t=f(S); v = adversary(S,t,g,X,e0,cache) if adversary else t
        cache[S]=v; return v
    A=set(range(m)); B=set(); moves=0; epochs=0
    while True:
        epochs+=1; restart=False
        for X,Y in ((A,B),(B,A)):
            moved=False
            if mode=='epoch':
                for g in sorted(X):
                    if g not in X: continue
                    hY=hv(Y); hXg=hv(X-{g},g,frozenset(X))
                    if hXg > hY+tau:
                        st = hv(Y|{g}) >= hXg-2*e0
                        X.remove(g); Y.add(g); moves+=1; moved=True
                        if st: restart=True; break
            else:
                progressed=True
                while progressed:
                    progressed=False
                    for g in sorted(X):
                        hY=hv(Y); hXg=hv(X-{g},g,frozenset(X))
                        if hXg > hY+tau:
                            hv(Y|{g}); X.remove(g); Y.add(g); moves+=1; moved=True; progressed=True; break
            if restart: break
            if moved: break
        if restart: continue
        return len(cache), moves, epochs, A, B

def adv_anchor(S,t,g,X,e0,cache):
    """Promote only the last fresh mover of the current X; hide the rest (all within ±e0)."""
    if g is None or g in (0,1) or X is None: return t
    fresh=[h for h in sorted(X) if h not in (0,1) and frozenset(X-{h}) not in cache]
    return t+e0 if (fresh and g==fresh[-1]) else t-e0

eps=0.1
ms=[8,16,24,32,48,64,96,128,192,256]
out={'eps':eps,'ms':ms,'anchor':{'epoch':[],'rescan':[]},
     'random':{'epoch':{'med':[],'lo':[],'hi':[]},'rescan':{'med':[],'lo':[],'hi':[]}}}
print("--- (a) adversarial anchor instance ---")
for m in ms:
    f,_=anchor_f(m,eps)
    ne,_,_,_,_ = run(f,m,eps,'epoch',adv_anchor)
    nr,_,_,_,_ = run(f,m,eps,'rescan',adv_anchor)
    out['anchor']['epoch'].append(ne); out['anchor']['rescan'].append(nr)
    print(f"  m={m:4d}: epoch={ne:7d} ({ne/m:5.2f}m)   rescan={nr:7d} ({nr/m/m:6.3f}m^2)")

print("--- (b) random instances (40 seeds, uniform noise within +-e0) ---")
for m in ms:
    E=[]; R=[]
    for s in range(40):
        rng=random.Random(1000*m+s); npr=np.random.default_rng(1000*m+s)
        f = rand_coverage(m,rng) if s%2==0 else rand_monotone(m,rng)
        e0=eps/8
        adv=lambda S,t,g,X,e0_,c: t+npr.uniform(-e0_,e0_)
        E.append(run(f,m,eps,'epoch',adv)[0]); R.append(run(f,m,eps,'rescan',adv)[0])
    for tag,arr in (('epoch',E),('rescan',R)):
        a=np.array(arr,float)
        bs=np.array([np.median(np.random.default_rng(7*i).choice(a,len(a))) for i in range(2000)])
        out['random'][tag]['med'].append(float(np.median(a)))
        out['random'][tag]['lo'].append(float(np.percentile(bs,2.5)))
        out['random'][tag]['hi'].append(float(np.percentile(bs,97.5)))
    print(f"  m={m:4d}: epoch med={np.median(E):7.0f}   rescan med={np.median(R):7.0f}")
json.dump(out,open('fig2_data.json','w')); print("saved fig2_data.json")
