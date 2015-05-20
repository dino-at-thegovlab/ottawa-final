# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding("utf-8")

from flask import Flask
from flask import abort
from flask import request
from flask import flash
from flask import redirect
from flask import url_for
from flask import render_template
from flask import session
from flask import jsonify

import yaml
import db

from slugify import slugify

noi_slug = lambda x: slugify(x, to_lower=True)

def avatar(user):
    if user['picture']:
        return user['picture']
    else:
        return "/static/icons/%s.gif" % ('%03d' % (int(user['userid']) % 361))

import json

COUNTRIES = "Afghanistan,Algeria,Argentina,Australia,Austria,Bahamas,Bangladesh,Belgium,Belize,Benin,Bhutan,Brazil,Bulgaria,Burkina Faso,Burundi,Cambodia,Cameroon,Canada,Central African Rep,Chad,Chile,China,Colombia,Congo,Congo, The Democratic Rep,Connected!,Connecting to database,Costa Rica,Cuba,Czech Republic,Denmark,Djibouti,Dominican Republic,Ecuador,Egypt,El Salvador,Ethiopia,Fiji,Finland,France,Gambia,Georgia,Germany,Ghana,Guatemala,Guinea,Haiti,Hungary,India,Indonesia,Iran,Iraq,Ireland,Italy,Ivory Coast (Cote D'Ivoire),Jamaica,Japan,Jordan,Kenya,Korea, Republic Of,Kyrgyzstan,Lebanon,Liberia,Lithuania,Macedonia (Republic of),Madagascar,Malawi,Malaysia,Mali,Mauritania,Mexico,Moldova, Rep,Mongolia,Montenegro,Namibia,Nepal,Netherlands,New Zealand,Niger,Nigeria,Pakistan,Panama,Papua New Guinea,Paraguay,Peru,Philippines,Romania,Russian Federation,Rwanda,Samoa,Senegal,Serbia,Slovakia (Slovak Rep),Somalia,South Africa,Spain,Sri Lanka,Sudan,Sweden,Switzerland,Taiwan,Tajikistan,Tanzania,Thailand,Togo,Tonga,Trinidad & Tobago,Tunisia,Turkey,Uganda,Ukraine,United Kingdom,United States,Uruguay,Viet Nam,Yemen,Zambia".split(',')
LANGS = 'Afrikanns|Albanian|Arabic|Armenian|Basque|Bengali|Bulgarian|Catalan|Cambodian|Chinese (Mandarin)|Croation|Czech|Danish|Dutch|English|Estonian|Fiji|Finnish|French|Georgian|German|Greek|Gujarati|Hebrew|Hindi|Hungarian|Icelandic|Indonesian|Irish|Italian|Japanese|Javanese|Korean|Latin|Latvian|Lithuanian|Macedonian|Malay|Malayalam|Maltese|Maori|Marathi|Mongolian|Nepali|Norwegian|Persian|Polish|Portuguese|Punjabi|Quechua|Romanian|Russian|Samoan|Serbian|Slovak|Slovenian|Spanish|Swahili|Swedish |Tamil|Tatar|Telugu|Thai|Tibetan|Tonga|Turkish|Ukranian|Urdu|Uzbek|Vietnamese|Welsh|Xhosa'.split('|')

CONTENT = yaml.load(open('content.yaml'))


app = Flask(__name__)
app.jinja_env.filters['slug'] = noi_slug
app.jinja_env.filters['avatar'] = avatar
app.debug = True
app.secret_key = 'M\xb5\xc1\xa39t\x97\x88\x13A\xe8\t\x90\xc2\x04@\xe4\xdeM\xc8?\x05}j'
SSL = False


@app.route('/test')
def test():
    return 'hello' + session


@app.route('/')
def main_page():
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
        return jsonify({'result': 0})


@app.route('/logout')
def logout():
    idp = session['social-login']['idp']
    session.clear()
    return redirect(url_for('main_page', **{'logout': idp}))


@app.route('/me', methods=['GET', 'POST'])
def my_profile():
    if request.method == 'GET':
        social_login = session['social-login']
        print "Looking up %s" % social_login['userid']
        userProfile = db.getUser(social_login['userid'])  # We get some stuff from the DB.
        print userProfile
        return render_template('my-profile.html', **{'userProfile': userProfile, 'COUNTRIES': COUNTRIES, 'LANGS': LANGS})
    if request.method == 'POST':
        userProfile = json.loads(request.form.get('me'))
        session['user-profile'] = userProfile
        db.updateCoreProfile(userProfile)
        flash('Your profile has been saved.')
        return render_template('my-profile.html', **{'userProfile': userProfile, 'COUNTRIES': COUNTRIES, 'LANGS': LANGS})


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
            return render_template('my-expertise.html', **{'userExpertise': userExpertise, 'AREAS': CONTENT['areas']})
 

@app.route('/dashboard')
def dashboard():
    top_countries = db.top_countries()
    return render_template('dashboard.html', **{'top_countries': top_countries})


@app.route('/user/<userid>')
def get_user(userid):
    user = db.getUser(userid)
    print user
    if user:
        return render_template('user-profile.html', **{'user': user, 'SKILLS': []})
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
        return render_template('search-results.html', **{'title': 'Expertise search', 'results': experts, 'query': query})

@app.route('/match')
def match():
    print session
    query = {'location': '', 'langs': [], 'skills': [], 'fulltext': 'NYU'}
    if 'user-expertise' not in session:
        session['user-expertise'] = {}
    experts = db.findMatchAsJSON(session['user-expertise'])
    return render_template('search-results.html', **{'title': 'Matching search', 'results': experts, 'query': query})


#################### MAIN ####################

if __name__ == "__main__":
    if SSL:
        context = ('server.crt', 'server.key')
        app.run(host='0.0.0.0', port=443, ssl_context=context)
    else:
        app.run(host='0.0.0.0', port=80)
