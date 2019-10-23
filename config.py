import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    TICKETMASTER_API_KEY = 'ekOl1mWCrvka6hMLAxMbRnhHHGbNFFEy'
    HOST = "https://app.ticketmaster.com"
    PATH = "/discovery/v2/events.json"
    DEFAULT_KEYWORD = "event"
    DEFAULT_RADIUS = 50

