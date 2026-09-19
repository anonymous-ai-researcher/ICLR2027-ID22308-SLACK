"""Generate the LaTeX tables for Appendix D from the stored experiment data."""
import json, numpy as np
from scipy.stats import binomtest

def wilson(p,n,z=1.96):
    d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d
    return max(0,c-h),min(1,c+h)

out=[]
# ---------- Table D.1 : Fig.1 success rates + paired tests ----------
D=json.load(open('fig1_data.json')); T=D['T_list']; n=D['n_seed']
S1=json.load(open('stats_fig1.json')); Ts=S1['Ts']
rows=[]
for tag in ('frozen','unfrozen'):
    R=np.array(D['res'][tag])
    for Tv in Ts:
        i=int(np.argmin([abs(t-Tv) for t in T])); ef1,efx,ef=R[i]
        b,c=S1[tag][str(Tv)][1][0], S1[tag][str(Tv)][0][1]
        p=float(binomtest(min(int(b),int(c)),int(b)+int(c),0.5).pvalue) if b+c>0 else 1.0
        rows.append((tag,T[i],ef1,efx,ef,int(b),int(c),p))
# Holm
ps=sorted(range(len(rows)),key=lambda i:rows[i][7]); M=len(rows); adj={}; prev=0
for rk,i in enumerate(ps):
    a=min(1.0,max(prev,(M-rk)*rows[i][7])); adj[i]=a; prev=a
L=[r"\begin{tabular}{llrrrrrrr}", r"\toprule",
   r"setting & $T$ & $\varepsilon$-EF1 & $\varepsilon$-EFX & $\varepsilon$-EF & $b$ & $c$ & raw $p$ & Holm $p$ \\", r"\midrule"]
for i,(tag,Tv,a,bb,cc,b,c,p) in enumerate(rows):
    fmt=lambda x: f"{x:.3f}"
    def sci(x):
        if x==0: return r"$<10^{-300}$"
        if x>=1e-3: return f"${x:.3f}$"
        mant,ex = f"{x:.1e}".split('e')
        return rf"${mant}\times 10^{{{int(ex)}}}$"
    pv, av = sci(p), sci(adj[i])
    if i==5: L.append(r"\midrule")
    L.append(f"{tag} & ${Tv}$ & {fmt(a)} & {fmt(bb)} & {fmt(cc)} & ${b}$ & ${c}$ & {pv} & {av} \\\\")
L+= [r"\bottomrule", r"\end{tabular}"]
out.append(("tabD1","\n".join(L)))

# ---------- Table D.2 : Fig.2 consultation counts ----------
D2=json.load(open('fig2_data.json')); ms=D2['ms']
L=[r"\begin{tabular}{rrrrrr}", r"\toprule",
   r"& \multicolumn{2}{c}{adversarial instance} & \multicolumn{3}{c}{random instances (40 seeds)} \\",
   r"\cmidrule(lr){2-3}\cmidrule(lr){4-6}",
   r"$m$ & epoch & re-exam. & epoch median & re-exam. median & epoch $95\%$ CI \\", r"\midrule"]
for j,m_ in enumerate(ms):
    L.append(f"${m_}$ & ${D2['anchor']['epoch'][j]}$ & ${D2['anchor']['rescan'][j]}$ & "
             f"${D2['random']['epoch']['med'][j]:.0f}$ & ${D2['random']['rescan']['med'][j]:.0f}$ & "
             f"$[{D2['random']['epoch']['lo'][j]:.0f}, {D2['random']['epoch']['hi'][j]:.0f}]$ \\\\")
L+=[r"\bottomrule", r"\end{tabular}"]
out.append(("tabD2","\n".join(L)))

# ---------- Table D.3 : Fig.4 robustness with Wilson CIs ----------
D4=json.load(open('fig4_data.json')); S=np.array(D4['S']); ns=D4['n_seed']
cls=[c.replace('rand. monotone','rand.\\ mon.').replace('budget-add.','budget-add.') for c in D4['classes']]
L=[r"\begin{tabular}{l"+"c"*len(cls)+"}", r"\toprule",
   "noise model & "+" & ".join(cls)+r" \\", r"\midrule"]
for i,nm in enumerate(D4['noise']):
    cells=[]
    for j in range(S.shape[1]):
        lo,hi=wilson(S[i,j],ns)
        cells.append(f"${S[i,j]:.3f}$"+r"\,\tiny$[{:.2f},{:.2f}]$".format(lo,hi))
    tag = nm if D4['inth'][i] else nm+r"$^{\dagger}$"
    L.append(tag+" & "+" & ".join(cells)+r" \\")
L+=[r"\bottomrule", r"\end{tabular}"]
out.append(("tabD3","\n".join(L)))

for name,tex in out:
    open(f'{name}.tex','w').write(tex); print(f"wrote {name}.tex ({len(tex.splitlines())} lines)")
