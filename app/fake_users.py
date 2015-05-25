import csv
from psycopg2.extras import Json


import yaml
import random
import json
import sys
from geopy.geocoders import Nominatim
from geopy.geocoders import GoogleV3
import time

from slugify import slugify

noi_slug = lambda x: slugify(x, to_lower=True)

import db

LEVELS = ['I can refer', 'I can teach', 'I can do', 'I want to learn']
LANGS = 'Afrikanns|Albanian|Arabic|Armenian|Basque|Bengali|Bulgarian|Catalan|Cambodian|Chinese (Mandarin)|Croation|Czech|Danish|Dutch|English|Estonian|Fiji|Finnish|French|Georgian|German|Greek|Gujarati|Hebrew|Hindi|Hungarian|Icelandic|Indonesian|Irish|Italian|Japanese|Javanese|Korean|Latin|Latvian|Lithuanian|Macedonian|Malay|Malayalam|Maltese|Maori|Marathi|Mongolian|Nepali|Norwegian|Persian|Polish|Portuguese|Punjabi|Quechua|Romanian|Russian|Samoan|Serbian|Slovak|Slovenian|Spanish|Swahili|Swedish |Tamil|Tatar|Telugu|Thai|Tibetan|Tonga|Turkish|Ukranian|Urdu|Uzbek|Vietnamese|Welsh|Xhosa'.split('|')

CONTENT = yaml.load(open('content.yaml'))
SKILLS = {}

for area in CONTENT['areas']:
    if 'topics' not in area:
        continue
    for topic in area['topics']:
        key = "%s/%s" % (area['id'], noi_slug(topic['topic']))
        SKILLS[key] = []
        for question in topic['questions']:
            SKILLS[key].append("%s/%s" % (key, noi_slug(question['label'])))

def makeRandomSkills():
    all_skills = {}
    for s in SKILLS:
        if random.random() > 0.8:
            how_many_items = int(random.gauss(len(SKILLS[s]), 1)) % len(SKILLS[s])
            skills = random.sample(SKILLS[s], how_many_items)
            for x in skills:
                all_skills[x] = random.randint(0, len(LEVELS)-1)
    return all_skills

print makeRandomSkills()
sys.exit(-1)

def insertUser(cursor, user):
    try:
        SQL = """INSERT INTO users(userid, first_name, last_name, country, city, latlng,
            org, org_type, title, skills, langs, account_type)   
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, -1);"""
        data = (user['userid'], user['first_name'], user['last_name'], user['country'], user['city'], user['latlng'],
            user['org'], user['org_type'], user['title'],
            Json(user['skills']), Json(user['langs']), )
        print cursor.mogrify(SQL, data)
        cursor.execute(SQL, data)
        cursor.connection.commit()
    except Exception, e:
        cursor.connection.rollback()
        print "ERROR"
        print e
        print "Error insert >>%s<<" % user

sectorMapping = { 'Academic': 'edu', 'Government': 'gov', 'Media': 'other', 'Other': 'other',
'Independent': 'other', 'Multilateral Agency': 'gov', 'Private Sector': 'com', 'NGO': 'org', 'Student': 'edu'}
def mapSector(s):
    if s in sectorMapping:
        return sectorMapping[s]
    else:
        print "no mapping for %s" % s
        return 'other'


cursor = db.getCursor()
#geolocator = Nominatim()
geolocator = GoogleV3(api_key='AIzaSyCjJduX95CXz3LtiX5sfw19GhqcicVYs6c', timeout=5)

GEOCODE = True
DRYRUN = False
COUNT = 2000

with open('ottawa-list-latest.csv', 'rb') as csvfile:
    reader = csv.reader(csvfile)
    next(reader, None)
    count = 0
    for item in reader:
        time.sleep(1)
        (userid, first_name, last_name, org, country, email, title, org_type) = item
        skills = makeRandomSkills()
        langs = [random.choice(LANGS), random.choice(LANGS)]

        user = {'userid': userid, 'first_name': first_name, 'last_name': last_name,
        'country': country, 'city': '', 'org': org, 'org_type': mapSector(org_type), 'title': title,
        'skills': skills, 'langs': langs}
        if (GEOCODE):
            location = geolocator.geocode(country)
            if location:
                user['latlng'] = "(%s, %s)" % (location.latitude, location.longitude)
            else:
                user['latlng'] = "(85, 0)"
        else:
            user['latlng'] = "(85, 0)"
        
        if not DRYRUN:
            insertUser(cursor, user)
        count = count + 1
        if count > COUNT:
            break