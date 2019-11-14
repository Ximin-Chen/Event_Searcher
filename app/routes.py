from app import app,db
from flask import render_template, flash, redirect, url_for, abort
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post
from flask import request, session
from werkzeug.urls import url_parse
from datetime import datetime
import json, requests
from flask import jsonify, Response



@app.route('/')
@app.route('/index', methods=['GET', 'POST'])
def index():
    return render_template("index.html", title='Home Page')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        if session.get('user_id'):
            userID = session['user_id']
            return jsonify(status='OK',user_id=userID,name='olivia')
        return jsonify(status='invalid session')

    if request.method == 'POST':
        username = request.json.get("user_id")
        password = request.json.get("password")
        user = User.query.filter_by(username=username, password_hash=password).first()
        if user:
            session['user_id'] = username
            session.permanent = True
            return jsonify(status="OK", user_id=username, name='ximin chen')  # name is hardcoded
        abort(400)
    return jsonify(status='error')



@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('index'))


@app.route('/register',methods=['POST'])
def register():
    username = request.json.get("user_id")
    password = request.json.get("password")
    # email = request.json.get('email') # miss Email address in the frontend now.
    first_name = request.json.get("first_name")
    last_name = request.json.get("last_name")
    if User.query.filter_by(username=username).first() is not None:
        return jsonify({'status': "error"})
    # miss Email address in the frontend now.
    user = User(username=username, password_hash=password,
                first_name=first_name, last_name=last_name)
    db.session.add(user)
    db.session.commit()
    return jsonify({'status': "OK"})


@app.route('/nearby', methods=['GET', 'POST'])
def nearby():
    if not session:
        abort(403)
    events_list = []
    lat = request.args.get('lat')
    lon = request.args.get('lon')
    print(lat, lon);
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
            if "name" in event:
                event_name = event['name']
            if "_embedded" in event:
                address_dict = event['_embedded']['venues'][0].get("address")
                address = ""
                for addr in address_dict:
                    address += address_dict[addr]
                event_address = address
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


# Used to retrieving/updating user info
@app.route('/user', methods=['GET', 'POST'])
def user():
    # Repurposed from /login route
    if request.method == 'GET':
        if session.get('user_id'):
            user_id = session['user_id']
            user = User.query.filter_by(username=user_id).first()
            return jsonify(status='OK', user_id=user_id, name=user_id, last_seen=user.last_seen, about_me=user.about_me,
                           first_name=user.firstname, last_name=user.lastname)
        return jsonify(status='invalid session')
    if request.method == 'POST':
        """ 

        TO IMPLEMENT FOR UPDATING USER INFO
        """
        if session.get('user_id'):
            user_id = session['user_id']
            user = User.query.filter_by(username=user_id).first()

            about_me = request.json.get("about_me")
            user.about_me = about_me or "Empty"
            db.session.commit()

            return jsonify(status='OK', user_id=user_id, name=user_id, last_seen=user.last_seen, about_me=user.about_me,
                           first_name=user.firstname, last_name=user.lastname)
        return jsonify(status='invalid session')
    return jsonify(status='error')


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




@app.route('/search', methods=['GET', 'POST'])
def search():
    if not session:
        abort(403)
    events_list = []
    keyword = request.args.get('keyword')
    result = use_ticketmaster_api(keyword=keyword)
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
            if "name" in event:
                event_name = event['name']
            if "_embedded" in event:
                address_dict = event['_embedded']['venues'][0].get("address")
                address = ""
                for addr in address_dict:
                    address += address_dict[addr]
                event_address = address
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


# @app.route('/detail', methods=['GET'])
# def detail():
#     if not session:
#         abort(403)
#     event_id = request.args.get('item_id')
#     event = Event.query.filter_by(id=event_id).first()
#     return jsonify(status='OK', id=event.id, name=event.id, img_url=event.img_url)
#         # return jsonify(status='invalid session')




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


# @app.route('/user', method=['GET'])
# def user():
#
#     return render_template('user.html')


# @app.before_request
# def before_request():
#     if current_user.is_authenticated:
#         current_user.last_seen = datetime.utcnow()
#         db.session.commit()
#
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