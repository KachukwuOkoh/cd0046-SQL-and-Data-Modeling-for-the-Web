from turtle import backward
from flask_sqlalchemy import SQLAlchemy
import datetime


db = SQLAlchemy()


class Venue(db.Model):
    __tablename__ = 'venues'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String(120)))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120), default=None)
    seeking_talent = db.Column(db.Boolean(), default=False)
    seeking_description = db.Column(db.String(200), default=None)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    shows = db.relationship('Show', backref='venue', lazy=True)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate


class Artist(db.Model):
    __tablename__ = 'artists'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String(120)))
    image_link = db.Column(db.String(500))
    seeking_venue = db.Column(db.Boolean(), default=False)
    website_link = db.Column(db.String(120), default=None)
    facebook_link = db.Column(db.String(120))
    seeking_description = db.Column(db.String(200), default=None)
    date_added = db.Column(db.DateTime(), default=datetime.datetime.utcnow())
    shows = db.relationship('Show', backref='artist', lazy=True)


    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artists.id'))
    venue_id = db.Column(db.Integer, db.ForeignKey('venues.id'))
    show_time = db.Column(db.DateTime(), nullable=False)