#!/usr/bin/env python3
"""
Figure generation for "One Item of Slack: Separating EF1 from EFX under Noisy Observations".

Regenerates all five figures of the paper from the cached experiment outputs.

    python make_all_figures.py           # all five
    python make_all_figures.py 3 5       # only Figures 3 and 5

Paper figure -> output file -> function in this script:

    Figure 1  fig2_ablation.pdf      make_figure1_ablation()
    Figure 2  fig1_separation.pdf    make_figure2_separation()
    Figure 3  fig3_phase.pdf         make_figure3_phase()
    Figure 4  fig4_robustness.pdf    make_figure4_robustness()
    Figure 5  fig5_realdata.pdf      make_figure5_realdata()

(The file names keep the historical numbering of the experiment scripts; the
paper numbering is the one in the left column.)

Inputs are the JSON files written by the run_*.py experiment scripts and kept
alongside this file. No experiment is rerun here.
"""
import sys

# ============================================================================
# Figure 1 (fig2_ablation.pdf): consultation counts, epoch rule vs re-examination
# source: make_fig2.py
# ============================================================================

def make_figure1_ablation():
    import json, numpy as np, matplotlib
    matplotlib.use('Agg'); import matplotlib.pyplot as plt

    D=json.load(open('fig2_data.json')); ms=np.array(D['ms'],float)

    def slope_ci(x,y,B=10000,seed=0):
        x,y=np.log(np.asarray(x,float)),np.log(np.asarray(y,float))
        s=np.polyfit(x,y,1)[0]; rng=np.random.default_rng(seed); bs=[]
        for _ in range(B):
            i=rng.integers(0,len(x),len(x))
            if len(np.unique(x[i]))>1: bs.append(np.polyfit(x[i],y[i],1)[0])
        return s,np.percentile(bs,2.5),np.percentile(bs,97.5)

    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
     'mathtext.fontset':'stix','font.size':10,'axes.labelsize':11,'axes.titlesize':11,
     'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':9.5,'axes.linewidth':0.8,
     'lines.linewidth':1.6,'xtick.direction':'in','ytick.direction':'in','axes.grid':True,
     'grid.alpha':0.25,'grid.linewidth':0.5,'legend.frameon':True,'legend.framealpha':0.95,
     'legend.edgecolor':'0.7'})
    CE,CR='#1b6ca8','#c0392b'
    fig,axes=plt.subplots(1,2,figsize=(7.2,3.0))
    fig.subplots_adjust(left=0.0761, right=0.9864,bottom=0.1584, top=0.9084,wspace=0.152)

    # (a) adversarial
    ax=axes[0]
    ae=np.array(D['anchor']['epoch'],float); ar=np.array(D['anchor']['rescan'],float)
    se=slope_ci(ms,ae); sr=slope_ci(ms,ar)
    ax.plot(ms,ar,color=CR,marker='s',ms=3.6,markeredgewidth=0,label='re-examination variant')
    ax.plot(ms,ae,color=CE,marker='o',ms=3.6,markeredgewidth=0,label='epoch rule')
    ax.plot(ms,0.506*ms**2,color=CR,ls=':',lw=0.9,alpha=0.75)
    ax.plot(ms,1.01*ms,color=CE,ls=':',lw=0.9,alpha=0.75)
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel(r'number of goods $m$'); ax.set_ylabel('distinct bundles consulted')
    ax.set_title('(a) adversarial instance')
    ax.legend(loc='upper left',handletextpad=0.55,borderaxespad=0.5)

    # (b) random
    ax=axes[1]
    for tag,c,mk,lab in (('rescan',CR,'s','re-examination variant'),('epoch',CE,'o','epoch rule')):
        md=np.array(D['random'][tag]['med'],float)
        lo=np.array(D['random'][tag]['lo'],float); hi=np.array(D['random'][tag]['hi'],float)
        ax.fill_between(ms,lo,hi,color=c,alpha=0.18,linewidth=0)
        ax.plot(ms,md,color=c,marker=mk,ms=3.6,markeredgewidth=0,label=lab)
    sre=slope_ci(ms,D['random']['epoch']['med']); srr=slope_ci(ms,D['random']['rescan']['med'])
    ax.set_xscale('log'); ax.set_yscale('log')
    ax.set_xlabel(r'number of goods $m$')
    ax.set_title(r'(b) random coverage and monotone')
    ax.legend(loc='upper left',handletextpad=0.55,borderaxespad=0.5)

    fig.canvas.draw(); r=fig.canvas.get_renderer()
    def note(ax,txt,xy_data,frac_xy,color,L=28.0,horiz=False):
        ab=ax.get_window_extent(renderer=r); W,H=ab.width,ab.height
        xa,ya=ax.transAxes.inverted().transform(ax.transData.transform([xy_data]))[0]
        tx = xa + (L+4)/W if horiz else frac_xy[0]
        ty = frac_xy[1] if horiz else ya - (L+4)/H
        ax.text(tx,ty,txt,transform=ax.transAxes,ha='left' if horiz else 'center',
                va='center',fontsize=10,color=color,linespacing=1.3,zorder=6)
        ax.annotate('',xy=(xa,ya),xytext=(xa+L/W,ty) if horiz else (tx,ya-L/H),
                    xycoords='axes fraction',textcoords='axes fraction',zorder=6,
                    arrowprops=dict(arrowstyle='-|>',color=color,lw=0.75,mutation_scale=7,
                                    shrinkA=0,shrinkB=0))
    axes[0].text(0.965,0.255,'slope %.2f\n[%.2f, %.2f]'%sr,transform=axes[0].transAxes,ha='right',
                 va='center',fontsize=10,color=CR,linespacing=1.3)
    axes[0].text(0.965,0.095,'slope %.2f\n[%.2f, %.2f]'%se,transform=axes[0].transAxes,ha='right',
                 va='center',fontsize=10,color=CE,linespacing=1.3)
    axes[1].text(0.965,0.255,'slope %.2f\n[%.2f, %.2f]'%srr,transform=axes[1].transAxes,ha='right',
                 va='center',fontsize=10,color=CR,linespacing=1.3)
    axes[1].text(0.965,0.095,'slope %.2f\n[%.2f, %.2f]'%sre,transform=axes[1].transAxes,ha='right',
                 va='center',fontsize=10,color=CE,linespacing=1.3)
    fig.savefig('fig2_ablation.pdf',dpi=1200); fig.savefig('fig2_ablation.png',dpi=220)
    print("anchor  epoch slope %.3f [%.3f,%.3f] ; rescan slope %.3f [%.3f,%.3f]"%(se+sr))
    print("random  epoch slope %.3f [%.3f,%.3f] ; rescan slope %.3f [%.3f,%.3f]"%(sre+srr))


