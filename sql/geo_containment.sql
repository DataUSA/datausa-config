-- Based on https://github.com/censusreporter/census-postgres-scripts from Census Reporter

-- Init w/ table creation
CREATE SCHEMA IF NOT EXISTS attrs;
DROP TABLE IF EXISTS attrs.geo_containment;
CREATE TABLE attrs.geo_containment (
    child_geoid varchar(40),
    parent_geoid varchar(40),
    percent_covered real
);

-- Places (160) in Counties (050)
INSERT INTO attrs.geo_containment (
    SELECT
        '16000US' || place.geoid AS child_geoid,
        '05000US' || county.geoid AS parent_geoid,
        ST_Area(ST_Intersection(place.geom,county.geom))/ST_Area(place.geom)*100 as percent_covered
    FROM tiger2013.place
    JOIN tiger2013.county ON ST_Intersects(place.geom, county.geom)
    WHERE
        ST_Area(ST_Intersection(place.geom,county.geom))/ST_Area(place.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(place.geom,county.geom)) DESC
);

-- Zip Codes (860) in Counties (050)
INSERT INTO attrs.geo_containment (
    SELECT
        '86000US' || zcta5.geoid10 AS child_geoid,
        '05000US' || county.geoid AS parent_geoid,
        ST_Area(ST_Intersection(zcta5.geom,county.geom))/ST_Area(zcta5.geom)*100 as percent_covered
    FROM tiger2013.zcta5
    JOIN tiger2013.county ON ST_Intersects(zcta5.geom, county.geom)
    WHERE
        ST_IsValid(zcta5.geom) AND
        ST_Area(ST_Intersection(zcta5.geom,county.geom))/ST_Area(zcta5.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(zcta5.geom,county.geom)) DESC
);

-- Places (160) in CBSA (310)
INSERT INTO attrs.geo_containment (
    SELECT
        '16000US' || place.geoid AS child_geoid,
        '31000US' || cbsa.geoid AS parent_geoid,
        ST_Area(ST_Intersection(place.geom,cbsa.geom))/ST_Area(place.geom)*100 as percent_covered
    FROM tiger2013.place
    JOIN tiger2013.cbsa ON ST_Intersects(place.geom, cbsa.geom)
    WHERE
        ST_IsValid(place.geom) AND
        ST_Area(ST_Intersection(place.geom,cbsa.geom))/ST_Area(place.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(place.geom,cbsa.geom)) DESC
);

-- ZCTA5s (860) in CBSA (310)
INSERT INTO attrs.geo_containment (
    SELECT
        '86000US' || zcta5.geoid10 AS child_geoid,
        '31000US' || cbsa.geoid AS parent_geoid,
        ST_Area(ST_Intersection(zcta5.geom,cbsa.geom))/ST_Area(zcta5.geom)*100 as percent_covered
    FROM tiger2013.zcta5
    JOIN tiger2013.cbsa ON ST_Intersects(zcta5.geom, cbsa.geom)
    WHERE
        ST_IsValid(zcta5.geom) AND
        ST_Area(ST_Intersection(zcta5.geom,cbsa.geom))/ST_Area(zcta5.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(zcta5.geom,cbsa.geom)) DESC
);

-- ZCTA5s (860) in States (040)
INSERT INTO attrs.geo_containment (
    SELECT
        '86000US' || zcta5.geoid10 AS child_geoid,
        '04000US' || state.geoid AS parent_geoid,
        ST_Area(ST_Intersection(zcta5.geom,state.geom))/ST_Area(zcta5.geom)*100 as percent_covered
    FROM tiger2013.zcta5
    JOIN tiger2013.state ON ST_Intersects(zcta5.geom, state.geom)
    WHERE
        ST_IsValid(zcta5.geom) AND
        ST_Area(ST_Intersection(zcta5.geom,state.geom))/ST_Area(zcta5.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(zcta5.geom,state.geom)) DESC
);

-- CBSAs (310) in States (040)
INSERT INTO attrs.geo_containment (
    SELECT
        '31000US' || cbsa.geoid AS child_geoid,
        '04000US' || state.geoid AS parent_geoid,
        ST_Area(ST_Intersection(cbsa.geom,state.geom))/ST_Area(cbsa.geom)*100 as percent_covered
    FROM tiger2013.cbsa
    JOIN tiger2013.state ON ST_Intersects(cbsa.geom, state.geom)
    WHERE
        ST_IsValid(cbsa.geom) AND
        ST_Area(ST_Intersection(cbsa.geom,state.geom))/ST_Area(cbsa.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(cbsa.geom,state.geom)) DESC
);

-- Tracts (140) in Places (160)
INSERT INTO attrs.geo_containment (
    SELECT
        '14000US' || tract.geoid AS child_geoid,
        '16000US' || place.geoid AS parent_geoid,
        ST_Area(ST_Intersection(tract.geom,place.geom))/ST_Area(tract.geom)*100 as percent_covered
    FROM tiger2013.tract
    JOIN tiger2013.place ON ST_Intersects(tract.geom, place.geom)
    WHERE
        ST_IsValid(tract.geom) AND
        ST_Area(ST_Intersection(tract.geom,place.geom))/ST_Area(tract.geom) > 0
    ORDER BY
        child_geoid ASC,
        ST_Area(ST_Intersection(tract.geom,place.geom)) DESC
);

-- Create indicies after all data has been inserted
CREATE INDEX attrs_geo_containment_idx_child_geoid ON attrs.geo_containment (child_geoid);
CREATE INDEX attrs_geo_containment_idx_parent_geoid ON attrs.geo_containment (parent_geoid);
