#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#


import json , sys
import dateutil.parser
import babel
import logging
from flask import Flask, render_template, request, Response, flash, redirect, url_for
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
  date = dateutil.parser.parse(str(value))
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
  venues = Venue.query.all()
  locations = set()
  for venue in venues:
    locations.add((venue.city, venue.state))
  for location in locations:
    data.append({"city" : location[0], "state": location[1], "venues":[] })
  for venue in venues:
    for i in data:
      if i["city"] == venue.city and i["state"] == venue.state:
        upcoming_shows = Show.query.join(Venue).filter(Venue.id == venue.id).filter(
                          Show.show_time > datetime.datetime.utcnow())
        i['venues'].append(
        {'id': venue.id, 'name': venue.name, 'num_upcoming_shows': upcoming_shows.count()})
        break
  print (data)

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
  upcoming_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time > datetime.datetime.utcnow())
  past_shows = Show.query.join(Venue).filter(Venue.id == venue_id).filter(Show.show_time <= datetime.datetime.utcnow())

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
  print(request.form)
  if request.method == 'POST':
    form = VenueForm()
    try:
      new_venue = Venue(
        name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        address=form.address.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_talent=form.seeking_talent.data,
        seeking_description=form.seeking_description.data)
      # on successful db insert, flash success
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      # on unsuccessful db insert, flash an error instead.
      db.session.rollback()
      flash('ERROR!!! ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

  else:
    print({sys.exc_info()})
    flash('Please do a re-check on form input')
  return redirect(url_for('index'))



@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  venue = Venue.query.get(venue_id)
  if request.method == 'DELETE':
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
  data = []
  artists = Artist.query.all()
  locations = set()
  for artist in artists:
    locations.add((artist.city, artist.state))
  for location in locations:
    data.append({"city" : location[0], "state": location[1], "artist":[] })
  for artist in artists:
    for i in data:
      if i["city"] == artist.city and i["state"] == artist.state:
        upcoming_shows = Show.query.join(Artist).filter(Artist.id == artist.id).filter(
                          Show.show_time > datetime.datetime.utcnow())
        i['artist'].append(
        {'id': artist.id, 'name': artist.name, 'num_upcoming_shows': upcoming_shows.count()})
        break
  print (data)

  return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # search for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
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
  upcoming_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time > datetime.datetime.utcnow())
  past_shows = Show.query.join(Artist).filter(Artist.id == artist_id).filter(Show.show_time <= datetime.datetime.utcnow())

  return render_template('pages/show_artist.html', artist=data, upcoming_shows=upcoming_shows, past_shows=past_shows)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist= Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm(request.form)
  if request.method == 'POST':
    try:
      artist.name = form.name.data
      artist.phone = form.phone.data
      artist.city = form.city.data
      artist.state = form.state.data
      artist.genres = form.genres.data
      artist.image_link = form.image_link.data
      artist.website_link = form.website_link.data
      artist.seeking_venue = form.seeking_venue.data
      artist.seeking_description = form.seeking_description.data

      db.session.add(artist)
      db.session.commit()
      flash('Artist ' + artist.name + ' was edited successfully')
    except:
      db.session.rollback()
      print(sys.exc_info())
      flash('Artist ' + artist.name + ' was not edited')
    finally:
      db.session.close()
  else:
    flash('Do a re-check on details edited')

  return redirect(url_for('show_artist', artist_id=artist_id))



@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue= Venue.query.get(venue_id)
  form = VenueForm(obj=venue)

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  venue = Venue.query.get(venue_id)
  form = VenueForm(request.form)
  if request.method == 'POST':
    try:
      venue.name = form.name.data
      venue.phone = form.phone.data
      venue.city = form.city.data
      venue.state = form.state.data
      venue.address = form.address.data
      venue.genres = form.genres.data
      venue.image_link = form.image_link.data
      venue.website_link = form.website_link.data
      venue.seeking_talent = form.seeking_talent.data
      venue.seeking_description = form.seeking_description.data

      db.session.add(venue)
      db.session.commit()
      flash('Venue ' + venue.name + ' was edited successfully')
    except:
      db.session.rollback()
      print (sys.exc_info())
      flash('Venue ' + venue.name + ' was not edited')

  else:
    flash('Do a re-check on details edited')

  return redirect(url_for('show_venue', venue_id=venue_id))



#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  print(request.form)
  if request.method == 'POST':
    form = ArtistForm()
    try:
      new_artist = Artist(name=form.name.data,
        city=form.city.data,
        state=form.state.data,
        phone=form.phone.data,
        image_link=form.image_link.data,
        genres=form.genres.data,
        facebook_link=form.facebook_link.data,
        website_link=form.website_link.data,
        seeking_venue=form.seeking_venue.data,
        seeking_description=form.seeking_description.data)
      # on successful db insert, flash success
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      # on unsuccessful db insert, flash an error instead.
      print(sys.exc_info())
      flash(sys.exc_info())
      db.session.rollback()
      flash('ERROR!!! ' + request.form['name'] + ' could not be listed.')
    finally:
      db.session.close()

  else:
    print({sys.exc_info()})
    flash('Please do a re-check on form input')
  return redirect(url_for('index'))


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data= []
  shows = db.session.query(Show).join(Venue, Artist).all()
  print (shows)

  for show in shows:
    data.append({
              'venue_id': show.venue.id,
              'venue_name': show.venue.name,
              'artist_id': show.artist.id,
              'artist_name': show.artist.name,
              'artist_image_link': show.artist.image_link,
              'start_time': show.show_time})
  print(data)


  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create', methods=['GET'])
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  print(request.form)
  form = ShowForm()
  if request.method == 'POST':
    try:
      new_show = Show(artist_id=form.artist_id.data,
                      venue_id=form.venue_id.data,
                      show_time=form.start_time.data)
      # on successful db insert, flash success
      db.session.add(new_show)
      db.session.commit()
      flash(f'Show {new_show.artist_id} of {new_show.venue_id}  was successfully listed!')
    except:
      # on unsuccessful db insert, flash an error instead.
      db.session.rollback()
      print(sys.exc_info())
      flash('ERROR!!! ' + request.form['artist_id'] + ' could not be listed.')
    finally:
      db.session.close()

  else:
    flash('Please do a re-check on form input')
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