# ============================================================================
# Figure 2 (fig1_separation.pdf): the EF1/EFX separation on the hard family
# source: make_fig1.py
# ============================================================================

def make_figure2_separation():
    import json, numpy as np, matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D

    D = json.load(open('fig1_data.json'))
    T = np.array(D['T_list'], float); n = D['n_seed']; m = D['m']; eps = D['eps']

    def wilson(p, n, z=1.96):
        d = 1 + z*z/n; c = (p + z*z/(2*n))/d
        h = z*np.sqrt(p*(1-p)/n + z*z/(4*n*n))/d
        return np.clip(c-h, 0, 1), np.clip(c+h, 0, 1)

    plt.rcParams.update({
        'font.family':'serif', 'font.serif':['Times New Roman','DejaVu Serif'],
        'mathtext.fontset':'stix', 'font.size':10, 'axes.labelsize':10.5,
        'axes.titlesize':10.5, 'xtick.labelsize':10, 'ytick.labelsize':10,
        'legend.fontsize':9.5, 'axes.linewidth':0.8, 'lines.linewidth':1.6,
        'xtick.direction':'in', 'ytick.direction':'in', 'xtick.major.size':3,
        'ytick.major.size':3, 'axes.grid':True, 'grid.alpha':0.25,
        'grid.linewidth':0.5, 'legend.frameon':True, 'legend.framealpha':0.95,
        'legend.edgecolor':'0.7', 'legend.borderpad':0.45, 'legend.handlelength':1.9,
    })
    C = {'EF1':'#1b6ca8', 'EFX':'#c0392b', 'EF':'#7f8c8d'}
    MK = {'EF1':'o', 'EFX':'s', 'EF':'^'}
    LB = {'EF1':r'$\varepsilon$-EF1', 'EFX':r'$\varepsilon$-EFX', 'EF':r'$\varepsilon$-EF'}

    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.00), sharey=True)
    fig.subplots_adjust(left=0.0839, right=0.9864, bottom=0.1550, top=0.9152, wspace=0.050)
    panels = [('frozen',  r'(a) EEAG: $\sigma(a_2)=\{g^*,g^\circ\}$ fixed'),
              ('unfrozen', r'(b) Standard setting: same valuations, released')]

    for ax, (key, title) in zip(axes, panels):
        R = np.array(D['res'][key])                      # (len(T), 3)
        for j, nm in enumerate(('EF1','EFX','EF')):
            p = R[:, j]
            loC, hiC = wilson(p, n)
            ax.fill_between(T, loC, hiC, color=C[nm], alpha=0.18, linewidth=0)
            # Markers staggered across the three series so that coincident curves
            # (which genuinely coincide here) remain individually identifiable.
            style = dict(color=C[nm], label=LB[nm], markeredgewidth=0)
            if nm == 'EF':
                ax.plot(T, p, linestyle=(0, (5.0, 3.0)), linewidth=2.6, alpha=0.80,
                        marker=MK[nm], markersize=4.2, markevery=(2, 3), zorder=2, **style)
            elif nm == 'EFX':
                ax.plot(T, p, linestyle='-', linewidth=1.5, marker=MK[nm],
                        markersize=3.4, markevery=(1, 3), zorder=3, **style)
            else:
                ax.plot(T, p, linestyle='-', linewidth=1.5, marker=MK[nm],
                        markersize=3.4, markevery=(0, 3), zorder=4, **style)
        ax.set_xscale('symlog', linthresh=30, linscale=0.45)
        ax.set_xlim(-3, 3e6); ax.set_ylim(-0.045, 1.045)
        ax.set_xticks([0, 1e2, 1e4, 1e6])
        ax.set_xticklabels([r'$0$', r'$10^{2}$', r'$10^{4}$', r'$10^{6}$'])
        ax.xaxis.set_minor_locator(matplotlib.ticker.SymmetricalLogLocator(
            base=10.0, linthresh=30, subs=[1.0]))
        ax.set_xlabel(r'observation budget $T$')
        ax.set_title(title, pad=4, fontsize=10.5)
        if key == 'frozen':
            ax.axvline(m*m, color='0.35', linestyle=':', linewidth=1.0, zorder=1)

    axes[0].set_ylabel('fraction of instances satisfied')
    axes[0].set_yticks([0, 0.25, 0.5, 0.75, 1.0])

    # --- annotations, positioned in axes fractions and kept clear of the curves ---
    axes[0].text(m*m, 0.35, r'$\Omega(m^{2})$ lower bound', rotation=90,
                 ha='center', va='center', fontsize=10, color='0.32',
                 bbox=dict(boxstyle='square,pad=0.18', facecolor='white',
                           edgecolor='none', alpha=0.88), zorder=5)

    # Two parallel leader lines: identical angle, anchored in the empty upper-right region.
    # Straight leaders of equal length: blue runs vertically from the top edge of its label
    # to the EF1 curve, red runs horizontally from the left edge of its label to the EFX
    # curve.  Because constrained_layout resizes the axes on each draw, the label offsets are
    # solved by iterating draw -> measure -> adjust until the measured gaps equal L_PX.
    # Leaders are drawn explicitly (not via annotate's auto-shrink) so their lengths are
    # exactly equal: each is a straight segment of L_PX pixels ending in an arrow head.
    L_PX  = 15.0
    GAP_PX = 6.0                                   # clearance between label and leader tail
    _x1 = 0.255                                    # blue label centre
    _y2 = 0.35                                     # height where the red leader meets EFX
    _Rf = np.array(D['res']['frozen'])[:, 1]
    _xd = float(np.interp(_y2, _Rf, T))

    t1 = axes[0].text(_x1, 0.0, 'EF1 attained with\nno observations',
                      transform=axes[0].transAxes, ha='center', va='top',
                      fontsize=10, color=C['EF1'], linespacing=1.35, zorder=6)
    t2 = axes[0].text(0.0, _y2, r'$\varepsilon$-EFX and' '\n' r'$\varepsilon$-EF coincide;' '\n'
                      r'$95\%$ at $T\!\approx\!10^{5}$',
                      transform=axes[0].transAxes, ha='left', va='center',
                      fontsize=10, color=C['EFX'], linespacing=1.35, zorder=6)

    fig.canvas.draw(); _r = fig.canvas.get_renderer()
    _ab = axes[0].get_window_extent(renderer=_r); _W, _H = _ab.width, _ab.height
    # axes-fraction height of DATA y = 1.0 (the EF1 curve), not of the top spine
    _lo, _hi = axes[0].get_ylim()
    _y1 = (1.0 - _lo) / (_hi - _lo)
    t1.set_position((_x1, _y1 - (L_PX + GAP_PX)/_H))
    _x2 = axes[0].transAxes.inverted().transform(
              axes[0].transData.transform([[_xd, 0.0]]))[0][0]
    t2.set_position((_x2 + (L_PX + GAP_PX)/_W, _y2))

    axes[0].annotate('', xy=(_x1, _y1), xytext=(_x1, _y1 - L_PX/_H),
                     xycoords='axes fraction', textcoords='axes fraction', zorder=6,
                     arrowprops=dict(arrowstyle='-|>', color=C['EF1'], linewidth=1.0,
                                     mutation_scale=8, shrinkA=0, shrinkB=0))
    axes[0].annotate('', xy=(_x2, _y2), xytext=(_x2 + L_PX/_W, _y2),
                     xycoords='axes fraction', textcoords='axes fraction', zorder=6,
                     arrowprops=dict(arrowstyle='-|>', color=C['EFX'], linewidth=1.0,
                                     mutation_scale=8, shrinkA=0, shrinkB=0))

    axes[1].text(0.5, 0.52, 'all three notions attained' '\n' 'with no observations',
                 transform=axes[1].transAxes, ha='center', va='center', fontsize=10,
                 color='0.15', linespacing=1.35, zorder=6,
                 bbox=dict(boxstyle='round4,pad=0.5', facecolor='white',
                           edgecolor='0.72', linewidth=0.8, alpha=0.97))

    h, l = axes[0].get_legend_handles_labels()
    leg = axes[0].legend(h, l, loc='center left', bbox_to_anchor=(0.030, 0.46),
                         borderaxespad=0.0, handletextpad=0.55)
    leg.set_zorder(6)
    fig.savefig('fig1_separation.pdf', dpi=1200)
    fig.savefig('fig1_separation.png', dpi=220)
    print("saved fig1_separation.pdf / .png")
    print(f"m={m}, eps={eps}, seeds={n}")


