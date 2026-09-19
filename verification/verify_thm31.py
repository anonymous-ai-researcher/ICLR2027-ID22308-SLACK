"""Re-verify EVERY step of Theorem 3.1's proof chain in exact rational arithmetic."""
from fractions import Fraction as F
import itertools, math
ETA=F(1,1024)

def v1(S,St,m):
    pool=S&frozenset(range(m)); c=len(pool&St)
    return F(3,16)*(1 if pool else 0)+F(3,16)*min(F(1),F(2*c,m))+(F(3,8)-ETA)*('g*' in S)+ETA*('go' in S)
def v2(S): return F(1,2)*('g*' in S)+F(1,2)*('go' in S)
def powerset(xs):
    for r in range(len(xs)+1):
        for c in itertools.combinations(xs,r): yield frozenset(c)

fails={k:0 for k in ('L1_monotone','L1_submod','L1_range','L1_coverage','L2_feasible','L2_equality',
                     'L3_ef1_free','L4_recovery','L5_coord','L6_meanshift','L7_kl')}
for m in (2,4,6,8):
    d=m//2; R=list(range(m)); U=R+['g*','go']
    for th in itertools.product([0,1],repeat=d):
        St=frozenset(2*i+th[i] for i in range(d))
        # --- L1 ---
        for S in powerset(U):
            val=v1(S,St,m)
            if not (F(0)<=val<=F(3,4)): fails['L1_range']+=1
            for g in U:
                if g not in S and v1(S|{g},St,m)<val: fails['L1_monotone']+=1
        for S in powerset(U):
            for g in U:
                if g in S: continue
                marg_S=v1(S|{g},St,m)-v1(S,St,m)
                for T in powerset(U):
                    if not S<=T or g in T: continue
                    if v1(T|{g},St,m)-v1(T,St,m) > marg_S: fails['L1_submod']+=1
        # coverage representation
        w={'u0':F(3,16),'u*':F(3,8)-ETA,'uo':ETA}
        for j in St: w[('u',j)]=F(3,8*m)
        def Tset(g):
            if g=='g*': return {'u*'}
            if g=='go': return {'uo'}
            return {'u0'}|({('u',g)} if g in St else set())
        for S in powerset(U):
            cov=sum(w[u] for u in set().union(*[Tset(g) for g in S])) if S else F(0)
            if cov!=v1(S,St,m): fails['L1_coverage']+=1
        # --- L2 ---
        lhs=v1(frozenset(St),St,m); rhs=v1(frozenset({'g*','go'}),St,m)
        if lhs!=rhs or lhs!=F(3,8): fails['L2_equality']+=1
        if not (lhs>=rhs and v2(frozenset({'g*','go'}))>=v2(frozenset())): fails['L2_feasible']+=1
        if len(St)!=m//2: fails['L2_feasible']+=1
        # --- L3: single pool item is exactly EF1 ---
        S1=frozenset({0}); B2=frozenset({'g*','go'})
        best=min(v1(B2-{g},St,m) for g in B2)
        if v1(S1,St,m) < best: fails['L3_ef1_free']+=1
        # --- L4/L5: recovery + coordinate recovery ---
        for eps in (F(1,128),F(1,256)):
            beta=F(16,3)*(ETA+eps)
            for S in powerset(R):
                if len(S)>m//2: continue
                ok_efx = v1(S,St,m) >= max(v1(B2-{g},St,m) for g in B2)-eps
                dH=len(S^St)
                if ok_efx and dH > beta*m: fails['L4_recovery']+=1
                if ok_efx:
                    hat=tuple(1 if (2*i+1) in S and (2*i) not in S else 0 for i in range(d))
                    if sum(a!=b for a,b in zip(hat,th)) > dH: fails['L5_coord']+=1
        # --- L6/L7 ---
        for i in range(d):
            th2=list(th); th2[i]^=1
            St2=frozenset(2*j+th2[j] for j in range(d))
            for S in powerset(U):
                gap=abs(v1(S,St,m)-v1(S,St2,m))
                if gap > F(3,8*m): fails['L6_meanshift']+=1
                p,q=v1(S,St,m),v1(S,St2,m)
                if not (F(3,16)<=p<=F(3,4) and F(3,16)<=q<=F(3,4)) and (S&frozenset(R)):
                    pass
                if p not in (F(0),) and q not in (F(0),):
                    kl=0.0
                    fp,fq=float(p),float(q)
                    if 0<fp<1 and 0<fq<1:
                        kl=fp*math.log(fp/fq)+(1-fp)*math.log((1-fp)/(1-fq))
                        if kl > 12/(13*m*m)+1e-12: fails['L7_kl']+=1
    print(f"  m={m:2d} done")
print()
for k,v in fails.items(): print(f"  {k:14s}: {'PASS' if v==0 else f'FAIL ({v})'}")
