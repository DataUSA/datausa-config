SELECT university.id AS university,
   substr(university.opeid, 0, 7) AS opeid
  FROM attrs.university
 WHERE university.opeid IS NOT NULL;
