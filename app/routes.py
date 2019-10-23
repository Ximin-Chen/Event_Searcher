from functools import wraps

from app import app, db, Config
from flask import render_template, flash, redirect, url_for
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Event
from flask import request, abort, session
from werkzeug.urls import url_parse
from datetime import datetime
import urllib.request
import json

from flask import jsonify, Response

HOST = Config.HOST
PATH = Config.PATH
API_KEY = Config.TICKETMASTER_API_KEY


def login_require(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                abort(401)
            return func(*args, **kwargs)
        return decorated_function


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_require
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
        user = User.query.filter_by(username=username).first()
        if user:
            if user.password_hash == password:
                session['user_id'] = username
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


@app.route('/search')
def search():
    url = f'''{HOST}{PATH}?apikey={API_KEY}&keyword=San%20Jose'''
    with urllib.request.urlopen(url) as file:
        page = file.read()
        data = json.loads(page, encoding="utf-8")

    print(data)
    eventsJSON = []

    if data["_embedded"]:
        for event in data["_embedded"]["events"]:
            e = Event()
            if event.get('id'):
                e.id = event.get('id')
            if event.get('name'):
                e.name = event.get('name')
            if event.get('rating'):
                e.rating = event.get("rating", None)
            if event.get('_embedded'):
                address_dict = event.get('_embedded').get('venues')[0].get("address")
                address = ""
                for addr in address_dict:
                    address += address_dict[addr]
                e.address = address
            if event.get('images'):
                e.img_url = event.get('images')[0].get('url')
            if event.get('url'):
                e.event_url = event.get('url')
            if event.get('distance'):
                e.distance = event.get("distance", None)
            """
            db.session.add(e)
            db.session.commit()
            """
            eventsJSON.append(event)

    """data["_embedded"]["events"]["images"]   """
    return Response(json.dumps(eventsJSON, indent=4, sort_keys=True))


