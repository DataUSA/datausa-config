CREATE TABLE geo_neighbors  AS (SELECT
	    '04000US' || s1.geoid AS geo,
	    '04000US' || s2.geoid AS neighbor
	FROM tiger2013.state s1
	JOIN tiger2013.state s2 on ST_Touches(s1.geom, s2.geom)
	WHERE s1.geoid != s2.geoid
UNION

SELECT
	    '05000US' || s1.geoid AS geo,
	    '05000US' || s2.geoid AS neighbor
	FROM tiger2013.county s1
	JOIN tiger2013.county s2 on ST_Touches(s1.geom, s2.geom)
	WHERE s1.geoid != s2.geoid

UNION

SELECT
	    '79500US' || s1.geoid10 AS geo,
	    '79500US' || s2.geoid10 AS neighbor
	FROM tiger2013.puma s1
	JOIN tiger2013.puma s2 on ST_Touches(s1.geom, s2.geom)
	WHERE s1.geoid10 != s2.geoid10
	
UNION

SELECT
	    '16000US' || s1.geoid AS geo,
	    '16000US' || s2.geoid AS neighbor
	FROM tiger2013.place s1
	JOIN tiger2013.place s2 on ST_Touches(s1.geom, s2.geom)
	WHERE s1.geoid != s2.geoid
UNION

SELECT
	    '31000US' || s1.geoid AS geo,
	    '31000US' || s2.geoid AS neighbor
	FROM tiger2013.cbsa s1
	JOIN tiger2013.cbsa s2 on ST_Touches(s1.geom, s2.geom)
	WHERE s1.geoid != s2.geoid
)