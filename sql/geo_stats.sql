-- county stats
CREATE TABLE stats.counties AS (SELECT 
a.id as geo,
(SELECT pos
	FROM 
	(SELECT geo, pop, rank()
		 OVER (PARTITION BY LEFT(geo, 3) ORDER BY pop DESC) AS 	pos FROM acs.yg
	WHERE geo like '05000' ||SUBSTR(a.id, 6, 4) || '%') as tmp
	WHERE geo = a.id) as stat_1,
(SELECT count(child_geoid) from attrs.geo_containment where parent_geoid = a.id and child_geoid LIKE '160%') as stat_2,
ARRAY(SELECT geo
FROM acs.yg WHERE geo in 
(SELECT child_geoid from attrs.geo_containment where parent_geoid = a.id and child_geoid LIKE '160%')
ORDER BY pop desc
LIMIT 3) as stat_3,
ARRAY(SELECT neighbor from attrs.geo_neighbors where geo = a.id) as stat_4
FROM attrs.geo_names a
WHERE id LIKE '05000US%')