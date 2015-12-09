table_name = 'attrs.new_geo_containment'
print '''
CREATE TABLE {} (
    child_geoid varchar(40),
    parent_geoid varchar(40),
    percent_covered real,
    area_covered real
);\n'''.format(table_name)


# list of child/parent
containments = [
    ("050", "310"),
    ("050", "795"),
    ("140", "160"),
    ("160", "050"),
    ("160", "310"),
    ("160", "795"),
    ("310", "040"),
    ("310", "795"),
]

# --  (160) in Counties (050)

name_map = {
    "160": "place",
    "050": "county",
    "310": "cbsa",
    "795": "puma",
    "140": "tract",
    "040": "state",
}

def gen_sql(child_level, parent_level):
    child_gid_name = "geoid" if parent_level != "795" else "geoid10"
    parent_gid_name = "geoid" if parent_level != "795" else "geoid10"
    child_name = name_map[child_level]
    parent_name = name_map[parent_level]
    sql = '''INSERT INTO {4} (
        SELECT
            '16000US' || {0}.{2} AS child_geoid,
            '05000US' || {1}.{3} AS parent_geoid,
            ST_Area(ST_Intersection({0}.geom,{1}.geom))/ST_Area({0}.geom)*100 as percent_covered,
            ST_Area(ST_Intersection({0}.geom,{1}.geom)) as area_covered
        FROM tiger2013.{0}
        JOIN tiger2013.{1} ON ST_Intersects({0}.geom, {1}.geom)
        WHERE ST_Area(ST_Intersection({0}.geom,{1}.geom))/ST_Area({0}.geom) > 0
    );'''.format(child_name, parent_name, child_gid_name, parent_gid_name, table_name)
    return sql

for parent, child in containments:
    print gen_sql(parent, child)
