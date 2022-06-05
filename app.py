#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
import logging
from flask import Flask, render_template, request, Response, flash, redirect, url_for
import flask
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
from models import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  recent_artist = Artist.query.order_by(Artist.date_added).limit(10).all()
  recent_venue = Venue.query.order_by(Venue.date_added).limit(10).all()
  return render_template('pages/home.html',
                          recent_artist=recent_artist,
                          recent_venue=recent_venue)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data = []
  # venue = Venue.query.all()
  # locations = set()
  # for venue in venues:
  #   locations.add((venue.city, venue.state))
  # for location in locations:
  #   data.append({"city" : location[0], "state": location[1], "venues":[] })
  # for venue in venues:
  #   for i in data:
  #     if i["city"] == venue.city and i["state"] == venue.state:



  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_word = request.form.get('search_term')
  search_result = (Venue.query.filter((Venue.city.ilike('%'+ search_word +'%') |
                                        Venue.name.ilike('%'+ search_word +'%') |
                                        Venue.state.ilike('%'+ search_word +'%'))))

  return render_template('pages/search_venues.html', results=search_result, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

  data = Venue.query.get(venue_id)
  upcoming_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time > datetime.utcnow())
  past_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time <= datetime.utcnow())

  return render_template('pages/show_venue.html', venue=data, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():

  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  trace = request.form.get
  deets = VenueForm(request.form)
  if deets.validate():
    try:
      new_venue =Venue(name=trace('name'), city=trace('city'),
                            state=trace('state'), address=trace('address'),
                            phone=trace('phone'), image_link=trace('image_link'),
                            genres=request.form.getlist('genres'),
                            facebook_link=trace('facebook_link'),
                            website_link=trace('website_link'),
                            seeking_talent=trace.seeking_talent.data,
                            seeking_description=trace('seeking_description'))
      db.session.add(new_venue)
      db.session.commit()
      # on successful db insert, flash success
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      # on unsuccessful db insert, flash an error instead.
      db.session.rollback()
      flash('ERROR!!!' + request.form['name'] + ' could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Please do a re-check on form input')
    return redirect(url_for('index'))



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  venue = Venue.query.get(venue_id)
  try:
    db.session.delete(venue)
    db.session.commit()
    flash(f'Venue {venue.name} has been deleted')
  except:
    db.session.rollback()
    flash(f'Venue {venue.name} could not been deleted')

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  return render_template('pages/artists.html', artists=Artist.query.all())


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  search_word = request.form.get('search_term')
  search_result = (Artist.query.filter((Artist.city.ilike('%'+ search_word +'%') |
                                        Artist.name.ilike('%'+ search_word +'%') |
                                        Artist.state.ilike('%'+ search_word +'%'))))

  return render_template('pages/search_artists.html', results=search_result, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  data = Artist.query.get(artist_id)
  upcoming_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time > datetime.utcnow())
  past_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time <= datetime.utcnow())

  return render_template('pages/show_artist.html', artist=data, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist= Artist.query.get(artist_id)

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.phone.data = artist.phone
  form.genres.data = artist.genres
  form.image_link.data = artist.image_link
  form.seeking_venue.data = artist.seeking_venue
  form.website_link.data = artist.website_link
  form.facebook_link.data = artist.facebook_link
  form.seeking_description = artist.seeking_description

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.get(artist_id)
  deets = ArtistForm(request.form)
  if deets.validate():
    artist.name = deets.name.data
    artist.city = deets.city.data
    artist.state = deets.state.data
    artist.phone = deets.phone.data
    artist.genres = deets.genres.data
    artist.image_link = deets.image_link.data
    artist.seeking_venue = deets.seeking_venue.data
    artist.website_link = deets.website_link.data
    artist.facebook_link = deets.facebook_link.data
    artist.seeking_description = deets.seeking_description.data

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)

  form.name.data = venue.name
  form.phone.data = venue.phone
  form.city.data = venue.city
  form.state.data = venue.state
  form.address.data = venue.address
  form.genres.data = venue.genres
  form.image_link.data = venue.image_link
  form.website_link.data = venue.website_link
  form.seeking_talent.data = venue.seeking_talent
  form.seeking_description = venue.seeking_description

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  deets = VenueForm(request.form)
  if deets.validate():
    venue.name = deets.name.data
    venue.phone = deets.phone.data
    venue.city = deets.city.data
    venue.state = deets.state.data
    venue.address = deets.address.data
    venue.genres = deets.genres.data
    venue.image_link = deets.image_link.data
    venue.website_link = deets.website_link.data
    venue.seeking_talent = deets.seeking_talent.data
    venue.seeking_description = deets.seeking_description.data
    db.session.commit()
    return redirect(url_for('show_venue', venue_id=venue_id))
  else:
    flash(f'Do a re-check on submissions')
    return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  trace = request.form.get
  deets = ArtistForm(request.form)
  if deets.validate():
    try:
      new_artist = Artist(name=trace('name'), city=trace('city'),
                            state=trace('state'), phone=trace('phone'),
                            genres=request.form.getlist('genres'),
                            image_link=trace('image_link'),
                            seeking_venue=trace('seeking_venue'),
                            website_link=trace('website_link'),
                            facebook_link=trace('facebook_link'),
                            seeking_description=trace('seeking_description'))
      db.session.add(new_artist)
      db.session.commit()
      # on successful db insert, flash success
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('ERROR!!!' + request.form['name'] + ' could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Please do a re-check on form input')
    return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data=[{
    "venue_id": 1,
    "venue_name": "The Musical Hop",
    "artist_id": 4,
    "artist_name": "Guns N Petals",
    "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "start_time": "2019-05-21T21:30:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 5,
    "artist_name": "Matt Quevedo",
    "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "start_time": "2019-06-15T23:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-01T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-08T20:00:00.000Z"
  }, {
    "venue_id": 3,
    "venue_name": "Park Square Live Music & Coffee",
    "artist_id": 6,
    "artist_name": "The Wild Sax Band",
    "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "start_time": "2035-04-15T20:00:00.000Z"
  }]
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  trace = request.form.get
  deets = ArtistForm(request.form)
  if deets.validate():
    try:
      show = Show(artist_id=trace('artist_id'), venue_id=trace('venue_id'),
                  show_time=trace('start_time'))
      db.session.add(show)
      db.session.commit()
      # on successful db insert, flash success
      flash('Show was successfully listed!')
    except:
      db.session.rollback()
      # on unsuccessful db insert, flash an error instead.
      flash('ERROR! Show could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Please do a re-check on form before input')
    return redirect(url_for('index'))

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
