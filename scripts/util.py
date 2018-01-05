import os

import pandas as pd
import requests
from sqlalchemy import create_engine


def datafold(data):
    return [dict(zip(data["headers"], d)) for d in data["data"]]


def university_attrs_df(usecols=None, converters=None):
    headers = {'User-Agent': 'DataUSA Client'}
    r = requests.get('https://university-api.datausa.io/attrs/university', headers=headers).json()
    df = pd.DataFrame(datafold(r))
    if usecols:
        df = df[usecols]
    if converters:
        for col, func in converters.items():
            df[col] = df[col].astype(func)
    if "msa" in df.columns:
        # clean msa strs
        df.msa = df.msa.str.replace("\.0$", "")
    return df


def import_to_db(master_df, table_name, schema="attrs", dtype=None):
    DATAUSA_PW = os.environ.get('DATAUSA_DB_PW')
    DATAUSA_DB = os.environ.get('DATAUSA_DB_NAME')
    DATAUSA_HOST = os.environ.get('DATAUSA_DB_HOST')
    dbpath = 'postgres://postgres:{}@{}:5432/{}'.format(DATAUSA_PW, DATAUSA_HOST, DATAUSA_DB)
    engine = create_engine(dbpath, echo=False)
    print("Importing to database...")
    master_df.to_sql(name=table_name, schema=schema, con=engine, if_exists='fail', index=False, dtype=dtype)
    print("Import complete!")
