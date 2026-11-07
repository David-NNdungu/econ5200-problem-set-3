# Phase 4 AI Appendix

**Model:** ChatGPT  
**Date:** November 6, 2026

I included the assigned bootstrap prompt, my revision for the county-year panel, and the prompt for reviewing my parallel-trends paragraph. I also recorded how I checked the bootstrap and what I changed in my paragraph.

## Task 4.1 — Assigned prompt

```text
[Prep] Act as an applied microeconometrician who has implemented
cluster-robust inference for panels with very few clusters.

[Request] Implement the wild cluster bootstrap exactly to the
specification below, for a county-year panel with treatment assigned
at the level of eight regional boards. Impose the null, apply
Rademacher weights at the cluster level, enumerate all 256 weight
vectors rather than resampling, and return the bootstrap p-value for
the treatment coefficient.
1. Fit the restricted model: your DiD regression with the treatment coefficient forced to zero. Keep the restricted residuals ũi and fitted values ỹi.
2. Draw one Rademacher weight per board — +1 or −1, each with probability one half. One weight per board, not per observation.
3. Build a synthetic outcome y*i = ỹi + wb(i) ũi, where b(i) is county i’s board.
4. Re-estimate the unrestricted model on y* and store the cluster-robust t-statistic on the treatment coefficient.
5. The bootstrap p-value is the share of |t*| at least as large as your actual |t|.
6. With 8 boards there are only 2^8 = 256 distinct weight vectors, so enumerate all 256 rather than resampling.

[Iterate] numpy, pandas and statsmodels only. Reuse my panel's column
names. The function must accept the cluster variable as an argument.

[Mechanism Check] Explain why the weights are applied to residuals at
the CLUSTER level rather than the observation level, why imposing the
null matters, and what changes when the number of clusters drops
below roughly ten.

[Evaluate] Run it on my panel and compare the p-value against the
naive cluster-robust one. Tell me which conclusion changes.
```

**Model reply:** [Paste the full reply to the assigned prompt here.]

## Task 4.1 — Revised prompt

```text
[Prep] Act as an applied microeconometrician who has implemented
cluster-robust inference for panels with very few clusters.

[Request] Implement the wild cluster bootstrap exactly to the
specification below, for a county-year panel with treatment assigned
at the level of eight regional boards. Impose the null, apply
Rademacher weights at the cluster level, enumerate all 256 weight
vectors rather than resampling, and return the bootstrap p-value for
the treatment coefficient.
1. Fit the restricted model: your DiD regression with the treatment coefficient forced to zero. Keep the restricted residuals ũi and fitted values ỹi.
2. Draw one Rademacher weight per board — +1 or −1, each with probability one half. One weight per board, not per observation.
3. Build a synthetic outcome y*i = ỹi + wb(i) ũi, where b(i) is county i’s board.
4. Re-estimate the unrestricted model on y* and store the cluster-robust t-statistic on the treatment coefficient.
5. The bootstrap p-value is the share of |t*| at least as large as your actual |t|.
6. With 8 boards there are only 2^8 = 256 distinct weight vectors, so enumerate all 256 rather than resampling.

[Iterate] Use NumPy, pandas and statsmodels for numerical work. Accept the panel, a formula, the coefficient name and the cluster column. My DataFrame is `panel`, my formula is `y ~ D + C(county) + C(year)`, my coefficient is `D`, and my cluster column is `board`. Hold the fixed effects and the estimation rows fixed when imposing the null and in every bootstrap draw. Use board-clustered t-statistics and compute the conventional board-clustered p-value with t reference degrees of freedom. Count numerical ties and return the extreme count and the total number of vectors.

[Mechanism Check] Explain why the weights are applied to residuals at
the CLUSTER level rather than the observation level, why imposing the
null matters, and what changes when the number of clusters drops
below roughly ten.

[Evaluate] Run it on my panel and compare the p-value against the
naive cluster-robust one. Tell me which conclusion changes.
```

**Model reply:** [Paste the full reply to the revised prompt here.]

### What I changed and how I checked it

- I specified the formula and coefficient so the null removes only treatment and retains the county and year fixed effects.
- I specified the `board` column and used one sign per board to preserve within-board dependence.
- I specified a common set of estimation rows and board-clustered t-statistics for the observed outcome and all synthetic outcomes.
- I counted numerical ties to preserve the sign-pair symmetry of the two-sided tail.
- I returned both p-values and the extreme count to make the decision reproducible. The function is in [src/did_toolkit.py](src/did_toolkit.py).

```text
Board-clustered t: 1.8277
Conventional board-clustered p: 0.110313
Wild cluster bootstrap p: 0.132812
Extreme vectors: 34 of 256
Smallest attainable two-sided p: 0.007812
```

## Task 4.3 — Hostile-read prompt

```text
[Prep] Act as the state agency's lead econometrician. You believe the
programme works and you are reading an external review that says your
TWFE estimate is uninformative.

[Request] Here is the reviewer's paragraph on parallel trends and
identification: 
I omit event time −1, the last year before adoption, so each coefficient measures the treated group's change relative to its comparison group from that baseline. The estimated leads are small relative to the post-adoption effects. That pattern is consistent with parallel trends before adoption, but it cannot establish how treated counties would have evolved without training. To interpret the post-adoption estimates causally, I would need to argue that untreated outcome changes would have been the same for each cohort and its comparison counties and that counties did not respond before adoption.

Give the three strongest
objections you would raise in a written response.

[Evaluate] Rank them by how much damage each does to the reviewer's
conclusion.
```

**Model reply:** [Paste the full reply to the hostile-read prompt here.]

### My review notes

1. The later estimates rely on one never-treated board, so a shock specific to that board could influence several estimates.
2. With few boards and varying cohort coverage, near-zero leads offer limited information about deviations from parallel trends.
3. If the agency argues that flat leads validate its TWFE coefficient, the decomposition gives a separate response. Even exact parallel trends before treatment would leave the early cohort's growing gains in the already-treated control comparisons.

The two paragraph versions and the decision on each objection appear in [the notebook](Econ_5200_PS3.ipynb).
