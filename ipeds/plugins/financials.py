import pandas as pd
from carnegie import get_dfs


def compute_quintiles(df, **kwargs):
    # master_df = pd.DataFrame()
    univ_df, linkage_df = get_dfs()
    # raise Exception(linkage_df)
    df.university = df.university.astype(str)
    df = df[df.university_level == 2].copy()
    df = df.merge(univ_df, on="university", how="left")
    del df["university_level"]
    df = df.merge(linkage_df, on="carnegie", how="left")
    df.university = df.uniq_ids

    df = df.groupby(["year", "university", "university_level"]).endowment_value_fiscal_year_end.quantile([0.2, 0.4, 0.6, 0.8, 1])
    df = df.reset_index()

    df.university_level = df.university_level.astype(int)
    df.rename(columns={"level_3": "endowment_quintile", "endowment_value_fiscal_year_end": "endowment_quintile_value"}, inplace=True)

    return df


def research_ranks(df, **kwargs):
    univ_df, linkage_df = get_dfs()

    df = df.reset_index()
    df = df.merge(univ_df, on="university", how="left")
    df['research_rank'] = df["research_total"].rank(method="dense", ascending=False)
    df['research_rank_pct'] = df["research_total"].rank(method="dense", ascending=False, pct=True)

    df['research_rank_carnegie'] = df.groupby("carnegie")["research_total"].rank(method="dense", ascending=False)
    df['research_rank_carnegie_pct'] = df.groupby("carnegie")["research_total"].rank(method="dense", ascending=False, pct=True)

    del df['carnegie']
    return df
