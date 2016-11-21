table_name = 'attrs.crosswalk_geo_containment'
print '''
CREATE TABLE {} (
    child_geoid varchar(40),
    parent_geoid varchar(40),
    percent_covered real,
    area_covered real
);\n'''.format(table_name)


# list of child/parent
containments = [
    ("160", "040"),
    ("160", "050"),
    ("160", "310"),
    ("160", "795"),

    ("140", "160"),

    ("050", "040"),
    ("050", "160"),
    ("050", "310"),
    ("050", "795"),

    ("310", "040"),
    ("310", "050"),
    ("310", "795"),
    ("310", "160"),

    ("795", "040"),
    ("795", "050"),
    ("795", "160"),
    ("795", "310"),

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
    child_gid_name = "geoid" if child_level != "795" else "geoid10"
    parent_gid_name = "geoid" if parent_level != "795" else "geoid10"
    child_name = name_map[child_level]
    parent_name = name_map[parent_level]
    sql = '''INSERT INTO {4} (
        SELECT
            '{5}00US' || {0}.{2} AS child_geoid,
            '{6}00US' || {1}.{3} AS parent_geoid,
            ST_Area(ST_Intersection({0}.geom,{1}.geom))/ST_Area({0}.geom)*100 as percent_covered,
            ST_Area(ST_Intersection({0}.geom,{1}.geom)) as area_covered
        FROM tiger2013.{0}
        JOIN tiger2013.{1} ON ST_Intersects({0}.geom, {1}.geom)
        WHERE ST_Area(ST_Intersection({0}.geom,{1}.geom))/ST_Area({0}.geom) > 0
    );'''.format(child_name, parent_name, child_gid_name, parent_gid_name, table_name, child_level, parent_level)
    return sql


# '''
# INSERT INTO attrs.geo_crosswalker(
# select distinct id as geo_a, '01000US' geo_b
# FROM attrs.geo_names
# WHERE id LIKE '795%' AND ID not in (select distinct geo_a from attrs.geo_crosswalker))
# '''

# identity rows for geo crosswalk joins
def all_levels_us_sql(table_name):
    sql = '''
        INSERT INTO {0} (
        select distinct child_geoid, '01000US' parent_geoid,
                        100 as percent_covered, NULL::real as area_covered
        FROM {0}
        WHERE child_geoid NOT LIKE '140%' and child_geoid NOT LIKE '01000US'
    );
    '''
    return sql.format(table_name)

def ident_sql(table_name):
    sql = '''INSERT INTO {0} (
        select distinct child_geoid, child_geoid as parent_geoid,
                        NULL::real as percent_covered, NULL::real as area_covered
        FROM {0}
    );
    INSERT INTO {0} (child_geoid, parent_geoid, percent_covered, area_covered) VALUES ('01000US', '01000US', NULL, NULL);
    '''
    return sql.format(table_name)

for parent, child in containments:
    print gen_sql(parent, child)

print all_levels_us_sql(table_name)
print ident_sql(table_name)

table_name_no_dot = table_name.replace(".", "_")
print "CREATE INDEX {}_idx_child_geoid ON {} (child_geoid);".format(table_name_no_dot, table_name)
print "CREATE INDEX {}_idx_parent_geoid ON {} (parent_geoid);".format(table_name_no_dot, table_name)
