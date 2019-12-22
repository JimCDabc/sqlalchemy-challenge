import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect

from flask import Flask, jsonify


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
        f"Available Routes:<br/>"
        f"/                         (Welcome screen)<br/>"
        f"/api/v1.0/precipitation   (Dictionary of Precip by Date)<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
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
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset."""
    # Query all passengers
    #sel = [Station.id, Station.station, Station.name, Station.latitude, Station.longitude, Station.elevation]
    sel = [Station.station]
    results = session.query(*sel).all()
    session.close()

    all_stations = list(np.ravel(results))
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    """Query for the dates and temperature observations from a year from the last data point.
    Return a JSON list of Temperature Observations (tobs) for the previous year."""


@app.route("/api/v1.0/<start>")
def start():
    """Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.

    When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.

    When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive."""

@app.route("/api/v1.0/<start>/<end>")
def start_end():
    # Do something
    print("TBD")
    
if __name__ == '__main__':
    app.run(debug=True)
