def compute_yields(df, **kwargs):
    df['yield_total'] = df.admissions_enrolled_total / df.admissions_total
    df['yield_men'] = df.admissions_enrolled_men / df.admissions_men
    df['yield_women'] = df.admissions_enrolled_women / df.admissions_women
    return df
