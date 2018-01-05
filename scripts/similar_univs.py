# coding: utf-8
import logging
import pandas as pd
from sklearn import preprocessing
from sklearn.manifold import TSNE
from util import university_attrs_df, import_to_db

logging.info("1. Loading CIP course data...")
df = pd.read_csv("~/Downloads/c2015_a/c2015_a.csv", converters={"CIPCODE": str, "UNITID": str})
df = df[df.CIPCODE != "99"].copy()  # filter out totals
df.CIPCODE = df.CIPCODE.str.slice(0, 2)

num_cips = df.CIPCODE.nunique()
logging.info("Working with {} CIP codes".format(num_cips))
df.rename(columns={"UNITID": "university"}, inplace=True)
df = df.pivot_table(index=["university"], columns=["CIPCODE"], values="CTOTALT").reset_index()

logging.info("2. Loading university attribute data...")

attrs_df = university_attrs_df(usecols=["id", "carnegie", "carnegie_parent", "status"], converters={"id": str})
logging.info("3. Loading university admissions data...")
adm_df = pd.read_csv("~/Downloads/adm2015.csv", converters={"UNITID": str})
adm_df['admit_rate'] = adm_df.ADMSSN / adm_df.APPLCN
adm_df = adm_df[["UNITID", "admit_rate"]]
adm_df.rename(columns={"UNITID": "university"}, inplace=True)
attrs_df.rename(columns={"id": "university"}, inplace=True)

logging.info("4. Merging dataframes...")

df = df.merge(attrs_df, how='left', on='university')
df = df.merge(adm_df, how='left', on='university')

carnegie_parents = df[df.status != 'D'].carnegie_parent.unique()
assert None not in carnegie_parents
del df["status"]

master_df = pd.DataFrame()

for cgroup in carnegie_parents:
    subset_df = df[df.carnegie_parent == cgroup]
    del subset_df["carnegie_parent"]
    logging.info("5. Filling zeroes and scaling...")
    subset_df = subset_df.set_index(["university"])
    subset_df = subset_df.fillna(0)
    min_max_scaler = preprocessing.MinMaxScaler()
    subset_df = pd.DataFrame(min_max_scaler.fit_transform(subset_df), columns=subset_df.columns, index=subset_df.index)

    logging.info("6. Performnig t-SNE")

    Y = TSNE(n_components=2,
             method='barnes_hut',
             perplexity=5,
             # angle=0.9,
             verbose=1,
             n_iter=5000).fit_transform(subset_df)

    output = pd.DataFrame(Y, index=subset_df.index).reset_index()
    output.columns = ['university', 'x', 'y']
    attrs_df = university_attrs_df(usecols=["id", "carnegie", "name", "sector", "carnegie_parent"], converters={"id": str})
    output = output.merge(attrs_df, how='left', left_on='university', right_on='id')
    print(output.head())
    # output.to_json("output_{}.json".format(cgroup), orient="records")
    master_df = pd.concat([master_df, output])

import_to_db(master_df, "similar_universities")
