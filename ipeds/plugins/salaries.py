def ipeds_occ(df, **kwargs):
    df = df.melt(id_vars=['year', 'university'])
    df['ipeds_occ'] = df.variable.str.replace(r"SANIN|SANIT", "")
    df.loc[df.variable.str.startswith("SANIN"), 'kind'] = 'num_noninstructional_staff'
    df.loc[df.variable.str.startswith("SANIT"), 'kind'] = 'outlays_noninstructional_staff'
    df = df.pivot_table(index=['year', 'university', 'ipeds_occ'], columns='kind', values='value')
    return df.reset_index()


def ipeds_is(df, **kwargs):
    df = df.melt(id_vars=['year', 'university', 'academic_rank'])

    df.loc[df.variable.str.endswith("_men"), 'sex'] = 1
    df.loc[df.variable.str.endswith("_women"), 'sex'] = 2

    df.sex = df.sex.astype(int)
    df.variable = df.variable.str.replace(r"(_men|_women)$", "")
    df = df.pivot_table(index=['year', 'university', 'academic_rank', 'sex'],
                        columns='variable', values='value')
    return df.reset_index()
