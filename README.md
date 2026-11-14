# One Item of Slack

### Separating EF1 from EFX under Noisy Observations

$$\text{EF1} : \exists g \qquad\qquad \text{EFX} : \forall g$$

**One quantifier. A quadratic gap.**

[![ICLR](https://img.shields.io/badge/ICLR-2027-8B5CF6.svg?style=flat-square)](https://iclr.cc/)
[![Python](https://img.shields.io/badge/python-3.9+-blue.svg?style=flat-square)](https://www.python.org/)
[![Exact](https://img.shields.io/badge/arithmetic-exact%20rational-success.svg?style=flat-square)](#part-3-verification-where-we-tried-to-break-it)
[![Seeded](https://img.shields.io/badge/seeds-fixed-orange.svg?style=flat-square)](#appendix-every-number-in-one-place)

> Anonymized code for an **ICLR 2027** submission under double-blind review.

---

## Welcome

> *Every fairness guarantee in the textbook quietly assumes that somebody knows exactly what
> everybody wants. In practice, nobody ever does.*

Picture a university after the first round of course registration. Students already hold
seats they will not give up. A handful of seats has just been freed. The registrar wants to
hand them out so that no student is left envying a classmate, and the only window into what
students want is noisy: survey answers, ranked lists, a few clicks. Every question costs
time, and every answer is slightly wrong.

That is the world this paper lives in. **Fairness has to be certified from estimates, not
from the truth.**

Two fairness notions dominate the field, and they differ by a single word:

| | EF1 | EFX |
|---|---|---|
| envy must vanish after removing | **some** item | **every** item |

Where these two notions have been told apart before, the difference came from **existence**
(an EFX allocation can fail to exist) or from **computation** (exact EFX can take
exponentially many queries). We found a gap that comes from neither. On our instances a
perfectly envy-free allocation always exists, it is easy to describe, and the gap is
**purely informational**:

| on our hard family | EF1 | EFX |
|---|---|---|
| an exactly envy-free allocation exists | yes | yes |
| noisy observations needed to certify it | **0** | **$\Theta(m^2)$** |

Zero versus quadratic. Same instances, same agents, same budget. Nothing differs but the
quantifier.

### The whole paper in one picture

```
               held by agent a1, cannot be split       pool of spare goods
             ┌───────────────────────────────┐     ┌──────────────────────────┐
             │  g*   worth almost everything │     │  r1  r2  r3  ...  rm     │
             │  g°   worth 2^-10             │     │  hand out at most m/2    │
             └───────────────────────────────┘     └──────────────────────────┘
                              │                                 │
          EF1 may drop g*:  almost nothing is left    EFX must drop g°:  3/8 - η is left
          one pool item already beats it              only the hidden set S_θ can match it
                              │                                 │
                      0 observations                   Θ(m²) observations
```

*EF1 may discard the one item that matters. EFX must survive discarding the one that does
not.* The rest of this README turns that sentence into numbers you can rerun.


---

## The story

Two agents. One of them already holds two items that nobody can take away: $g^{*}$, worth
almost everything, and $g^{\circ}$, worth $\eta = 2^{-10}$, a rounding error with a name.
A pool of $m$ spare goods sits between them. You may hand out $m/2$ of them to repair the envy.

You cannot see the valuations. You can only sample them, noisily, one observation at a time.

Now pick your fairness notion.

**Pick EF1.** You are allowed to discard *some* item from the bundle you envy. Discard
$g^{*}$. What is left is worth $\eta$. Any single pool item beats that.
**Hand over item number one and stop. You never looked at the data.**

**Pick EFX.** You must survive discarding *any* item, including $g^{\circ}$, the worthless
one. What is left is worth $3/8 - \eta$. Now you have to build a bundle nearly that
valuable, and the only bundles that qualify are the ones matching a hidden set $S_\theta$
you cannot see. **You are going to be here a while.**

$$\text{EF1}: 0 \text{ observations} \qquad\qquad \text{EFX}: \Omega(m^2) \text{ observations}$$

Same agents. Same valuations. Same goods. Same budget. The gap is the quantifier.

<details>
<summary><b>Where exactly does the quadratic come from?</b></summary>

<br>

Flipping one hidden bit moves any bundle's value by at most $3/(8m)$. That is the signal.
Bernoulli divergence is **quadratic** in the mean gap, so one observation carries

$$O\left(\left(\frac{3}{8m}\right)^2\right) = O\left(\frac{1}{m^2}\right) \text{ bits}$$

about that coordinate. There are $m/2$ coordinates to learn. Divide:

$$\frac{m/2}{O(1/m^2)} = \Omega(m^2)$$

Assouad's lemma turns that counting argument into a theorem. The constants are in
`verification/verify_thm31.py`, computed in exact rationals so you can check them yourself.

And the upper bound? A single observation of a bundle is a **noisy linear measurement of
all of $\theta$ at once**. An estimator that exploits this needs $O(m^2)$, matching.
Sharing observations across coordinates is worth a factor of $m$ over the naive scheme.

</details>

---

## Appendix: every number in one place

| experiment | $m$ | $\varepsilon$ | instances | $\sigma$ | seed | noise |
|---|---|---|---|---|---|---|
| `run_fig1` | 32 | 1/128 | 300 | n/a | 0 / 1 | Bernoulli |
| `run_fig2` | 8–256 | 0.1 | 40 | n/a | 7 | n/a |
| `run_fig3` | 8–48 | 0.002–0.150 | 60 | n/a | 0 | Bernoulli |
| `run_fig4` | 24 | 0.10 | 300 | 0.25 | $7919i + 131j + s$ | 6 models |
| `run_n3` | 6 | 0.1 | 150 / 100 | n/a | 0 | uniform |
| `run_ablation` | 20 | 0.1 | 150 | 0.25 | `100+s` / `200+s` | uniform |
| `realdata` | 9 / 240 | 0.1 | 300 / 200 | 0.25 | 0 | uniform |

**Constants of the construction**

$$\eta = 2^{-10}, \qquad \text{pool item} = \frac{3}{16}, \qquad \text{hidden-set extra} = \frac{3}{8m}$$

$$g^{*} = \frac{3}{8} - \eta, \qquad g^{\circ} = \eta, \qquad k = \frac{m}{2}, \qquad \varepsilon^{\star} = \frac{3}{32} - \eta$$

**Algorithm constants**

$$\tau = 6\varepsilon_0 \quad \text{with} \quad \varepsilon_0 = \frac{\varepsilon}{8}, \qquad \text{epoch cap} = \left\lceil \frac{4}{\varepsilon} \right\rceil + 1$$

All randomness is seeded. Given the seed, the JSON outputs are deterministic.

---

*One item of slack lets an allocation stop tracking valuations at the scale of single items.*

*A fixed pair that cannot be reallocated separately puts that scale back.*
