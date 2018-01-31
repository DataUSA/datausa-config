import pandas as pd
# import requests


def datafold(data):
    return [dict(zip(data["headers"], d)) for d in data["data"]]


def clean(df, **kwargs):
    master_df = pd.DataFrame()
    id_vars = ["opeid"] if "id_vars" not in kwargs else kwargs["id_vars"]
    for i in range(1, 4):
        target_names = ["num", "default_rate", "rate_type", "denom"]
        ids = ["{}_{}".format(name, i) for name in target_names]

        tmp_df = pd.melt(df, id_vars + ids, value_vars=["year_{}".format(i)], value_name="year")
        tmp_df.rename(columns=dict(zip(ids, target_names)), inplace=True)
        del tmp_df["variable"]
        master_df = pd.concat([master_df, tmp_df])
    return master_df


def map_to_carnegies(df, **kwargs):

    year = kwargs.get("year")
    attr_df = pd.read_csv("https://nces.ed.gov/ipeds/datacenter/data/HD{}.zip".format(year), converters={"OPEID": str}, compression='infer', usecols=["OPEID", "C15BASIC"])
    lookups = {
        "ASC": [1, 2, 3, 4, 5, 6, 7, 8, 9],
        "BAA": [14, 23],
        "BAC": [21, 22],
        "DOC": [15, 16, 17],
        "MAS": [18, 19, 20],
        "NAD": [-2],
        "SFI": [10, 11, 12, 13, 24, 25, 26, 27, 28, 29, 30, 31, 32],
        "TRI": [33]
    }
    attr_df.rename(columns={"OPEID": "opeid8", "C15BASIC": "carnegie"}, inplace=True)

    def lookup_c(c):
        for cp, clist in lookups.items():
            if int(str(c).strip()) in clist:
                return str(cp)
        raise Exception("INVALID CARNEGIE LOOKUP", c)

    df["opeid_level"] = 2

    attr_df["opeid"] = attr_df.opeid8.str.slice(0, 6)  # convert to opeid6
    attr_df['carnegie_parent'] = attr_df.carnegie.apply(lookup_c)

    df_c1 = df.merge(attr_df, on="opeid").groupby(["year", "carnegie", "rate_type"]).median()
    df_c1["opeid_level"] = 1
    df_c1 = df_c1.reset_index()
    df_c1.rename(columns={"carnegie": "opeid"}, inplace=True)

    df_c2 = df.merge(attr_df, on="opeid").groupby(["year", "carnegie_parent", "rate_type"]).median()

    del df_c2["carnegie"]
    df_c2["opeid_level"] = 0
    df_c2 = df_c2.reset_index()
    df_c2.rename(columns={"carnegie_parent": "opeid"}, inplace=True)
    result_df = pd.concat([df, df_c1, df_c2])
    return result_df
# map_to_carnegies(None, year=2016)
