import re
import numpy as np
import pandas as pd


def transform_grad_rate(df, **kwargs):
    df = df.set_index(["year", "university"])
    columns_to_work_on = set([re.sub(r"_(ba|2y)$", "", x) for x in df.columns])

    for var in columns_to_work_on:
        var1 = "{}_ba".format(var)
        var2 = "{}_2y".format(var)
        assert df[df[var1].notnull() & df[var2].notnull()].empty
        df.loc[df[var1].notnull(), var] = df[var1]
        df.loc[df[var2].notnull(), var] = df[var2]
        df.drop(columns=[var1, var2], axis=1, inplace=True)

    return df.reset_index()


def transform_grad_rate_race(df, **kwargs):
    first_pk = ["year", "university", "line", "SECTION", "COHORT", "chrtstat", "grtype"]

    if "pk" not in kwargs or not kwargs["pk"]:
        raise Exception("Please specify a valid primary key")
    pk = kwargs["pk"]

    df = df.melt(id_vars=first_pk, value_name="value")
    df = df[~df.variable.astype(str).str.endswith("_total")]
    df.loc[df.variable.str.endswith("_men"), "sex"] = "1"
    df.loc[df.variable.str.endswith("_women"), "sex"] = "2"
    df.loc[df.variable.str.contains("_asian_"), "ipeds_race"] = "asian"
    df.loc[df.variable.str.contains("_native_"), "ipeds_race"] = "native"
    df.loc[df.variable.str.contains("_black_"), "ipeds_race"] = "black"
    df.loc[df.variable.str.contains("_hispanic_"), "ipeds_race"] = "hispanic"
    df.loc[df.variable.str.contains("_hawaiian_"), "ipeds_race"] = "hawaiian"
    df.loc[df.variable.str.contains("_white_"), "ipeds_race"] = "white"
    df.loc[df.variable.str.contains("_multiracial_"), "ipeds_race"] = "multiracial"
    df.loc[df.variable.str.contains("_unknown_"), "ipeds_race"] = "unknown"
    df.loc[df.variable.str.contains("_nonresident_"), "ipeds_race"] = "nonresident"
    df.loc[df.chrtstat == 13, 'kind'] = 'num_finishers'
    df.loc[df.chrtstat == 12, 'kind'] = 'cohort_size'
    assert df[df.kind.isnull()].empty
    df.drop(columns=['SECTION', 'COHORT', 'chrtstat', 'grtype', 'line'], axis=1, inplace=True)
    df = pd.pivot_table(df, values='value', columns='kind', aggfunc=np.sum, index=pk)
    df = df.reset_index()
    df['grad_rate'] = df.num_finishers / df.cohort_size
    return df
