import pandas as pd

def clean(df, **kwargs):
    print(kwargs, "HELLO!")
    master_df = pd.DataFrame()
    for i in range(1, 4):
        target_names = ["num", "default_rate", "rate_type", "denom"]
        ids = ["{}_{}".format(name, i) for name in target_names]

        tmp_df = pd.melt(df, id_vars=["opeid"] + ids, value_vars=["year_{}".format(i)], value_name="year")
        tmp_df.rename(columns=dict(zip(ids, target_names)), inplace=True)
        del tmp_df["variable"]
        master_df = pd.concat([master_df, tmp_df])

    return master_df
