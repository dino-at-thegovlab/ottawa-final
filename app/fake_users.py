import csv
from psycopg2.extras import Json


import yaml
import random
import json
import sys

from slugify import slugify

noi_slug = lambda x: slugify(x, to_lower=True)

import db

LEVELS = ['I can refer', 'I can teach', 'I can do', 'I am interested']
LANGS = 'Afrikanns|Albanian|Arabic|Armenian|Basque|Bengali|Bulgarian|Catalan|Cambodian|Chinese (Mandarin)|Croation|Czech|Danish|Dutch|English|Estonian|Fiji|Finnish|French|Georgian|German|Greek|Gujarati|Hebrew|Hindi|Hungarian|Icelandic|Indonesian|Irish|Italian|Japanese|Javanese|Korean|Latin|Latvian|Lithuanian|Macedonian|Malay|Malayalam|Maltese|Maori|Marathi|Mongolian|Nepali|Norwegian|Persian|Polish|Portuguese|Punjabi|Quechua|Romanian|Russian|Samoan|Serbian|Slovak|Slovenian|Spanish|Swahili|Swedish |Tamil|Tatar|Telugu|Thai|Tibetan|Tonga|Turkish|Ukranian|Urdu|Uzbek|Vietnamese|Welsh|Xhosa'.split('|')


CONTENT = yaml.load(open('content.yaml'))
SKILLS = {}

for area in CONTENT['areas']:
    if 'topics' not in area:
        continue
    for topic in area['topics']:
        SKILLS[topic['topic']] = []
        for question in topic['questions']:
            SKILLS[topic['topic']].append(noi_slug(question['label']))


def makeRandomSkills():
    all_skills = [{'fake': 0}]
    for s in SKILLS:
        if random.random() > 0.5:
            how_many_items = int(random.gauss(len(SKILLS[s]), 1)) % len(SKILLS[s])
            skills = random.sample(SKILLS[s], how_many_items)
            for x in skills:
                all_skills.append({x: random.randint(0, len(LEVELS)-1)})
    return all_skills

#print makeRandomSkills()

def insertUser(cursor, user):
    try:
        SQL = """INSERT INTO users(userid, first_name, last_name, country, city, org, title, skills, langs)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s);"""
        data = (user['userid'], user['first_name'], user['last_name'], user['country'], user['city'], user['org'], user['title'],
            Json(user['skills']), Json(user['langs']), )
        print cursor.mogrify(SQL, data)
        cursor.execute(SQL, data)
        cursor.connection.commit()
    except Exception, e:
        cursor.connection.rollback()
        print "ERROR"
        print e
        print "Error insert >>%s<<" % user

cursor = db.getCursor()
with open('ottawa-list.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    for item in reader:
        (userid, last_name, org, country, email, title, registration_type, first_name, city) = item
        skills = makeRandomSkills()
        langs = [random.choice(LANGS), random.choice(LANGS)]

        user = {'userid': userid, 'first_name': first_name, 'last_name': last_name,
        'country': country, 'city': city, 'org': org, 'title': title,
        'skills': skills, 'langs': langs}
        insertUser(cursor, user)