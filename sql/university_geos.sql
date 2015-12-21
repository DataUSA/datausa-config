-- First run:
-- pg_dump -t attrs.ztest_university datausa -h postgres.datawheel.us -U postgres -W > /tmp/universities.sql
-- insert into attrs.university (select * from attrs.ztest_university where id not in (select id from attrs.university))
-- CREATE LOOKUP for each univ
CREATE TABLE university_geo AS
SELECT u.id as university, '04000US' || state.geoid as geo
FROM tiger2013.state state, university u
WHERE ST_Intersects(state.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326))
UNION
(SELECT u.id as university, '05000US' || county.geoid as geo
FROM tiger2013.county county, university u
WHERE ST_Intersects(county.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
UNION
(SELECT u.id as university, '31000US' || cbsa.geoid as geo
FROM tiger2013.cbsa cbsa, university u
WHERE ST_Intersects(cbsa.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
UNION
(SELECT u.id as university, '16000US' || place.geoid as geo
FROM tiger2013.place place, university u
WHERE ST_Intersects(place.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
UNION
(SELECT u.id as university, '79500US' || puma.geoid10 as geo
FROM tiger2013.puma puma, university u
WHERE ST_Intersects(puma.geom, ST_SetSRID(ST_Point(u.lng, u.lat),4326)))
