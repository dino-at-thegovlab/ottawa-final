CREATE DATABASE noi2;
\c noi2;

CREATE EXTENSION plv8;

CREATE TABLE IF NOT EXISTS users ( userid varchar(50) PRIMARY KEY,
  first_name text,
  last_name text,
  email text,
  country text,
  country_code text,
  city text,
  latlng text,
  org text,
  org_type text,
  picture text,
  title text,
  langs json,
  domains json,
  skills json,
  domain_expertise text,
  projects text,
  timestamp timestamp default current_timestamp,
  account_type smallint  );

ALTER TABLE users ADD COLUMN org_type text;
ALTER TABLE users ADD COLUMN latlng text;
ALTER TABLE users ADD COLUMN domain text;
ALTER TABLE users ADD COLUMN timestamp timestamp default current_timestamp;
ALTER TABLE users ADD COLUMN account_type smallint default 0;
ALTER TABLE users ADD COLUMN country_code text;
ALTER TABLE users ADD COLUMN domains json;
ALTER TABLE users ADD COLUMN projects text;

-- CREATE OR REPLACE VIEW all_users AS SELECT * FROM users;
CREATE OR REPLACE VIEW all_users AS SELECT * FROM users WHERE account_type = 0;

CREATE TABLE IF NOT EXISTS query_logs (
	userid varchar(50),
	timestamp timestamp default current_timestamp,
	query_info json);

CREATE OR REPLACE FUNCTION plv8_score(skills json, tags text[])
RETURNS integer AS $$
	var count = 0;
	for (var i = 0; i < tags.length; i++) {
		if (tags[i] in skills) {
			count = count + Math.max(skills[tags[i]], 0);
		}
	}
	return count;
$$ LANGUAGE plv8 IMMUTABLE CALLED ON NULL INPUT;
/* We intersect the two sets and only count positive expertise. */


CREATE OR REPLACE FUNCTION plv8_match_my_needs(my_needs text[], their_skills json)
RETURNS integer AS $$
	var count = 0;
	for (var i = 0; i < my_needs.length; i++) {
		if (my_needs[i] in their_skills) {
			count = count + Math.max(their_skills[my_needs[i]], 0);
		}
	}
	return count;
$$ LANGUAGE plv8 IMMUTABLE CALLED ON NULL INPUT;

CREATE OR REPLACE FUNCTION plv8_test(json_data json)
RETURNS integer AS $$
	plv8.elog(NOTICE, 'Inside plv8_test function');
	plv8.elog(NOTICE, JSON.stringify(json_data));
	return 0;
$$ LANGUAGE plv8 IMMUTABLE CALLED ON NULL INPUT;


CREATE OR REPLACE FUNCTION plv8_knn_skills(my_skills json, their_skills json)
RETURNS float AS $$
	// plv8.elog(NOTICE, JSON.stringify(my_skills), JSON.stringify(their_skills));
	var skills = Object.keys(my_skills);
	var scores = [1];
	for (var i = 0; i < skills.length; i++) {
		if (skills[i] in their_skills) {
			var diff = parseInt(their_skills[skills[i]]) - parseInt(my_skills[skills[i]]);
			scores.push(diff * diff);
		}
		else {
			scores.push(50);
		}
	}
	scores = scores.sort().reverse().slice(0,10);
	var scores_length = scores.length;
	var count = 0.0;
	for (var j = 0; j < scores_length; j++) {
		count = count + scores[j];
	}
	var result = count / (1.0 * scores.length);
	return result;
$$ LANGUAGE plv8 IMMUTABLE CALLED ON NULL INPUT;

/* We intersect the two sets and only count positive expertise. */

/*

noi2=# select count(*), split_part(userid, ':', 1) AS social from all_users GROUP BY social;
 count |  social   
-------+-----------
     6 | facebook
    19 | google
     1 | windows
    11 | twitter
     1 | instagram
    20 | linkedin
(6 rows)

%% Get some stats about how people are using the forms.
SELECT skill_number, COUNT(*) FROM
	(SELECT userid, COUNT(*) AS skill_number FROM
		(SELECT userid, json_object_keys(skills) AS skill FROM all_users)
		AS T WHERE skill LIKE 'opendata%' GROUP BY userid)
	AS T2 GROUP by skill_number ORDER BY skill_number DESC;

*/
