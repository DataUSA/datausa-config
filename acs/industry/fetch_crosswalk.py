import pprint
import sys, csv, click, hashlib
import pandas as pd

@click.command()
@click.argument('tbl', type=str, default="B24030")
@click.argument('estimate', type=str, default='3')
@click.option('--gender/--no-gender', default=True)
def fetch_crosswalk(tbl, estimate, gender):
    acs = pd.read_json('http://api.census.gov/data/2013/acs{}/variables.json'.format(estimate))
    col = 0
    desc_offset = 2 if gender else 1
    lookup = {}
    current = {0:0,1:0,2:0}
    prev_depth = None
    while True:
        col += 1
        zfilled_col = str(col).zfill(3)
        try:
            row = acs.ix['{}_{}E'.format(tbl, zfilled_col)]
        except:
            break
        desc = row['variables']['label']
        desc = desc.split("!!")
        if len(desc) < desc_offset or "Total:" in desc or "Female:" in desc: continue
        depth = len(desc) - desc_offset
        for d in current.keys():
            if d > depth: current[d] = 0
        if prev_depth is not None and not prev_depth < depth:
            current[depth] += 1
        if depth == 0:
            lookup["{}".format(str(current[0]).zfill(2))] = ["{}".format(str(current[0]).zfill(2)), '{}_{}'.format(tbl, zfilled_col), depth, desc[-1]]
            lookup["{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2))] = ["{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2)), '{}_{}a'.format(tbl, zfilled_col), depth, desc[-1]]
            lookup["{}{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2), str(current[2]).zfill(2))] = ["{}{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2), str(current[2]).zfill(2)), '{}_{}b'.format(tbl, zfilled_col), depth, desc[-1]]
        if depth == 1:
            lookup["{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2))] = ["{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2)), '{}_{}'.format(tbl, zfilled_col), depth, desc[-1]]
            lookup["{}{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2), str(current[2]).zfill(2))] = ["{}{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2), str(current[2]).zfill(2)), '{}_{}a'.format(tbl, zfilled_col), depth, desc[-1]]
        if depth == 2:
            lookup["{}{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2), str(current[2]).zfill(2))] = ["{}{}{}".format(str(current[0]).zfill(2), str(current[1]).zfill(2), str(current[2]).zfill(2)), '{}_{}'.format(tbl, zfilled_col), depth, desc[-1]]
        
        # pprint.pprint(lookup)
        # print lookup
        # raw_input('')
        prev_depth = depth
        
    if lookup.values():
        with open('acs_{}year_{}_crosswalk.csv'.format(estimate, tbl), 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['acs_ind','col', 'depth', 'name'])
            csvwriter.writerows(sorted(lookup.values(), key=lambda x: x[0]))
    else:
        print 'NO DATA FOUND'

if __name__ == '__main__':
    fetch_crosswalk()
