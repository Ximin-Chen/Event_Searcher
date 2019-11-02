import urllib
from functools import wraps

import requests
from app import app, db
from flask import render_template, flash, redirect, url_for, copy_current_request_context
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Event
from flask import request, abort, session
from werkzeug.urls import url_parse
from datetime import datetime
import json
from flask import jsonify, Response

# def login_required(func):
#         @wraps(func)
#         def decorated_function(*args, **kwargs):
#             if 'user_id' not in session:
#                 abort(401)
#             return func(*args, **kwargs)
#         return decorated_function


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template("index.html", title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    # form = LoginForm()
    # if form.validate_on_submit():
    #     user = User.query.filter_by(username=form.username.data).first()
    #     if user is None or not user.check_pw(form.password.data):
    #         flash('Invalid username or password!')
    #         return redirect(url_for('index'))
    #     login_user(user, remember=form.remember_me.data)
    #     next_page = request.args.get('next')
    #     if not next_page or url_parse(next_page).netloc != '':
    #         next_page = url_for('index')
    #     return redirect(next_page)
    # return render_template("login.html", title="Sign In", form=form)
    # username = request.json.get("user_id")
    # password = request.json.get("password")
    #
    # print(username, password)
    # if username is None or password is None:
    #     abort(404)
    if request.method == 'GET':
        if session.get('user_id'):
            user_id = session['user_id']
            return jsonify(status='OK',user_id=user_id,name='ximin chen') # name is hardcoded
        return jsonify(status='invalid session')
    if request.method == 'POST':
        username = request.json.get("user_id")
        password = request.json.get("password")
        user = User.query.filter_by(username=username, password_hash=password).first()
        if user:
            session['user_id'] = username
            session.permanent = True
            return jsonify(status="OK", user_id=username, name='ximin chen') # name is hardcoded
        abort(400)
    return jsonify(status='error')


@app.route('/logout')
def logout():
    session['user_id'] = None
    return redirect(url_for('index'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    # if current_user.is_authenticated:
    #     return redirect(url_for('index'))
    # form = RegistrationForm()
    # if form.validate_on_submit():
    #     user = User(username=form.username.data, email=form.email.data)
    #     user.set_pw(form.pw.data)
    #     db.session.add(user)
    #     db.session.commit()
    #     flash('Congratulations, you are a new registered user!')
    #     return redirect(url_for('login'))
    # return render_template('register.html', title='Register', form=form)
    username = request.json.get("user_id")
    password = request.json.get("password")
    # email = request.json.get('email') # miss Email address in the frontend now.
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    # return jsonify({'status': 'error'}), 400
    if username is None or password is None or first_name is None or \
            last_name is None:
        abort(400)
    if User.query.filter_by(username=username).first() is not None:
        abort(400)
    # miss Email address in the frontend now.
    user = User(username=username, password_hash=password,
                first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': "OK"})


#
# @app.route('/user/<username>')
# @login_required
# def user(username):
#     user = User.query.filter_by(username=username).first_or_404()
#     posts = [
#         {'author': user, 'body': 'Test post #1'},
#         {'author': user, 'body': 'Test post #2'}
#     ]
#     return render_template('user.html', user=user, posts=posts, title='Profile')

#
# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.utcnow()
#         db.session.commit()

#
# @app.route("/edit_profile", methods=['GET','POST'])
# def edit_profile():
#     form = EditProfileForm()
#     if form.validate_on_submit():
#         current_user.username = form.username.data
#         current_user.about_me = form.about_me.data
#         db.session.commit()
#         flash('Your changes have been saved.')
#         return redirect(url_for('edit_profile'))
#     elif request.method == 'GET':
#         form.username.data = current_user.username
#         form.about_me.data = current_user.about_me
#     return render_template('edit_profile.html', title='Edit Profile',
#                            form=form)

#
# @app.route('/follow/<username>')
# @login_required
# def follow(username):
#     user =User.query.filter_by(username=username).first()
#     if user is None:
#         flash(f'User {username} not found!')
#         return redirect(url_for('index'))
#     if user == current_user:
#         flash('You cannot follow yourself!')
#         return redirect(url_for('user'), username=username)
#     current_user.follow(user)
#     db.session.commit()
#     flash(f"You are following {username}")
#     return redirect(url_for('user', username=username))
#
#
# @app.route('/unfollow/<username>')
# @login_required
# def unfollow(username):
#     user = User.query.filter_by(username=username).first()
#     if user is None:
#         flash(f'User {username} not found.')
#         return redirect(url_for('index'))
#     if user == current_user:
#         flash('You cannot unfollow yourself!')
#         return redirect(url_for('user', username=username))
#     current_user.un_follow(user)
#     db.session.commit()
#     flash(f'You are not following {username}.')
#     return redirect(url_for('user', username=username))
#
#
# @app.route('/explore')
# @login_required
# def explore():
#     posts = Post.query.order_by(Post.timestamp.desc()).all()
#     return render_template('index.html', title='Explore', posts=posts)


@app.route('/nearby', methods=['GET', 'POST'])
def nearby():
    events_list = []
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    result = use_ticketmaster_api(lat=lat,lon=lon)
    if result:
        event_id = ''
        event_name = ''
        event_rating = ''
        event_address = ''
        event_img = ''
        event_url = ''
        event_distance = ''
        for event in result["_embedded"]["events"]:
            if "id" in event:
                event_id = event['id']
                # print(event_id)
            if "name" in event:
                event_name = event['name']
                # print(event_name)
            if "_embedded" in event:
                address_dict = event['_embedded']['venues'][0].get("address")
                address = ""
                for addr in address_dict:
                    address += address_dict[addr]
                event_address = address
                # print(event_address)
            if "images" in event:
                event_img = event['images'][0].get('url')
            if "url" in event:
                event_url = event.get('url')
            if "distance" in event:
                event_distance = event.get("distance",None)
            e = Event(event_id, event_name, event_rating,event_address,event_img,event_url,event_distance)
            events_list.append(e)
            json_data = json.dumps(events_list, default=lambda o:o.__dict__, indent=10)
        return Response(json_data)
    else:
        return None


@app.route('/search')
def search():
    events_list = []
    keyword = request.args.get("keyword")
    url = use_ticketmaster_api(apikey=app.config['TICKETMASTER_API_KEY'], keyword=keyword)
    with urllib.request.urlopen(url) as file:
        data = file.read()
        result = json.loads(data, encoding='utf-8')
    if result:
        event_id = ''
        event_name = ''
        event_rating = ''
        event_address = ''
        event_img = ''
        event_url = ''
        event_distance = ''


class Event(object):
    def __init__(self, id, name, rating, address, img_url, event_url, distance):
        self.id = id
        self.name = name
        self.rating = rating
        self.address = address
        self.img_url = img_url
        self.event_url = event_url
        self.distance = distance


def use_ticketmaster_api(**kwargs):
    if 'TICKETMASTER_API_KEY' not in app.config or \
            not app.config['TICKETMASTER_API_KEY']:
        raise Exception('Error: the Ticketmaster api is not configured.')
    auth = {'apikey':  app.config['TICKETMASTER_API_KEY']}
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    auth.update(kwargs)
    response = requests.get(url, params=auth)
    if response.status_code != 200:
        raise Exception('Error: Cannot find the exact api.')
    return json.loads(response.content,encoding="utf-8")

