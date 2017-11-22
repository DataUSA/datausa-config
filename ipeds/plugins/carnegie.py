import os
from sqlalchemy import create_engine
import pandas as pd

DATAUSA_PW = os.environ.get('DATAUSA_DB_PW')
DATAUSA_DB = os.environ.get('DATAUSA_DB_NAME')
DATAUSA_HOST = os.environ.get('DATAUSA_DB_HOST')

if not DATAUSA_HOST:
    raise Exception("Make sure DATAUSA_DB_HOST environment variable is set")

db_path = 'postgres://postgres:{}@{}:5432/{}'.format(DATAUSA_PW, DATAUSA_HOST, DATAUSA_DB)
engine = create_engine(db_path, echo=False)
university_to_carnegie = None
carnegie_df = pd.read_sql("SELECT id as carnegie, parent, depth, children FROM attrs.carnegie WHERE depth=0", engine)
univ_df = pd.read_sql("SELECT id as university, carnegie FROM attrs.university WHERE carnegie IS NOT NULL", engine)
carnegies = []
depths = []
uniq_ids = []
for carnegie, parent, depth, children in carnegie_df.values:
    for child in children:
        carnegies += [child, child]
        depths += [1, 0]
        uniq_ids += [child, carnegie]

linkage_df = pd.DataFrame({"carnegie": carnegies, "university_level": depths, "uniq_ids": uniq_ids})


def get_fn(fn_name):
    if fn_name == "mode":
        return lambda x: x.mode().iloc[0]
    return getattr(pd.Series, fn_name)


def add_rows(orig_df, **kwargs):

    orig_idx = [x for x in orig_df.index.names if x]
    orig_cols = [x for x in orig_df.columns]
    if len(orig_idx) > 0:
        orig_df = orig_df.reset_index()
    orig_df.university = orig_df.university.astype(str)
    extra_rows_df = orig_df.merge(univ_df, on="university", how="left")
    extra_rows_df = extra_rows_df.merge(linkage_df, on="carnegie", how="left")

    extra_rows_df.university = extra_rows_df.uniq_ids
    extra_rows_df.drop(columns=["uniq_ids", "carnegie"], axis=1, inplace=True)
    pk = kwargs["pk"] if "pk" in kwargs else ["year", "university"]
    default_agg = "median" if "default_agg" not in kwargs else kwargs["default_agg"]
    aggs = {col: default_agg for col in extra_rows_df.columns if col not in pk}
    if "aggs_dict" in kwargs:
        aggs.update(kwargs["aggs_dict"])

    aggs = {col: get_fn(fn) for col, fn in aggs.items()}
    # take the median of all values, by default otherwise apply the desired function
    # we need to do a little magic to get the mode reducer to work with cols that
    # may have all NaNs, so first we just gather all values then apply the mode fn
    extra_rows_df = extra_rows_df.groupby(pk).agg(aggs).reset_index()

    new_df = orig_df.append(extra_rows_df)
    new_df.loc[new_df.university_level.isnull(), 'university_level'] = 2
    new_df.university_level = new_df.university_level.astype(int)
    if "restore_index" in kwargs and kwargs["restore_index"]:
        new_df = new_df.set_index(orig_idx)
    if "index" in new_df.columns and "index" not in orig_cols:
        del new_df["index"]
    return new_df


# print(add_rows(pd.DataFrame({"year": [2016, 2016], "university": ["211440", "166027"], "value": [0, 10]})))
