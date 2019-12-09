from app import app,db
from flask import render_template, flash, redirect, url_for, abort
from app.forms import LoginForm, RegistrationForm, EditProfileForm, PostForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User, Post, Event, Favourite
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
            return jsonify(status='OK',user_id=userID,name=userID)
        return jsonify(status='invalid session')

    if request.method == 'POST':
        username = request.json.get("user_id")
        password = request.json.get("password")
        user = User.query.filter_by(username=username, password_hash=password).first()
        if user:
            session['user_id'] = username
            session.permanent = True
            return jsonify(status="OK", user_id=username, name=username)  # name is hardcoded
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
                firstname=first_name, lastname=last_name)
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
    userID= request.args.get('user_id')
    latlong = lat + "," + lon
    result = use_ticketmaster_api(latlong=latlong)
    if result:
        event_id = ''
        event_name = ''
        event_category = ''
        event_address = ''
        event_img = ''
        event_url = ''
        event_date = ''
        event_description = ''
        favorite =''
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
                city = event['_embedded']['venues'][0]['city'].get("name")
                state = event['_embedded']['venues'][0]['state'].get("name")
                event_address = address + ", " + city + ", " + state
            if "classifications" in event:
                category = event['classifications'][0]['segment'].get("name")
                event_category = category
            if "images" in event:
                event_img = event['images'][0].get('url')
            if "url" in event:
                event_url = event.get('url')
            if "dates" in event:
                event_date = event['dates']['start'].get("localDate", None)
            if "promoter" in event:
                event_description = event['promoter'].get("description", None)
            fav_events = Favourite.query.filter_by(user_id=userID)
            for fav_event in fav_events:
                if fav_event.event_id == event_id:
                    favorite = True
            e = Events(event_id, event_name, event_category, event_address, event_img, event_url,
                       event_date, event_description,favorite)
            favorite = ''
            events_list.append(e)

            exists = Event.query.filter_by(id=event_id).first()
            if not exists:
                evt = Event(id=event_id, name=event_name, address=event_address, img_url=event_img,
                            category=event_category, event_url=event_url, date=event_date,
                            description=event_description)
                db.session.add(evt)
                db.session.commit()
        json_data = json.dumps(events_list, default=lambda o: o.__dict__, indent=10)
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
    userID = request.args.get('user_id')
    result = use_ticketmaster_api(keyword=keyword)
    if result:
        event_id = ''
        event_name = ''
        event_category = ''
        event_address = ''
        event_img = ''
        event_url = ''
        event_date = ''
        event_description = ''
        favorite = ''
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
                city = event['_embedded']['venues'][0]['city'].get("name")
                state = event['_embedded']['venues'][0]['state'].get("name")
                event_address = address + ", " + city + ", " + state
            if "classifications" in event:
                category = event['classifications'][0]['segment'].get("name")
                event_category = category
            if "images" in event:
                event_img = event['images'][0].get('url')
            if "url" in event:
                event_url = event.get('url')
            if "dates" in event:
                event_date = event['dates']['start'].get("localDate",None)
            if "promoter" in event:
                event_description = event['promoter'].get("description", None)
            fav_events = Favourite.query.filter_by(user_id=userID)
            for fav_event in fav_events:
                if fav_event.event_id == event_id:
                    favorite = True
            e = Events(event_id, event_name, event_category, event_address, event_img, event_url,
                       event_date, event_description, favorite)
            events_list.append(e)
            favorite = ''
            exists = Event.query.filter_by(id=event_id).first()
            if not exists:
                evt = Event(id=event_id, name=event_name, address=event_address, img_url=event_img,
                            category=event_category, event_url=event_url,
                            description=event_description, date=event_date)
                db.session.add(evt)
                db.session.commit()
        json_data = json.dumps(events_list, default=lambda o: o.__dict__, indent=10)
        return Response(json_data)
    else:
        return None


@app.route('/detail', methods=['GET'])
def detail():
    if not session:
        abort(403)
    event_id = request.args.get('item_id')
    event = Event.query.filter_by(id=event_id).first()
    if event:
        return jsonify(status='OK', id=event.id, name=event.name, img_url=event.img_url, category=event.category,
                       address=event.address, event_url=event.event_url, date=event.date, description=event.description)
    return jsonify(status='invalid session')


@app.route('/history', methods=['GET'])
def history():
    if not session:
        abort(403)
    userID = request.args.get('user_id')
    print(userID)
    if request.method == 'GET':
        fav_list = []
        fav_dict = Favourite.query.filter_by(user_id=userID)
        if fav_dict:
            event_id = ''
            event_name = ''
            event_category = ''
            event_address = ''
            event_img = ''
            event_url = ''
            event_date = ''
            event_description = ''
            favorite = ''
            for fav in fav_dict:
                event_id = fav.event_id
                event_name = Event.query.filter_by(id=event_id).first().name
                event_category = Event.query.filter_by(id=event_id).first().category
                event_address = Event.query.filter_by(id=event_id).first().address
                event_img = Event.query.filter_by(id=event_id).first().img_url
                event_url = Event.query.filter_by(id=event_id).first().event_url
                event_date = Event.query.filter_by(id=event_id).first().date
                event_description = Event.query.filter_by(id=event_id).first().description
                favorite = True
                e = Events(event_id, event_name, event_category, event_address, event_img, event_url, event_date,
                           event_description, favorite)
                fav_list.append(e)
        json_data = json.dumps(fav_list, default=lambda o: o.__dict__, indent=10)
        return Response(json_data)
    return

@app.route('/favorite', methods=['POST', 'DELETE'])
def favorite():
    if not session:
        abort(403)
    username = request.json.get("user_id")
    fav_dict = request.json.get("favorite")
    if request.method == 'POST':
        for favorite in fav_dict:
            fav = Favourite(user_id=username, event_id=favorite)
            db.session.add(fav)
            db.session.commit()
        return jsonify(result='SUCCESS')
    if request.method == 'DELETE':
        for favorite in fav_dict:
            fav = Favourite.query.filter_by(user_id=username, event_id=favorite).first()
            db.session.delete(fav)
            db.session.commit()
        return jsonify(result='SUCCESS')
    return jsonify(result='FAILURE')




class Events(object):
    def __init__(self, id, name, category, address, img_url, event_url, date, description, favorite):
        self.id = id
        self.name = name
        self.category = category
        self.address = address
        self.img_url = img_url
        self.event_url = event_url
        self.date = date
        self.favorite = favorite
        self.description = description


def use_ticketmaster_api(**kwargs):
    if 'TICKETMASTER_API_KEY' not in app.config or \
            not app.config['TICKETMASTER_API_KEY']:
        raise Exception('Error: the Ticketmaster api is not configured.')
    auth = {'apikey':  app.config['TICKETMASTER_API_KEY'], 'radius': app.config['DEFAULT_RADIUS']}
    url = "https://app.ticketmaster.com/discovery/v2/events.json"
    auth.update(kwargs)
    print(auth)
    response = requests.get(url, params=auth)
    if response.status_code != 200:
        raise Exception('Error: Cannot find the exact api.')
    return json.loads(response.content,encoding="utf-8")




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