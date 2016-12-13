-- First run:
-- 1. pg_dump -t attrs.ztest_university datausa --no-privileges -h postgres.datawheel.us -U postgres -W > /tmp/universities.sql
-- 2. psql < universities.sql
-- 3. Generate university_geo lookup table
-- pg_dump -t public.university_geo postgis_template --no-privileges -h postgres.datawheel.us -U postgres -W > /tmp/universities.sql
CREATE TABLE university_geo AS
SELECT u.id as university, '04000US' || state.geoid as geo
FROM tiger2015.state state, attrs.university u
WHERE ST_Intersects(state.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326))
UNION
(SELECT u.id as university, '05000US' || county.geoid as geo
FROM tiger2015.county county, attrs.university u
WHERE ST_Intersects(county.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
UNION
(SELECT u.id as university, '31000US' || cbsa.geoid as geo
FROM tiger2015.cbsa cbsa, attrs.university u
WHERE ST_Intersects(cbsa.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
UNION
(SELECT u.id as university, '16000US' || place.geoid as geo
FROM tiger2015.place place, attrs.university u
WHERE ST_Intersects(place.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
UNION
(SELECT u.id as university, '79500US' || puma.geoid10 as geo
FROM tiger2015.puma puma, attrs.university u
WHERE ST_Intersects(puma.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
