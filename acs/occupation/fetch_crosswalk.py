import pprint
import sys, csv, click, hashlib
import pandas as pd

@click.command()
@click.argument('tbl', type=str, default="B24010")
@click.argument('estimate', type=str, default='3')
@click.option('--gender/--no-gender', default=True)
def fetch_crosswalk(tbl, estimate, gender):
    # acs = pd.read_json('http://api.census.gov/data/2013/acs{}/variables.json'.format(estimate))
    acs = pd.read_json('/Users/alexandersimoes/Downloads/variables.json'.format(estimate))
    col = 0
    desc_offset = 2 if gender else 1
    lookup = {}
    current = [0,0,0,0,0]
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
        for di, d in enumerate(current):
            if di > depth: current[di] = 0
        if prev_depth is not None and not prev_depth < depth:
            current[depth] += 1
        
        col_letters = ['', 'a','b','c','d','e']
        col_letter_i = -1
        for di, d in enumerate(current):
            if di >= depth:
                col_letter_i += 1
                new_id = "".join(['{0:02d}'.format(x) for x in current[:di+1]])
                # print di, new_id
                lookup[new_id] = [new_id, '{}_{}{}'.format(tbl, zfilled_col, col_letters[col_letter_i]), di, desc[-1]]
                
        # pprint.pprint(lookup)
        prev_depth = depth
        
    if lookup.values():
        with open('acs_{}year_{}_crosswalk.csv'.format(estimate, tbl), 'w') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['id','col', 'depth', 'name'])
            csvwriter.writerows(sorted(lookup.values(), key=lambda x: x[0]))
    else:
        print 'NO DATA FOUND'

if __name__ == '__main__':
    fetch_crosswalk()
