import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify

import datetime as dt
from dateutil.relativedelta import relativedelta

# Note importing from juptyer notebook will take additional work.  
# so just duplicated code of some functions below
    # import ipynb
    # from climate import lastDateOfData, yearPastDate, calc_temps, daily_normals


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f'<h3>Available Routes:</h3>'
        f'<table><tbody>'
        f'<tr><td align=right><a href="/">~/</a></td><td> -- </td><td>Welcome Screen</td></tr>'
        f'<tr><td align=right><a href="/api/v1.0/precipitation">~/api/v1.0/precipitation </a></td><td> -- </td><td>Dictionary of average precipitation across stations keyed by date</td> </tr>'
        f'<tr><td align=right><a href="/api/v1.0/stations">~/api/v1.0/stations</a></td><td> -- </td><td>List of Stations </td> </tr>'
        f'<tr><td align=right><a href="/api/v1.0/tobs">~/api/v1.0/tobs</a></td><td> -- </td><td>List of temperature observations from final 12 months of data </td> </tr>'
        f'<tr><td align=right><a href="/api/v1.0/&lt;start&gt;">~/api/v1.0/&lt;start&gt;</a></td><td> -- </td><td>Min, Avg, & Max Temperature from start date on </td> </tr>'
        f'<tr><td align=right><a href="/api/v1.0/&lt;start&gt;/&lt;end&gt;">~/api/v1.0/&lt;start&gt;/&lt;end&gt;</a></td><td> -- </td><td>Min, Avg, & Max Temperature between start & end dates</td> </tr>'
        f'</tbody></table>'
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    print('/api/v1.0/precipitation route called')
    
    """Convert the query results to a Dictionary using date as the key and prcp as the value.
        Return the JSON representation of your dictionary."""

    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query all passengers
    sel = [Measurement.date, func.avg(Measurement.prcp)]
    results = session.query(*sel).group_by(Measurement.date)

    prcps_dict = {}
    for date, prcp in results:
        prcps_dict[date] = prcp

    session.close()

    # Convert dictionare of date: sumPrecip
    return jsonify(prcps_dict)

@app.route("/api/v1.0/stations")
def stations():
    print('/api/v1.0/stations route called')
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all stations
    #sel = [Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    sel = [Station.station]
    results = session.query(*sel).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print('/api/v1.0/tobs route called')
    
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""

    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Calculate dates for last year of data
    lastDateStr = session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0]
    lastDate = dt.datetime.strptime(lastDateStr, '%Y-%m-%d').date()
    yearAgoDate = lastDate - dt.timedelta(minutes=525600)

    sel = [Measurement.date, Measurement.tobs]
    tobsResults = session.query(*sel).filter(Measurement.date >= yearAgoDate).all()
    session.close()
 
    all_tobs = []
    for date, temp in tobsResults :
        tobs_dict = {}
        tobs_dict["date"] = date
        tobs_dict["tobs"] = temp
        all_tobs.append(tobs_dict)
        
    return jsonify(all_tobs)

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print(f'start_end route: /api/v1.0/{start}/{end} route called')

    # Do something
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    for a given start or start-end range.
    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

    try :
        startDate = dt.datetime.strptime(start, '%Y-%m-%d').date()
        endDate = dt.datetime.strptime(end, '%Y-%m-%d').date()
    except ValueError as err:
        print(err)
        return jsonify([str(err)])

    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= startDate).filter(Measurement.date <= endDate).all()
    session.close()

    print(results)
    resultTemps = []
    for tmin, tavg, tmax in results :
        temps_dict = {}
        temps_dict["start"] = start
        temps_dict["end"] = end
        temps_dict["tmin"] = tmin
        temps_dict["tavg"] = tavg
        temps_dict["tmax"] = tmax
        resultTemps.append(temps_dict)
    return jsonify(resultTemps)

    
@app.route("/api/v1.0/<start>")
def start(start):
    print(f'start route: /api/v1.0/{start} route called')    
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature 
    for a given start or start-end range.
    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date."""

    try:
        startDate = dt.datetime.strptime(start, '%Y-%m-%d').date()
    except ValueError as err:
        print(err)
        return jsonify([str(err)])
    
    session = Session(engine)
    sel = [func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)]
    results = session.query(*sel).filter(Measurement.date >= startDate).all()
    session.close()

    print(results)

    resultTemps = []
    for tmin, tavg, tmax in results :
        temps_dict = {}
        temps_dict["start"] = start
        temps_dict["tmin"] = tmin
        temps_dict["tavg"] = tavg
        temps_dict["tmax"] = tmax
        resultTemps.append(temps_dict)
    return jsonify(resultTemps)

    
if __name__ == '__main__':
    app.run(debug=True)
