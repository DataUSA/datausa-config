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