# ============================================================================
# Figure 3 (fig3_phase.pdf): cost surface over the (m, epsilon) plane
# source: make_fig3.py
# ============================================================================

def make_figure3_phase():
    import json, numpy as np, matplotlib
    matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib import cm, colors
    from mpl_toolkits.mplot3d import Axes3D  # noqa

    D=json.load(open('fig3_data.json'))
    ms=np.array(D['ms'],float); eps=np.array(D['epss'],float)
    Z=np.array(D['Z'],float); Zl=np.log10(np.maximum(Z,1.0))
    EPS_STAR=D['eps_star']

    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
     'mathtext.fontset':'stix','font.size':9,'axes.labelsize':10.5,'axes.titlesize':10.5,
     'xtick.labelsize':10,'ytick.labelsize':10,'legend.fontsize':10,'axes.linewidth':0.8,
     'xtick.direction':'in','ytick.direction':'in'})

    fig=plt.figure(figsize=(7.6,3.25))
    fig.subplots_adjust(left=0.0500, right=0.9200,bottom=0.1335, top=0.9212,wspace=0.24)

    # ---------------- (a) surface ----------------
    ax=fig.add_subplot(1,2,1,projection='3d')
    Mg,Eg=np.meshgrid(np.log2(ms),eps)
    norm=colors.Normalize(Zl.min(),Zl.max())
    surf=ax.plot_surface(Mg,Eg,Zl,facecolors=cm.viridis(norm(Zl)),rstride=1,cstride=1,
                         linewidth=0.25,antialiased=True,shade=False,alpha=0.97)
    surf.set_edgecolor('white')
    # theoretical vanishing plane
    yy=np.array([EPS_STAR,EPS_STAR]); xx=np.array([np.log2(ms).min(),np.log2(ms).max()])
    X2,Y2=np.meshgrid(xx,yy); Zt=np.linspace(Zl.min(),Zl.max(),2)
    ax.plot_surface(np.array([[xx[0],xx[1]],[xx[0],xx[1]]]),
                    np.array([[EPS_STAR,EPS_STAR],[EPS_STAR,EPS_STAR]]),
                    np.array([[Zl.min(),Zl.min()],[Zl.max(),Zl.max()]]),
                    color='#c0392b',alpha=0.16,linewidth=0,zorder=10)
    ax.plot(xx,[EPS_STAR]*2,[Zl.min()]*2,color='#c0392b',lw=1.4,zorder=11)
    ax.set_xticks(np.log2([8,16,32,48])); ax.set_xticklabels(['8','16','32','48'])
    ax.set_yticks([0.00,0.05,0.10,0.15])
    ax.set_zticks([0,2,4,6]); ax.set_zticklabels([r'$10^{0}$',r'$10^{2}$',r'$10^{4}$',r'$10^{6}$'])
    ax.set_xlabel(r'$m$',labelpad=-1); ax.set_ylabel(r'$\varepsilon$',labelpad=-3)
    ax.set_zlabel(r'observations for $95\%$ empirical success',labelpad=-2,fontsize=10.5)
    ax.view_init(elev=26,azim=-132); ax.set_box_aspect((1.05,1.0,0.94),zoom=1.13)
    ax.xaxis.pane.set_alpha(0.04); ax.yaxis.pane.set_alpha(0.04); ax.zaxis.pane.set_alpha(0.04)
    for a_ in (ax.xaxis,ax.yaxis,ax.zaxis): a_._axinfo['grid'].update(color='0.85',linewidth=0.5)
    ax.tick_params(pad=-2)
    ax.set_title(r'(a) cost surface over $(m,\varepsilon)$',pad=2,y=1.045)
    ax.text2D(0.985,0.905,r'$\varepsilon^{\star}=3/32-\eta$',
              transform=ax.transAxes,fontsize=10.0,color='#c0392b',linespacing=1.3,ha='right',va='top')

    # ---------------- (b) heat map + contours ----------------
    ax2=fig.add_subplot(1,2,2)
    im=ax2.pcolormesh(ms,eps,Zl,cmap='viridis',shading='gouraud',norm=norm,rasterized=True)
    cs=ax2.contour(ms,eps,Zl,levels=[2,3,4,5],colors='white',linewidths=0.7,alpha=0.85)
    _cl=ax2.clabel(cs,fmt=lambda v:r'$10^{%d}$'%int(v),fontsize=10.0,inline=True,inline_spacing=4,
                   manual=[(13.0,0.127),(26.0,0.104),(13.0,0.026),(39.0,0.021)])
    for _t in _cl: _t.set_fontweight('bold')
    ax2.axhline(EPS_STAR,color='#c0392b',lw=1.4)
    ax2.text(8.4,EPS_STAR+0.0045,r'$\varepsilon^{\star}$',ha='left',va='bottom',
             fontsize=10.0,color='#c0392b',zorder=6,
             bbox=dict(boxstyle='square,pad=0.15',facecolor='white',edgecolor='none',alpha=0.82))
    ax2.set_xscale('log',base=2); ax2.set_xticks([8,16,32,48]); ax2.set_xticklabels(['8','16','32','48'])
    ax2.set_xlabel(r'number of goods $m$'); ax2.set_ylabel(r'tolerance $\varepsilon$')
    ax2.set_title(r'(b) the same data, with cost contours',pad=5)
    ax2.set_ylim(eps.min(),eps.max())
    cb=fig.colorbar(im,ax=ax2,pad=0.028,fraction=0.052)
    cb.set_label(r'observations for $95\%$ empirical success',fontsize=10.5,rotation=90,labelpad=8)
    cb.set_ticks([0,2,4,6]); cb.set_ticklabels([r'$10^{0}$',r'$10^{2}$',r'$10^{4}$',r'$10^{6}$'])
    cb.ax.tick_params(labelsize=10)

    # ALIGN_TITLES: put the 3D panel's title at the same figure-y as the 2D panel's
    fig.canvas.draw(); _r = fig.canvas.get_renderer()
    _t2 = ax2.title.get_window_extent(renderer=_r)
    _t1 = ax.title.get_window_extent(renderer=_r)
    _fh = fig.get_window_extent(renderer=_r).height
    _dy = (_t2.y0 - _t1.y0) / _fh
    _x, _y = ax.title.get_position()
    ax.title.set_position((_x, _y + _dy / (ax.get_window_extent(renderer=_r).height / _fh)))

    fig.savefig('fig3_phase.pdf',dpi=1200); fig.savefig('fig3_phase.png',dpi=220)
    print("saved fig3_phase")
    print("row at eps=0.150:",Z[-1]); print("eps*=",EPS_STAR)

