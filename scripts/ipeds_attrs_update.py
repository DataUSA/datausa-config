import requests
import pandas as pd

headers = { 'User-Agent': 'DataUSA Client'}

r = requests.get('https://api.datausa.io/attrs/university', headers=headers).json()
headers = r['headers']
uid_idx = headers.index("id")
data = r['data']

unids = [d[uid_idx] for d in data]

df = pd.read_csv("/tmp/hd2015.csv") # path to latest hd file from ipeds


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
}, inplace=True)
df['id'] = df['id'].astype(str)

df = df[~df.id.isin(unids)].copy()

df.loc[df.state.isnull(), 'state'] = 'XX'
df.loc[df.county.isnull(), 'county'] = 'XXXXX'
df.loc[df.msa.isnull(), 'msa'] = 'XXXXX'

df.state = "04000US" + df.state.astype(str).str.zfill(2)
df.state = "05000US" + df.county.astype(str).str.zfill(5)
df.state = "31000US" + df.msa.astype(str).str.zfill(5)

df['last_year'] = 2015
df = df[["last_year", "id", "name", "state", "county", "msa", "category", "sector", "lat", "lng"]]
to_import = True
if to_import:
    from sqlalchemy import create_engine
    import os
    DATAUSA_PW = os.environ.get('DATAUSA_DB_PW')
    DATAUSA_DB = os.environ.get('DATAUSA_DB_NAME')
    DATAUSA_HOST = os.environ.get('DATAUSA_DB_HOST')
    dbpath = 'postgres://postgres:{}@{}:5432/{}'.format(DATAUSA_PW, DATAUSA_HOST, DATAUSA_DB)
    engine = create_engine(dbpath, echo=False)
    df.to_sql(name='university', schema="attrs", con=engine, if_exists='append', index=False)
    print "import complete"
