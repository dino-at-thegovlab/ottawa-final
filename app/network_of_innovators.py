# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask
from flask import abort
from flask import request
from flask import Response
from flask import flash
from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
from flask import jsonify
from flask import g

import yaml
import db
import platform

from vcard import make_vCard

from slugify import slugify

noi_slug = lambda x: slugify(x, to_lower=True)


def avatar(user):
    if user['picture']:
        return user['picture']
    else:
        return "/static/icons/%s.gif" % ('%03d' % (int(user['userid']) % 361))


def email_recipients(users):
    return [user['email'] for user in users if user['email'] is not None]


def make_question(question, area, topic):
    return "%s/%s/%s" % (area['id'], noi_slug(topic['topic']), noi_slug(question['label']))


def skills_by_area(skills, area):
    return [i for i in skills.keys() if i.startswith(area['id'])]


LEVELS = {'LEVEL_I_CAN_EXPLAIN': {'score': 2, 'icon': '<i class="fa fa-graduation-cap"></i>'},
          'LEVEL_I_CAN_DO_IT': {'score': 5, 'icon': '<i class="fa fa-cubes"></i>'},
          'LEVEL_I_CAN_REFER': {'score': 1, 'icon': '<i class="fa fa-user-plus"></i>'},
          'LEVEL_I_WANT_TO_LEARN': {'score': -1, 'icon': '<i class="fa fa-heart"></i>'}}
# ASSERT THAT all scores are different.

CONSTANTS = {}
CONSTANTS['EMAIL_FEEDBACK'] ='noi-app-feedback@thegovlab.org'

def expertise_level_icon(level_score):
    level = [l for l in LEVELS.keys() if LEVELS[l]['score'] == int(level_score)]
    if level:
        return LEVELS[level[0]]['icon']
    else:
        return '<i class="fa fa-question"></i>'

import json

COUNTRIES = "Afghanistan,Algeria,Argentina,Australia,Austria,Bahamas,Bangladesh,Belgium,Belize,Benin,Bhutan,Brazil,Bulgaria,Burkina Faso,Burundi,Cambodia,Cameroon,Canada,Central African Rep,Chad,Chile,China,Colombia,Congo,Congo, The Democratic Rep,Connected!,Connecting to database,Costa Rica,Cuba,Czech Republic,Denmark,Djibouti,Dominican Republic,Ecuador,Egypt,El Salvador,Ethiopia,Fiji,Finland,France,Gambia,Georgia,Germany,Ghana,Guatemala,Guinea,Haiti,Hungary,India,Indonesia,Iran,Iraq,Ireland,Italy,Ivory Coast (Cote D'Ivoire),Jamaica,Japan,Jordan,Kenya,Korea, Republic Of,Kyrgyzstan,Lebanon,Liberia,Lithuania,Macedonia (Republic of),Madagascar,Malawi,Malaysia,Mali,Mauritania,Mexico,Moldova, Rep,Mongolia,Montenegro,Namibia,Nepal,Netherlands,New Zealand,Niger,Nigeria,Pakistan,Panama,Papua New Guinea,Paraguay,Peru,Philippines,Romania,Russian Federation,Rwanda,Samoa,Senegal,Serbia,Slovakia (Slovak Rep),Somalia,South Africa,Spain,Sri Lanka,Sudan,Sweden,Switzerland,Taiwan,Tajikistan,Tanzania,Thailand,Togo,Tonga,Trinidad & Tobago,Tunisia,Turkey,Uganda,Ukraine,United Kingdom,United States,Uruguay,Viet Nam,Yemen,Zambia".split(',')
LANGS = 'Afrikanns|Albanian|Arabic|Armenian|Basque|Bengali|Bulgarian|Catalan|Cambodian|Chinese (Mandarin)|Croation|Czech|Danish|Dutch|English|Estonian|Fiji|Finnish|French|Georgian|German|Greek|Gujarati|Hebrew|Hindi|Hungarian|Icelandic|Indonesian|Irish|Italian|Japanese|Javanese|Korean|Latin|Latvian|Lithuanian|Macedonian|Malay|Malayalam|Maltese|Maori|Marathi|Mongolian|Nepali|Norwegian|Persian|Polish|Portuguese|Punjabi|Quechua|Romanian|Russian|Samoan|Serbian|Slovak|Slovenian|Spanish|Swahili|Swedish |Tamil|Tatar|Telugu|Thai|Tibetan|Tonga|Turkish|Ukranian|Urdu|Uzbek|Vietnamese|Welsh|Xhosa'.split('|')