# ============================================================================
# Figure 4 (fig4_robustness.pdf): robustness outside the hypotheses
# source: make_fig4.py
# ============================================================================

def make_figure4_robustness():
    import json, numpy as np, matplotlib
    matplotlib.use('Agg'); import matplotlib.pyplot as plt
    from matplotlib import colors

    D=json.load(open('fig4_data.json'))
    S=np.array(D['S']); noise=D['noise']; cls=D['classes']; inth=D['inth']; eps=D['eps']

    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],
     'mathtext.fontset':'stix','font.size':9,'axes.labelsize':9.5,'axes.titlesize':9.2,
     'xtick.labelsize':8,'ytick.labelsize':8,'legend.fontsize':8,'axes.linewidth':0.8,
     'xtick.direction':'out','ytick.direction':'out'})

    fig=plt.figure(figsize=(7.2,3.0))
    gs=fig.add_gridspec(1,2,width_ratios=[1.30,1.0],left=0.1253, right=0.9757,
                        bottom=0.3320, top=0.9066,wspace=0.82)

    # ---- (a) success-rate grid ----
    ax=fig.add_subplot(gs[0,0])
    cmap=plt.get_cmap('RdYlGn'); norm=colors.Normalize(0.75,1.0)
    im=ax.imshow(S,cmap=cmap,norm=norm,aspect='auto')
    ax.set_xticks(range(len(cls))); SHORT={'coverage':'coverage','matroid rank':'matroid rank','budget-add.':'budget-add.','unit-demand':'unit-demand','XOS':'XOS','rand. monotone':'rand. monotone'}
    ax.set_xticklabels([SHORT.get(c,c) for c in cls],rotation=90,ha='center',va='top',fontsize=7.2)
    ax.set_yticks(range(len(noise))); ax.set_yticklabels(noise)
    for i in range(S.shape[0]):
        for j in range(S.shape[1]):
            v=S[i,j]
            ax.text(j,i,f'{v:.2f}'.lstrip('0'),ha='center',va='center',fontsize=7.4,
                    color='black' if v>0.86 else 'white', zorder=3)
    viol=[i for i,ok in enumerate(inth) if not ok]
    if viol:
        ax.add_patch(plt.Rectangle((-0.5,min(viol)-0.5),len(cls),len(viol),fill=False,
                     edgecolor='#2c3e50',linewidth=1.8,zorder=5))
        ax.annotate('outside the\nassumptions',
                    xy=(len(cls)-0.42,np.mean(viol)),xycoords='data',
                    xytext=(len(cls)+0.28,np.mean(viol)),textcoords='data',
                    ha='left',va='center',fontsize=7.2,color='#2c3e50',linespacing=1.3,
                    annotation_clip=False,
                    arrowprops=dict(arrowstyle='-|>',color='#2c3e50',lw=0.8,
                                    mutation_scale=7,shrinkA=1,shrinkB=1))
    ax.set_title(r'(a) fraction of instances truly $\varepsilon$-EFX')

    # ---- (b) bias, which is what actually matters ----
    ax2=fig.add_subplot(gs[0,1])
    rng=np.random.default_rng(0); s=0.25; N=200000; vs=np.linspace(0,1,21)
    series={'uniform':lambda v: v+rng.uniform(-s,s,N),
            'Bernoulli':lambda v: (rng.random(N)<min(1,max(0,v))).astype(float),
            'trunc. Gauss':lambda v: np.clip(v+rng.normal(0,s,N),0,1),
            'Gaussian':lambda v: v+rng.normal(0,s,N),
            r'$t_3$ heavy tail':lambda v: v+s*rng.standard_t(3,N)}
    STY={'uniform':('#7f8c8d','-'),'Bernoulli':('#8e44ad','-'),'trunc. Gauss':('#c0392b','-'),
         'Gaussian':('#1b6ca8','--'),r'$t_3$ heavy tail':('#16a085','--')}
    for k,fn in series.items():
        b=[np.mean(fn(v))-v for v in vs]
        c,ls=STY[k]; ax2.plot(vs,b,color=c,ls=ls,lw=1.5,label=k)
    for sgn in (+1,-1):
        ax2.axhline(sgn*eps,color='0.45',ls=':',lw=1.0,zorder=1)
    ax2.text(0.015,eps,r'$+\varepsilon$',ha='left',va='bottom',fontsize=7.4,color='0.35',zorder=2)
    ax2.text(0.015,-eps,r'$-\varepsilon$',ha='left',va='top',fontsize=7.4,color='0.35',zorder=2)
    ax2.set_xlabel(r'true bundle value $v$'); ax2.set_ylabel(r'bias  $\mathbb{E}[X]-v$')
    ax2.set_title(r'(b) bias of each noise model')
    ax2.set_xlim(0,1); ax2.set_ylim(-0.145,0.235)
    ax2.legend(loc='upper right',bbox_to_anchor=(0.975,0.975),handlelength=1.8,
               handletextpad=0.5,borderaxespad=0.0,framealpha=0.96,edgecolor='0.7',fontsize=6.9)
    ax2.grid(alpha=0.25,linewidth=0.5)
    fig.savefig('fig4_robustness.pdf',dpi=1200); fig.savefig('fig4_robustness.png',dpi=220)
    print("min success:",S.min(),"at",noise[int(np.argmin(S)//S.shape[1])],cls[int(np.argmin(S)%S.shape[1])])
    print("trunc-Gauss row:",S[2].round(3)," Gaussian row:",S[3].round(3))


# ============================================================================
# Figure 5 (fig5_realdata.pdf): non-constructed preference and ranking data
# source: make_fig5.py
# ============================================================================

def make_figure5_realdata():
    import json, numpy as np, matplotlib
    matplotlib.use('Agg'); import matplotlib.pyplot as plt
    D=json.load(open('realdata.json'))
    def wilson(p,n,z=1.96):
        d=1+z*z/n; c=(p+z*z/(2*n))/d; h=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/d; return np.clip(c-h,0,1),np.clip(c+h,0,1)
    plt.rcParams.update({'font.family':'serif','font.serif':['Times New Roman','DejaVu Serif'],'mathtext.fontset':'stix',
     'font.size':9,'axes.labelsize':10,'axes.titlesize':9.2,'xtick.labelsize':8.5,'ytick.labelsize':8.5,'legend.fontsize':8,
     'axes.linewidth':0.8,'xtick.direction':'in','ytick.direction':'in','axes.grid':True,'grid.alpha':0.25,'grid.linewidth':0.5,
     'legend.frameon':True,'legend.framealpha':0.95,'legend.edgecolor':'0.7'})
    C={'EF1':'#1b6ca8','EFX':'#c0392b','EF':'#7f8c8d'}; MK={'EF1':'o','EFX':'s','EF':'^'}
    LB={'EF1':r'$\varepsilon$-EF1','EFX':r'$\varepsilon$-EFX','EF':r'$\varepsilon$-EF'}
    fig,axes=plt.subplots(1,2,figsize=(7.2,3.0))
    fig.subplots_adjust(left=0.0734, right=0.9831,bottom=0.1564, top=0.9068,wspace=0.30)

    # (a) AGH frozen vs unfrozen
    ax=axes[0]; n=300
    Ts=[int(t) for t in D['agh']['frozen'].keys()]; Ts.sort()
    for setting,ls,alpha in (('frozen','-',1.0),('unfrozen',(0,(3.2,2.0)),0.75)):
        R=np.array([D['agh'][setting][str(t)] for t in Ts])
        for j,nm in enumerate(('EF1','EFX','EF')):
            p=R[:,j]; lo,hi=wilson(p,n)
            if setting=='frozen': ax.fill_between(Ts,lo,hi,color=C[nm],alpha=0.13,linewidth=0)
            ax.plot(Ts,p,color=C[nm],ls=ls,lw=1.5,alpha=alpha,marker=MK[nm],ms=3.4,markeredgewidth=0,
                    markevery=(j,2) if setting=='frozen' else (j+1,2),
                    label=LB[nm]+(' (fixed)' if setting=='frozen' else ' (released)'))
    ax.set_xscale('symlog',linthresh=30,linscale=0.4); ax.set_xlim(-2,3e4); ax.set_ylim(0.25,1.03); ax.set_yticks([0.3,0.5,0.7,0.9,1.0])
    ax.set_xticks([0,1e2,1e3,1e4]); ax.set_xticklabels([r'$0$',r'$10^{2}$',r'$10^{3}$',r'$10^{4}$'])
    ax.set_xlabel(r'observation budget $T$'); ax.set_ylabel('fraction of student pairs satisfied')
    ax.set_title('(a) AGH course rankings, pairs of students')
    h,l=ax.get_legend_handles_labels(); ax.legend(h,l,loc='lower right',ncol=2,handlelength=2.0,columnspacing=0.9,handletextpad=0.5,fontsize=7.2)

    # (b) cleanweb EFX consultations vs m
    ax=axes[1]
    cw=np.array(D['cleanweb']['efx']); ms=cw[:,0]; cons=cw[:,2]; succ=cw[:,1]
    ax.plot(ms,cons,color=C['EFX'],marker='s',ms=3.8,markeredgewidth=0,lw=1.6,label='epoch cutter, measured',zorder=3)
    ax.plot(ms,1.5*ms,color=C['EFX'],ls=':',lw=1.0,alpha=0.85,label=r'$1.5\,m$ reference')
    ax.set_xscale('log',base=2); ax.set_yscale('log')
    ax.set_xticks([16,32,64,128,240]); ax.set_xticklabels(['16','32','64','128','240'])
    ax.set_xlabel(r'number of items $m$'); ax.set_ylabel('distinct bundles consulted')
    ax.set_title('(b) cleanweb, two rankers of up to 240 items')
    ax.legend(loc='upper left',handlelength=2.0,handletextpad=0.5)
    ax.text(0.97,0.06,r'$\varepsilon$-EFX attained on $100\%$ of pairs at every $m$',transform=ax.transAxes,
            ha='right',va='bottom',fontsize=7.4,color=C['EFX'])
    fig.savefig('fig5_realdata.pdf',dpi=1200); fig.savefig('fig5_realdata.png',dpi=220); print("saved fig5")


# ============================================================================
FIGURES = {
    1: make_figure1_ablation,
    2: make_figure2_separation,
    3: make_figure3_phase,
    4: make_figure4_robustness,
    5: make_figure5_realdata,
}

if __name__ == "__main__":
    wanted = [int(a) for a in sys.argv[1:]] or sorted(FIGURES)
    for k in wanted:
        if k not in FIGURES:
            print(f"no Figure {k}; choose from {sorted(FIGURES)}")
            continue
        print(f"Figure {k} ...", end=" ", flush=True)
        FIGURES[k]()
        print("done")
