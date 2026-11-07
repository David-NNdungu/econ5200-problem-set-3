"""Difference-in-differences toolkit extending the Lab 11 helpers."""
from __future__ import annotations

import numpy as np
import pandas as pd

NEVER = 10 ** 9      # the cohort of a never-treated unit: later than any period


def two_by_two(df: pd.DataFrame, outcome: str, treated: str, post: str) -> float:
    """The canonical 2x2: difference of differences of the four group means."""
    g = df.groupby([treated, post])[outcome].mean()
    return (g[1, 1] - g[1, 0]) - (g[0, 1] - g[0, 0])


def att_by_cohort_period(df: pd.DataFrame, time: str, outcome: str,
                         cohort: str) -> pd.DataFrame:
    """ATT(g, t) for every cohort g and period t >= g.

    Controls are units NOT YET treated at t, never units already treated.
    The baseline is period g - 1, the last period before cohort g is treated.
    Returns one row per (g, t): the event time e = t - g, the estimate, and
    the number of treated units it rests on.
    """
    out = []
    cohorts = sorted(c for c in df[cohort].unique() if c < NEVER)
    for g in cohorts:
        tr = df[df[cohort] == g]
        for t in sorted(df.loc[df[time] >= g, time].unique()):
            co = df[df[cohort] > t]              # not yet treated at t
            if co.empty or (tr[time] == g - 1).sum() == 0:
                continue                         # no control left, or no baseline period
            d_tr = (tr.loc[tr[time] == t, outcome].mean()
                    - tr.loc[tr[time] == g - 1, outcome].mean())
            d_co = (co.loc[co[time] == t, outcome].mean()
                    - co.loc[co[time] == g - 1, outcome].mean())
            out.append({"g": g, "t": t, "e": t - g,
                        "att": d_tr - d_co, "n": int((tr[time] == t).sum())})
    return pd.DataFrame(out)


def overall_att(cells: pd.DataFrame) -> float:
    """Size-weighted average of the ATT(g, t) cells."""
    return float(np.average(cells["att"], weights=cells["n"]))


def event_study(cells: pd.DataFrame) -> pd.DataFrame:
    """Average the ATT(g, t) cells by event time e = t - g, weighted by size.

    Negative e would be pre-treatment periods. They are a diagnostic, not a
    test: estimates near zero are consistent with parallel trends and do not
    establish it.
    """
    rows = []
    for e, group in cells.groupby("e"):
        rows.append({"e": e, "att": np.average(group["att"], weights=group["n"])})
    return pd.DataFrame(rows)


def cluster_se_ratio(fit_iid, fit_clustered, param: str) -> float:
    """How many times larger the clustered standard error is than the iid one."""
    return float(fit_clustered.bse[param] / fit_iid.bse[param])


def clustered_inference(
    data: pd.DataFrame, formula: str, term: str, county: str, board: str
) -> pd.DataFrame:
    """Report iid, county-clustered and board-clustered inference on the same OLS fit."""
    import statsmodels.formula.api as smf

    model = smf.ols(formula, data=data, missing="raise")
    fits = {"Default": model.fit()}
    for label, group in [("County", county), ("Board", board)]:
        fits[label] = model.fit(
            cov_type="cluster", cov_kwds={"groups": data[group]}, use_t=True
        )
    return pd.DataFrame([
        {"inference": label, "estimate": fit.params[term],
         "se": fit.bse[term], "p": fit.pvalues[term]}
        for label, fit in fits.items()
    ]).set_index("inference")


def wild_cluster_bootstrap(
    data: pd.DataFrame, formula: str, term: str, cluster: str
) -> dict[str, float | int]:
    """Enumerate the restricted two-sided wild cluster bootstrap for a single term."""
    from itertools import product

    import statsmodels.api as sm
    import statsmodels.formula.api as smf

    model = smf.ols(formula, data=data, missing="raise")
    x = model.exog
    j = model.exog_names.index(term)
    codes, clusters = pd.factorize(data[cluster])
    if len(clusters) < 2 or (codes < 0).any():
        raise ValueError("At least two nonmissing clusters are required.")
    fit_options = {
        "cov_type": "cluster", "cov_kwds": {"groups": codes}, "use_t": True
    }
    unrestricted = model.fit(**fit_options)
    observed = float(unrestricted.tvalues[term])
    restricted = sm.OLS(model.endog, np.delete(x, j, axis=1)).fit()
    fitted, residuals = restricted.fittedvalues, restricted.resid

    t_star = []
    for signs in product((-1, 1), repeat=len(clusters)):
        y_star = fitted + np.asarray(signs)[codes] * residuals
        t_star.append(sm.OLS(y_star, x).fit(**fit_options).tvalues[j])

    magnitudes = np.abs(t_star)
    threshold = abs(observed)
    # Count numerical ties, including the all-positive and all-negative draws.
    extreme = (magnitudes > threshold) | np.isclose(
        magnitudes, threshold, rtol=1e-10, atol=1e-12
    )
    return {"t": observed, "cluster_p": float(unrestricted.pvalues[term]),
            "bootstrap_p": float(extreme.mean()), "vectors": len(t_star),
            "extreme": int(extreme.sum())}


if __name__ == "__main__":
    toy = pd.DataFrame({"treated": [0, 0, 1, 1], "post": [0, 1, 0, 1],
                        "y": [1, 2, 4, 7]})
    assert np.isclose(two_by_two(toy, "y", "treated", "post"), 2)
    print("Toolkit smoke test passed.")