ORG_TYPES = { 'edu': 'Academia', 'com': 'Private Sector', 'org': 'Non Profit', 'gov': 'Government', 'other': 'Other' }

CONTENT = yaml.load(open('content.yaml'))

NOI_COLORS =  'red,blue,green,orange,purple,yellow,gray'.split(',')

#REDIRECT_PAGE = 'http://noi.thegovlab.org/'
if platform.linux_distribution()[0] == 'Ubuntu':
    HOST = 'noi.thegovlab.org'
else:
    HOST = 'localhost'
print "Running service on %s." % HOST

app = Flask(__name__)
app.jinja_env.filters['slug'] = noi_slug
app.jinja_env.filters['avatar'] = avatar
app.jinja_env.filters['email_recipients'] = email_recipients
app.jinja_env.filters['make_question'] = make_question
app.jinja_env.filters['skills_by_area'] = skills_by_area
app.jinja_env.filters['expertise_level_icon'] = expertise_level_icon


# Constant that should be available for all templates.
app.jinja_env.globals['ORG_TYPES'] = ORG_TYPES
app.jinja_env.globals['CONTENT'] = CONTENT
app.jinja_env.globals['COUNTRIES'] = COUNTRIES
app.jinja_env.globals['LANGS'] = LANGS
app.jinja_env.globals['NOI_COLORS'] = NOI_COLORS
app.jinja_env.globals['HOST'] = HOST
app.jinja_env.globals['CONSTANTS'] = CONSTANTS
app.jinja_env.globals['LEVELS'] = LEVELS
app.jinja_env.globals['DEBUG'] = False



app.debug = True
app.secret_key = 'M\xb5\xc1\xa39t\x97\x88\x13A\xe8\t\x90\xc2\x04@\xe4\xdeM\xc8?\x05}j'
SSL = False


@app.route('/test')
def test():
    return 'hello' + session


@app.route('/')
def main_page():
    print session

    return render_template('main.html', **{'SKIP_NAV_BAR': False})


@app.route('/test-template')
def test_template():
    return render_template('test.html', **{'SKIP_NAV_BAR': False})


@app.route('/about')
def about_page():
    return render_template('about.html', **{})


@app.route('/test-hello')
def test_hello():
    return render_template('test-hello.html', **{})


@app.route('/login', methods=['GET', 'POST'])
def login():
    print session
    if request.method == 'GET':
        return render_template('login-page.html', **{'SKIP_NAV_BAR': True})
    if request.method == 'POST':
        social_login = json.loads(request.form.get('social-login'))
        session['social-login'] = social_login
        userid = social_login['userid']
        userProfile = db.getUser(userid)
        if userProfile:
            session['user-profile'] = userProfile
        else:
            db.createNewUser(userid, social_login['first_name'], social_login['last_name'], social_login['picture'])
            userProfile = db.getUser(userid)
            session['user-profile'] = userProfile
        flash('You are authenticated using your %s Credentials.' % social_login['idp'])
        g.is_logged_in = True
        return jsonify({'result': 0})


@app.route('/logout')
def logout():
    idp = session['social-login']['idp']
    session.clear()
    return redirect(url_for('main_page', **{'logout': idp}))


@app.route('/edit/<userid>', methods=['GET', 'POST'])
def edit_user(userid):
    if request.method == 'GET':
        userProfile = db.getUser(userid)  # We get some stuff from the DB.
        return render_template('my-profile.html', **{'userProfile': userProfile })
    if request.method == 'POST':
        userProfile = json.loads(request.form.get('me'))
        session['user-profile'] = userProfile
        db.updateCoreProfile(userProfile)
        flash('Your profile has been saved.')
        return render_template('my-profile.html', **{'userProfile': userProfile})

@app.route('/me', methods=['GET', 'POST'])
def my_profile():
    if request.method == 'GET':
        social_login = session['social-login']
        print "Looking up %s" % social_login['userid']
        userProfile = db.getUser(social_login['userid'])  # We get some stuff from the DB.
        print userProfile
        return render_template('my-profile.html', **{'userProfile': userProfile })
    if request.method == 'POST':
        userProfile = json.loads(request.form.get('me'))
        session['user-profile'] = userProfile
        db.updateCoreProfile(userProfile)
        flash('Your profile has been saved.')
        session['has_created_profile'] = True
        return render_template('my-profile.html', **{'userProfile': userProfile})


