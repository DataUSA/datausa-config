import requests
import pandas as pd
from slugify import slugify
from sqlalchemy.dialects import postgresql
from sqlalchemy.types import String
from util import datafold
import os

DEBUG = os.environ.get("DEBUG", "True") not in ["0", "false", "False"]


def clean_cip(x):
    return x.split(".")[0].zfill(2)


def stem_map():
    url = "C2016_A.zip" if DEBUG else "https://nces.ed.gov/ipeds/datacenter/data/C2016_A.zip"
    df = pd.read_csv(url, compression="infer", converters={"UNITID": str})
    df.rename(columns={"CIPCODE": "cip", "UNITID": "id", "CTOTALT": "total"}, inplace=True)
    stem_list = ["01", "02", "11", "14", "15", "25", "26", "27", "40", "41", "51"]
    df.cip = df.cip.astype(str).apply(clean_cip)
    df.loc[df.cip.isin(stem_list) & df.total > 0, 'is_stem'] = 1
    return df.groupby("id").agg({"is_stem": pd.Series.sum}).reset_index()


def load_existing_data():
    headers = {'User-Agent': 'DataUSA Client'}
    r = requests.get('https://university-api.datausa.io/attrs/university', headers=headers).json()
    existing_df = pd.DataFrame(datafold(r))
    # clean msa strs
    existing_df.msa = existing_df.msa.str.replace("\.0$", "")
    return existing_df


def load_carnegies():
    headers = {'User-Agent': 'DataUSA Client'}
    r = requests.get('https://university-api.datausa.io/attrs/carnegie', headers=headers).json()
    df = pd.DataFrame(datafold(r))
    del df["children"]
    return df.rename(columns={"depth": "university_level", "parent": "carnegie_parent"})


def add_carnegies(master_df):
    cdf = load_carnegies()

    def my_mode(x):
        res = x.mode()
        if not res.empty:
            return res.iloc[0]
        return None

    delta_df = pd.DataFrame()
    for level in [0, 1]:
        carnegie_attr_df = cdf[cdf.university_level == level]
        pk = "carnegie" if level == 1 else "carnegie_parent"
        collapsed_df = master_df.groupby(pk).agg({
            "county": my_mode,
            "category": my_mode,
            "is_stem": my_mode,
            "sector": my_mode,
            "state": my_mode,
            "lat": pd.Series.mean,
            "lng": pd.Series.mean
        }).reset_index()
        collapsed_df.rename(columns={pk: "id"}, inplace=True)
        carnegie_attr_df = carnegie_attr_df.merge(collapsed_df, on="id", how="left")
        carnegie_attr_df['university_level'] = carnegie_attr_df.university_level.astype(int)

        new_rows = carnegie_attr_df.copy()
        delta_df = pd.concat([delta_df, new_rows])
    delta_df['status'] = 'CG'
    delta_df["url_name"] = delta_df.name.apply(slugify)

    return pd.concat([master_df, delta_df])


def load_new_data(opeid_only=False):
    url = "HD2016.zip" if DEBUG else "https://nces.ed.gov/ipeds/datacenter/data/HD2016.zip"
    df = pd.read_csv(url, compression="infer", converters={"UNITID": str, "CBSA": str, "C15BASIC": str})
    df.rename(columns={
        "UNITID": "id",
        "INSTNM": "name",
        "FIPS": "state",
        "COUNTYCD": "county",
        "CBSA": "msa",
        "WEBADDR": "url",
        "INSTCAT": "category",
        "SECTOR": "sector",
        "LONGITUD": "lng",
        "LATITUDE": "lat",
        "OPEID": "opeid",
        "ACT": "status",
        "C15BASIC": "carnegie"
    }, inplace=True)
    print(df.head())

    if not opeid_only:
        df["url_name"] = df.name.apply(slugify)
        df.loc[df.state.isnull(), 'state'] = 'XX'
        df.loc[df.county.isnull(), 'county'] = 'XXXXX'
        df.loc[df.msa.isnull(), 'msa'] = 'XXXXX'
        df.state = "04000US" + df.state.astype(str).str.zfill(2)
        df.county = "05000US" + df.county.astype(str).str.zfill(5)
        df.msa = "31000US" + df.msa.astype(str).str.zfill(5)

        stem_df = stem_map()
        df = df.merge(stem_df, how="left", on="id")
        df.loc[df.category.isnull(), 'category'] = -1
        df.status = df.status.str.strip().astype(unicode)
    df['last_year'] = 2016
    keys = ["last_year", "id", "name", "state", "county", "msa", "category", "sector", "lat", "lng", "is_stem", "status", "carnegie", "url", "url_name"] if not opeid_only else ["id", "opeid"]
    df = df[keys]

    return df


def carnegie_processing(my_df):
    my_df['university_level'] = 2
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

    for key, val in lookups.items():
        my_df.loc[my_df.carnegie.isin(map(str, val)), 'carnegie_parent'] = key

    return my_df


print("1. Loading existing data...")
existing_df = load_existing_data()

print("2. Loading new data...")
new_df = load_new_data()
# preserve meta information from existing DFs
edf_meta = existing_df[existing_df.id.isin(new_df.id)][["id", "image_link", "image_meta", "image_author", "keywords"]].copy()

new_df = new_df.merge(edf_meta, how="left", on="id")
print(new_df[new_df.id == "110662"])
print(edf_meta[edf_meta.id == "211440"].keywords)

# # old institutions for historical purposes
existing_df = existing_df[~existing_df.id.isin(new_df.id)].copy()
existing_df['status'] = 'D'
master_df = pd.concat([existing_df, new_df])

existing_df = None
new_df = None

print("3. Loading new OPEIDs...")
opeis = load_new_data(opeid_only=True)

print("4. Processing data...")
# merges in opeids
master_df = master_df.merge(opeis, how='left', on="id")
master_df.loc[master_df.is_stem.isnull(), 'is_stem'] = 0
master_df.loc[master_df.is_stem > 0, 'is_stem'] = 1
master_df.is_stem = master_df.is_stem.astype(int)
master_df.loc[master_df.category.isnull(), 'category'] = -1
# fix url names
master_df.loc[master_df.duplicated("url_name"), 'url_name'] = master_df.url_name + "-" + master_df.id.astype(str)
master_df['display_name'] = master_df.name

print("5. Post processing...")
master_df = carnegie_processing(master_df)


print(master_df.head())
print("6. Insert Carnegie Groupings...")
master_df = add_carnegies(master_df)

to_import = True
if to_import:
    from sqlalchemy import create_engine
    import os
    for col in master_df.columns:
        if col in ["name", "display_name", "url"]:
            master_df[col] = master_df[col].str.decode('utf8', 'ignore')
    DATAUSA_PW = os.environ.get('DATAUSA_DB_PW')
    DATAUSA_DB = os.environ.get('DATAUSA_DB_NAME')
    DATAUSA_HOST = os.environ.get('DATAUSA_DB_HOST')
    dbpath = 'postgres://postgres:{}@{}:5432/{}'.format(DATAUSA_PW, DATAUSA_HOST, DATAUSA_DB)
    engine = create_engine(dbpath, echo=False)
    print(master_df.dtypes)
    print("7. Importing to database...")
    master_df.to_sql(name='university_vtest2', schema="attrs", con=engine, if_exists='fail', index=False, dtype={"keywords": postgresql.ARRAY(String), "carnegie": String})
    print("Import complete!")
