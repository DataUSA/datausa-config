import numpy as np
import pandas as pd
import re


def transform_living(df, **kwargs):
    if "pk" not in kwargs or not kwargs["pk"]:
        raise Exception("Please specify a valid primary key")
    pk = kwargs["pk"]

    df = df.melt(id_vars=pk, value_name="num_in_living_arrangement")

    df.variable = df.variable.str.strip()
    df.loc[df.variable == "num_living_oncampus", "living_arrangement"] = "1"
    df.loc[df.variable == "num_living_offcampuswithfamily", "living_arrangement"] = "2"
    df.loc[df.variable == "num_living_offcampusnotwithfamily", "living_arrangement"] = "3"
    df.loc[df.variable == "num_living_unknown", "living_arrangement"] = "4"

    del df["variable"]
    return df


def transform_income_range(df, **kwargs):
    if "pk" not in kwargs or not kwargs["pk"]:
        raise Exception("Please specify a valid primary key")
    pk = kwargs["pk"]

    df = df.melt(id_vars=pk)

    df.variable = df.variable.str.strip()
    df.loc[df.variable.str.endswith("level_1"), "income_range"] = "1"
    df.loc[df.variable.str.endswith("level_2"), "income_range"] = "2"
    df.loc[df.variable.str.endswith("level_3"), "income_range"] = "3"
    df.loc[df.variable.str.endswith("level_4"), "income_range"] = "4"
    df.loc[df.variable.str.endswith("level_5"), "income_range"] = "5"
    df.variable = df.variable.str.slice(0, -8)
    df = pd.pivot_table(df, values="value", index=pk + ["income_range"], columns=["variable"], aggfunc=np.sum)

    columns_to_work_on = set([re.sub(r"_(public|private)", "", x) for x in df.columns])
    df = df.reset_index()
    for var in columns_to_work_on:
        var1 = "{}_public".format(var)
        var2 = "{}_private".format(var)
        assert df[df[var1].notnull() & df[var2].notnull()].empty
        df.loc[df[var1].notnull(), var] = df[var1]
        df.loc[df[var2].notnull(), var] = df[var2]
        df.drop(columns=[var1, var2], axis=1, inplace=True)
    # df = df.dropna(axis=0, how='all', subset=my_list)  # drop rows where are of the elements are nan

    return df


def transform_public_private(df, **kwargs):
    columns_to_work_on = ['avg_netprice_gos_aid']
    for var in columns_to_work_on:
        var1 = "{}_public".format(var)
        var2 = "{}_private".format(var)
        assert df[df[var1].notnull() & df[var2].notnull()].empty
        df.loc[df[var1].notnull(), var] = df[var1]
        df.loc[df[var2].notnull(), var] = df[var2]
        df.drop(columns=[var1, var2], axis=1, inplace=True)
    return df
