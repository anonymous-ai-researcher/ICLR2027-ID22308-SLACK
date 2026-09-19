<div align="center">

# One Item of Slack

### Separating EF1 from EFX under Noisy Observations

<br>

$$\Large \textsf{EF1} : \exists\, g \qquad\qquad \textsf{EFX} : \forall\, g$$

**One quantifier. A quadratic gap.**

<br>

[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/)
[![Exact](https://img.shields.io/badge/arithmetic-exact%20rational-success.svg?style=flat-square)](#part-3--verification-where-we-tried-to-break-it)
[![Seeded](https://img.shields.io/badge/seeds-fixed-orange.svg?style=flat-square)](#appendix--every-number-in-one-place)
[![Anonymous](https://img.shields.io/badge/review-double--blind-lightgrey.svg?style=flat-square)](#)

</div>

---

## The story

Two agents. One of them already holds two items that nobody can take away: $g^\*$, worth
almost everything, and $g^\circ$, worth $\eta = 2^{-10}$ — a rounding error with a name.
A pool of $m$ spare goods sits between them. You may hand out $m/2$ of them to repair the envy.

You cannot see the valuations. You can only sample them, noisily, one observation at a time.

Now pick your fairness notion.

**Pick EF1.** You are allowed to discard *some* item from the bundle you envy. Discard
$g^\*$. What is left is worth $\eta$. Any single pool item beats that. **Hand over item
number one and stop. You never looked at the data.**

**Pick EFX.** You must survive discarding *any* item — including $g^\circ$, the worthless
one. What is left is worth $\tfrac38 - \eta$. Now you have to build a bundle nearly that
valuable, and the only bundles that qualify are the ones matching a hidden set $S_\theta$
you cannot see. **You are going to be here a while.**

$$\textsf{EF1: } 0 \text{ observations} \qquad\qquad \textsf{EFX: } \Omega(m^2) \text{ observations}$$

Same agents. Same valuations. Same goods. Same budget. The gap is the quantifier.

<details>
<summary><b>Where exactly does the quadratic come from?</b> (click)</summary>

<br>

Flipping one hidden bit moves any bundle's value by at most $\tfrac{3}{8m}$. That is the
signal. Bernoulli divergence is **quadratic** in the mean gap, so one observation carries

$$O\!\left(\left(\tfrac{3}{8m}\right)^2\right) = O(1/m^2) \text{ bits}$$

about that coordinate. There are $m/2$ coordinates to learn. Divide:

$$\frac{m/2}{O(1/m^2)} = \Omega(m^2)$$

Assouad's lemma turns that counting argument into a theorem. The constants are in
`verification/verify_thm31.py`, computed in exact rationals so you can check them yourself.

And the upper bound? A single observation of a bundle is a **noisy linear measurement of
all of $\theta$ at once**. An estimator that exploits this needs $O(m^2)$ — matching.
Sharing observations across coordinates is worth a factor of $m$ over the naive scheme.

</details>

---

## Part 1 — Reproduce the headline in one command

```bash
pip install -r requirements.txt
python experiments/run_fig1.py
```

**Fixed parameters** (hardcoded, no flags):

| | |
|:--|:--|
| goods | $m = 32$ |
| tolerance | $\varepsilon = 1/128 = 0.0078125$ |
| instances | $300$ |
| observation model | Bernoulli |
| budgets $T$ | $0$, then 22 log-spaced points over $[10^{1.0},\, 10^{5.4}]$ |
| estimator | conditional-mean over random half-sets |
| seed | `default_rng(0)` for EEAG, `default_rng(1)` for standard |

**What you should see** — one algorithm, one allocation, three verdicts:

```
--- frozen, m=32, eps=0.0078125, seeds=300 ---
T=0      EF1=1.000  EFX=0.000  EF=0.000
...
T≈5.9e4  EF1=1.000  EFX≈0.50   EF≈0.50
T≈9.6e4  EF1=1.000  EFX≈0.95   EF≈0.95
```

EF1 is satisfied at $T=0$ and never wavers. EFX crosses half around $5.9 \times 10^4$ and
$95\%$ around $9.6 \times 10^4$. At $m = 32$ that puts the measured constant in front of
$m^2$ at **58 and 93**.

> **The experiment is rigged against us, deliberately.** The algorithm is told $T$ but
> **not** which notion will judge it. It produces one allocation; that allocation is then
> checked against all three. No notion gets a bespoke method, so no difference can come
> from the algorithm. And success is scored under the **true** valuations — an algorithm
> that believes it succeeded still fails if the truth disagrees.

---

## Part 2 — The whole picture

### The phase plane

```bash
python experiments/run_fig3.py      # slow: bisection over a 6×9 grid
```

| | |
|:--|:--|
| goods | $m \in \{8, 12, 16, 24, 32, 48\}$ |
| tolerance | $\varepsilon \in \{0.002,\, 0.008,\, 0.031,\, 0.062,\, 0.078,\, 0.093,\, 0.100,\, 0.120,\, 0.150\}$ |
| instances per evaluation | $60$ |
| threshold | first $T$ with $\ge 95\%$ success, by bisection to a factor $1.45$ |
| seed | `default_rng(0)` |

Cost climbs steeply in $m$, gently in $1/\varepsilon$, then **falls off a cliff** at
$\varepsilon^\star = \tfrac{3}{32} - \eta \approx 0.0928$. That line is drawn from theory,
not fitted to the data — and the collapse begins right above it.

### What the epoch rule buys

```bash
python experiments/run_fig2.py
```

$\varepsilon = 0.1$, $m \in \{8, 16, 24, 32, 48, 64, 96, 128, 192, 256\}$, 40 seeds per
point on random instances.

On the adversarial anchor: re-examination consults $\Theta(m^2)$ bundles (fitted exponent
$1.93$, bootstrap interval $[1.91, 1.96]$), the epoch rule consults $\Theta(m)$ (exponent
$0.95$, interval $[0.92, 0.97]$). Disjoint intervals; each excludes the other's exponent.

### Outside the hypotheses

```bash
python experiments/run_fig4.py
```

$m = 24$, $\varepsilon = 0.10$, $\sigma = 0.25$, $300$ instances per cell, identical
per-bundle sample budget everywhere. Six valuation classes × six noise models.

The interesting row is the one that **breaks**: truncated Gaussian is bounded but
**biased**, and it drops to $0.80$. Unbounded Gaussian and $t_3$ heavy tails stay at
$0.97$ and above. On this grid the failure mode is bias, not unboundedness.

### Beyond two agents

```bash
python experiments/run_n3.py
```

$\varepsilon = 0.1$, $m = 6$, additive Dirichlet valuations,
$T \in \{0, 300, 1000, 3000, 10^4, 3 \times 10^4\}$, $150$ instances for $n = 2, 3$ and
$100$ for $n = 4$, seed `default_rng(0)`.

### Where the proof constants stop working

```bash
python experiments/run_ablation.py
```

Margin $\tau / \varepsilon \in \{0.25, 0.5, 0.75, 1.0, 1.25\}$ at fixed
$\varepsilon_0 = \varepsilon/8$; then the coupled path $\tau = 6\varepsilon_0$ with
$\varepsilon_0 / \varepsilon \in \{1/32, 1/16, 1/8, 1/4, 1/2\}$; then
$\delta \in \{10^{-1}, \ldots, 10^{-4}\}$.

### Non-constructed data

```bash
python experiments/realdata.py      # fetches PrefLib; needs network
```

AGH course survey (146 students × 9 courses) and cleanweb rankings (up to 240 items).
$\varepsilon = 0.1$, $\sigma = 0.25$, 200 repetitions per bundle, seeds
`default_rng(0)` / `Random(0)`.

### Statistics

```bash
python experiments/stats_fig1.py    # exact McNemar, Holm correction
python experiments/gen_tables.py    # LaTeX tables from the JSON
```

Comparisons between two notions are made on the **same** instance with the **same**
observations, so the test is the exact McNemar test with Holm correction.

---

## Part 3 — Verification, where we tried to break it

Theory papers hide arithmetic slips in plain sight. We went looking for ours.

### The lower bound, in exact rationals

```bash
python verification/verify_thm31.py
```

No floats. No rounding. No "approximately". Everything is `fractions.Fraction`.

| check | scope | result |
|:--|:--|:--|
| monotonicity, submodularity | all subsets, $m \le 8$, every $\theta$ | ✓ |
| recovery inequality | 27,152 pairs $(\theta,\rho)$ at $m = 8$ | max $d_H = \mathbf{0}$ |
| mean-shift bound | 65,536 exact comparisons at $m = 8$ | equals $3/(8m)$ **exactly** |
| Assouad chain | symbolic | gap $= \mathbf{1/192} > 0$ |

That last row is the entire lower bound compressed into one number:

$$\underbrace{\tfrac{7}{32}}_{\text{Assouad gives}} \;-\; \underbrace{\tfrac{41}{192}}_{\text{success allows}} \;=\; \tfrac{1}{192} \;>\; 0$$

Positive. The argument closes. Change $\eta$ or $\varepsilon$ enough and it stops closing —
that is why the theorem says $\varepsilon \le 1/128$.

### The algorithm, against an adversary

```bash
python verification/verify_adversary.py
```

At **every** consultation, the adversary branches on the estimate taking either endpoint
of its accuracy interval — all $2^k$ patterns of $k$ consultations. Over **770,576
complete adversarial paths** on random coverage, random monotone, and anchor instances
with $m \le 6$: every leaf was a two-sided $\varepsilon$-EFX partition under the true
valuation, within the stated consultation and epoch bounds.

<details>
<summary><b>The bug the adversary found</b> (click)</summary>

<br>

A checker that recomputes the scan order after each move — rather than iterating over the
order fixed at the start of the pass — **reports failures**.

We did not know that mattered. The adversary found it before a reviewer could. That is why
the theorem now states the snapshot requirement explicitly.

</details>

---

## What is in here

```
src/
  core.py               the hard family I_m(θ), the noisy observation model,
                        and the fairness checks under TRUE valuations
  cutter_ls.py          the epoch cutter: two-sided ε-EFX from estimates

experiments/            run_fig1  the separation (start here)
                        run_fig2  consultation counts, epoch vs re-examination
                        run_fig3  the (m, ε) phase plane
                        run_fig4  robustness outside the hypotheses
                        run_n3    beyond two agents
                        run_ablation  where the proof constants stop working
                        realdata  PrefLib preference and ranking data
                        stats_fig1, gen_tables

verification/           verify_thm31      the lower bound, exact rationals
                        verify_adversary  the cutter, 770,576 paths

figures/                make_all_figures.py   all five figures, one file
```

### Figures

```bash
python figures/make_all_figures.py        # all five
python figures/make_all_figures.py 3 5    # just Figures 3 and 5
```

The file names keep the historical numbering of the experiment scripts; the mapping to
paper figures is in the module docstring.

---

## Reproduce everything

```bash
pip install -r requirements.txt

for f in experiments/run_*.py; do python "$f"; done   # writes *.json
python experiments/realdata.py                        # needs network
python experiments/stats_fig1.py
python figures/make_all_figures.py                    # writes *.pdf, *.png

python verification/verify_thm31.py                   # slow, exact arithmetic
python verification/verify_adversary.py               # slow, 2^k branching
```

Expect the phase plane and the two verification scripts to take a while. The exact-rational
arithmetic at $m = 8$ is slow **on purpose** — floats would defeat the point.

---

## Appendix — every number in one place

| experiment | $m$ | $\varepsilon$ | instances | $\sigma$ | seed | noise |
|:--|:--|:--|:--|:--|:--|:--|
| `run_fig1` | 32 | 1/128 | 300 | — | 0 / 1 | Bernoulli |
| `run_fig2` | 8…256 | 0.1 | 40 | — | 7 | — |
| `run_fig3` | 8…48 | 0.002…0.150 | 60 | — | 0 | Bernoulli |
| `run_fig4` | 24 | 0.10 | 300 | 0.25 | 7919·i+131·j+s | 6 models |
| `run_n3` | 6 | 0.1 | 150 / 100 | — | 0 | uniform |
| `run_ablation` | 20 | 0.1 | 150 | 0.25 | 100+s / 200+s | uniform |
| `realdata` | 9 / 240 | 0.1 | 300 / 200 | 0.25 | 0 | uniform |

**Constants of the construction**: $\eta = 2^{-10}$; pool items worth $\tfrac{3}{16}$ each;
hidden-set items add $\tfrac{3}{8m}$; $g^\*$ worth $\tfrac38 - \eta$; $g^\circ$ worth $\eta$;
budget $k = m/2$; $\varepsilon^\star = \tfrac{3}{32} - \eta$.

**Algorithm constants**: margin $\tau = 6\varepsilon_0$ with $\varepsilon_0 = \varepsilon/8$;
epoch cap $\lceil 4/\varepsilon \rceil + 1$.

All randomness is seeded. Given the seed, the JSON outputs are deterministic.

---

<div align="center">

<br>

*One item of slack lets an allocation stop tracking valuations at the scale of single items.*

*A fixed pair that cannot be reallocated separately puts that scale back.*

<br>

</div>
