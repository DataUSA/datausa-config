import pandas as pd

df = pd.read_csv("crosswalk_geo_containment.csv")

my_connections = {}

headers = [str(x) for x in df.columns]
for row in list(df.itertuples()):
    my_set = frozenset([row.parent_geoid, row.child_geoid])
    if not my_set in my_connections:
        my_connections[my_set] = True

import csv
with open('eggs.csv', 'wb') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=',',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["geo_a", "geo_b"])
    for row in my_connections.keys():
        my_row = list(row)
        if len(my_row) == 1:
            my_row = 2*my_row
        spamwriter.writerow(my_row)

    