@app.route('/my-expertise', methods=['GET', 'POST'])
def my_expertise():
        social_login = session['social-login']
        userid = social_login['userid']
        if request.method == 'GET':
            userProfile = db.getUser(userid)
            print userProfile
            userExpertise = userProfile['skills']
            return render_template('my-expertise.html', **{ 'AREAS': CONTENT['areas'],
                'userExpertise': userExpertise})
        if request.method == 'POST':
            userExpertise = json.loads(request.form.get('my-expertise-as-json'))
            session['user-expertise'] = userExpertise
            db.updateExpertise(userid, userExpertise)
            flash('Your expertise has been saved.')
            session['has_filled_expertise'] = True
            return render_template('my-expertise.html', **{'userExpertise': userExpertise, 'AREAS': CONTENT['areas']})
 

@app.route('/dashboard')
def dashboard():
    top_countries = db.top_countries()
    ALL_USERS = db.getAllUsers()
    OCCUPATIONS = db.getUserOccupations()
    return render_template('dashboard.html', **{'top_countries': top_countries,
                                                'ALL_USERS': ALL_USERS, 'OCCUPATIONS': OCCUPATIONS})

@app.route('/dashboard-2')
def dashboard2():
    top_countries = db.top_countries()
    return render_template('dashboard-2.html', **{'top_countries': top_countries})

@app.route('/vcard/<userid>')
def vcard(userid):
    user = db.getUser(userid)
    if user:
        card = make_vCard(user['first_name'], user['last_name'], user['org'], user['title'], user['email'], user['city'], user['country'])
        return Response(card, mimetype='text/vcard')
    else:
        flash('This is does not correspond to a valid user.')
        return redirect(url_for('main'))


@app.route('/user/<userid>')
def get_user(userid):
    user = db.getUser(userid)
    print user
    if user:
        return render_template('user-profile.html', **{'user': user, 'userid': userid, 'SKILLS': []})
    else:
        flash('This is does not correspond to a valid user.')
        return redirect(url_for('search'))

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'GET':
        return render_template('search.html', **{ 'LANGS': LANGS, 'COUNTRIES': COUNTRIES, 'AREAS': CONTENT['areas']})
    if request.method == 'POST':
        print request
        country = request.values.get('country', '')
        langs = request.values.getlist('langs')
        skills = request.values.getlist('skills')
        fulltext = request.values.get('fulltext', '')
        query = {'location': country, 'langs': langs, 'skills': skills, 'fulltext': fulltext}
        print query
        experts = db.findExpertsAsJSON(**query)
        session['has_done_search'] = True
        return render_template('search-results.html', **{'title': 'Expertise search', 'results': experts, 'query': query})

@app.route('/match')
def match():
    social_login = session['social-login']
    userid = social_login['userid']
    query = {'location': '', 'langs': [], 'skills': [], 'fulltext': ''}
    if 'skills' not in session['user-expertise']:
        userProfile = db.getUser(userid)
        userExpertise = userProfile['skills']
        session['user-expertise'] = userExpertise
    print "user expertise: ", json.dumps(session['user-expertise'])
    skills = session['user-expertise']
    my_needs = [k for k,v in skills.iteritems() if int(v) == -1]
    print my_needs
    experts = db.findMatchAsJSON(my_needs)
    session['has_done_search'] = True
    return render_template('search-results.html', **{'title': 'People Who Know what I do not', 'results': experts, 'query': query})


@app.route('/match-knn')
def knn():
    query = {}
    if 'user-expertise' not in session:
        print "User expertise not in session"
        my_needs = []
    else:
        skills = session['user-expertise']
    print skills
    experts = db.findMatchKnnAsJSON(skills)
    session['has_done_search'] = True
    return render_template('search-results.html', **{'title': 'People most like me', 'results': experts, 'query': query})


@app.route('/match-test')
def match_test():
    print session
    query = {'location': '', 'langs': [], 'skills': [], 'fulltext': 'NYU'}
    if 'user-expertise' not in session:
        session['user-expertise'] = {}
    experts = db.findMatchAsJSON(session['user-expertise'])
    return render_template('test.html', **{'title': 'Matching search', 'results': experts, 'query': query})


#################### MAIN ####################

if __name__ == "__main__":
    if SSL:
        context = ('server.crt', 'server.key')
        app.run(host='0.0.0.0', port=443, ssl_context=context)
    else:
        app.run(host='0.0.0.0', port=80)
