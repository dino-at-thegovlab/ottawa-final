CREATE DATABASE noi2;
\c noi2;
CREATE TABLE  users ( userid varchar(50) PRIMARY KEY,
  first_name text,
  last_name text,
  email text,
  country text,
  city text,
  org text,
  picture text,
  title text,
  langs json,
  skills json);

CREATE OR REPLACE FUNCTION plv8_score(skills json, tags text[])
RETURNS integer AS $$
var count = 0;
try {
	var skill_keys = Object.keys(skills);
	for (var i = 0; i < tags.length; i++) {
		for (var j in skill_keys) {
			var skill_key = skill_keys[j];
			if (tags[i] in skills[skill_key]) {
				count = count + skills[skill_key][tags[i]];
			}
		}
	}
	} catch(err) {
	}
	return count;
$$ LANGUAGE plv8 IMMUTABLE STRICT;