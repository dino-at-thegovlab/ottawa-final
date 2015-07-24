#!/usr/bin/python
# -*- coding: utf-8 -*-
import psycopg2
import sys
from psycopg2.extras import Json

HOST = 'db'
DBNAME = 'noi2'
DBUSER = 'postgres'
PASSWORD = 'ottawa6491'
PORT = 5432

CONN_STR = """host='%(HOST)s' dbname='%(DBNAME)s' 
    user='%(DBUSER)s' password='%(PASSWORD)s' port=%(PORT)s""" % { 'HOST': HOST, 'PORT': PORT, 'DBNAME': DBNAME, 'DBUSER': DBUSER, 'PASSWORD': PASSWORD, 'PORT': PORT}


def getCursor():
    conn = psycopg2.connect(CONN_STR)
    print "Connected!\n"
    cursor = conn.cursor()
    return cursor


def runQuery(sql, data):
    cursor = getCursor()
    print cursor.mogrify(sql, data)
    cursor.execute(sql, data)
    records = cursor.fetchall()
    cursor.close()
    return records


def logQuery(userid, query_info):
    cursor = getCursor()
    SQL = """INSERT INTO query_logs(userid, query_info) VALUES (%s, %s)"""
    data = (userid, Json(query_info))
    cursor.execute(SQL, data)
    cursor.connection.commit()


def getUserOccupations():
    cursor = getCursor()
    SQL = """SELECT row_to_json(T) FROM
            ( SELECT COUNT(*) AS cnt, org_type
              FROM all_users WHERE org_type != '' GROUP BY org_type
            ) AS T"""
    data = ()
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    records = cursor.fetchall()
    cursor.close()
    return map(lambda x: x[0], records)


def getAllUsers():
    cursor = getCursor()
    SQL = """SELECT row_to_json(T) FROM
                (SELECT userid AS userid,
                    first_name AS first_name,
                     last_name AS last_name,
                        latlng AS latlng FROM all_users
                ) AS T"""
    data = ()
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    records = cursor.fetchall()
    cursor.close()
    return map(lambda x: x[0], records)


def getRecentUsers(limit=10):
    cursor = getCursor()
    SQL = """SELECT row_to_json(T) FROM
                (SELECT * FROM users ORDER BY timestamp DESC limit %s) AS T"""
    data = (limit,)
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    records = cursor.fetchall()
    cursor.close()
    return map(lambda x: x[0], records)    


def findMatchAsJSON(my_needs):
    cursor = getCursor()
    SQL = """SELECT row_to_json(T1) FROM
                (SELECT *, plv8_match_my_needs(%s, skills::json) AS score
                FROM all_users WHERE skills IS NOT NULL) AS T1
            ORDER BY score DESC LIMIT 20;"""
    data = (my_needs, )
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    records = cursor.fetchall()
    cursor.close()
    return map(lambda x: x[0], records)


def findMatchKnnAsJSON(my_skills):
    cursor = getCursor()
    SQL = """SELECT row_to_json(T1) FROM
                (SELECT *, plv8_knn_skills(%s, skills::json) AS score
                FROM all_users WHERE skills IS NOT NULL) AS T1
            ORDER BY score ASC LIMIT 20;"""
    data = (Json(my_skills), )
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    records = cursor.fetchall()
    cursor.close()
    return map(lambda x: x[0], records)


def findExpertsAsJSON(location, langs, skills, fulltext, domains):
    cursor = getCursor()
    if fulltext != "":
        SQL = """SELECT row_to_json(T1) FROM
        (
        SELECT *, plv8_score(skills, %s) AS score
        FROM all_users
        WHERE ( (country=%s) OR (%s='') ) AND
        ( (langs::jsonb ?| %s) OR (%s='{}') ) AND
        ( (domains::jsonb ?| %s) OR (%s='{}') ) AND
        to_tsvector(ARRAY_TO_STRING(ARRAY[first_name, last_name, org, title, projects], ' ')) @@ plainto_tsquery(%s)
        ) AS T1
        ORDER BY score DESC LIMIT 20"""
        data = (skills, location, location, langs, langs, domains, domains, fulltext)
    else:        
        SQL = """SELECT row_to_json(T1) FROM
            (
            SELECT *, plv8_score(skills, %s) AS score
            FROM all_users
            WHERE ( (country=%s) OR (%s='') ) AND
            ( (langs::jsonb ?| %s) OR (%s='{}') ) AND
            ( (domains::jsonb ?| %s) OR (%s='{}') )
            ) AS T1
        ORDER BY score DESC LIMIT 20"""
        data = (skills, location, location, langs, langs, domains, domains)
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    records = cursor.fetchall()
    cursor.close()
    return map(lambda x:x[0], records)


def getUser(userid):
    SQL = """SELECT row_to_json(all_users) FROM all_users WHERE userid = %s"""
    data = (userid,)
    records = runQuery(SQL, data)
    if records and records[0]:
        return records[0][0]
    else:
        records


def updateExpertise(userid, expertise):
    cursor = getCursor()
    data = (Json(expertise), userid)
    SQL = """UPDATE users SET skills = %s
    WHERE userid = %s"""
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    cursor.connection.commit()
    cursor.close()
    return


def createNewUser(userid, first_name='', last_name='', picture=''):
    cursor = getCursor()
    SQL = """INSERT INTO users(userid, first_name, last_name, picture) VALUES (%s, %s, %s, %s)"""
    data = ( userid, first_name, last_name, picture)
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    cursor.connection.commit()


def updateCoreProfile(user):
    cursor = getCursor()
    data = (user['first_name'], user['last_name'], user['email'], user['picture'],
        user['country'], user['country_code'], user['city'],
        user['org'], user['title'], Json(user['langs']), user['latlng'], user['org_type'], Json(user['domains']), user['projects'], user['userid'])
    try:
        SQL = """INSERT INTO users(first_name, last_name, email, picture, country, country_code, city, org, title, langs, latlng, org_type, domains, projects, userid)
                        VALUES    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        print cursor.mogrify(SQL, data)
        cursor.execute(SQL, data)
        cursor.connection.commit()
        return
    except Exception, e:
        print e
        cursor.connection.rollback()
    SQL = """UPDATE users SET (first_name, last_name, email, picture, country, country_code, city, org, title, langs, latlng, org_type, domains, projects) =
    (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) WHERE userid = %s"""
    print cursor.mogrify(SQL, data)
    cursor.execute(SQL, data)
    cursor.connection.commit()
    cursor.close()
    return




def top_countries():
    SQL = """SELECT country, COUNT(*) AS cnt
    FROM all_users WHERE country != '' GROUP BY country ORDER BY cnt DESC;"""
    data = ()
    records = runQuery(SQL, data)
    return records

if __name__ == "__main__":
    records = top_countries()
    for r in records:
        print r
