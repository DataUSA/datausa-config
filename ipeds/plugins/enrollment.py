def transform_race_gender(df, **kwargs):
    if "pk" not in kwargs or not kwargs["pk"]:
        raise Exception("Please specify a valid primary key")
    pk = kwargs["pk"]

    df = df.melt(id_vars=pk, value_name="num_enrolled")

    df.variable = df.variable.str.strip()
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

    del df["variable"]
    return df
