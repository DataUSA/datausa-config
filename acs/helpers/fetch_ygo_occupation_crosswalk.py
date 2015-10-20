import sys, csv, click
import pandas as pd

@click.command()
@click.argument('tbl', type=str)
@click.argument('estimate', type=str, default='5')
def fetch_crosswalk(tbl, estimate):
    acs = pd.read_json('http://api.census.gov/data/2013/acs{}/variables.json'.format(estimate))
    col = 0
    lookup = {}
    while True:
        col += 1
        zfilled_col = str(col).zfill(3)
        try:
            row = acs.ix['{}_{}E'.format(tbl, zfilled_col)]
        except:
            break
        desc = row['variables']['label']
        desc = desc.split("!!")
        if len(desc) < 2:
            continue
        depth = len(desc) - 2
        if desc[-1] not in lookup:
            lookup[desc[-1]] = ['{}_{}E'.format(tbl, zfilled_col), depth, desc[-1]]
    if lookup.values():
        with open('acs_{}year_{}_crosswalk.csv'.format(estimate, tbl), 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerows(sorted(lookup.values(), key=lambda x: x[0]))
    else:
        print 'NO DATA FOUND'

if __name__ == '__main__':
    fetch_crosswalk()