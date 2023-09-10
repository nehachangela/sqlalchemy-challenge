import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

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
        f"Welcome to the Hawaii Climate Analysis API!<br/>"
        f"--------------------------------------<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/percipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date<br/>"
        f"/api/v1.0/start_date/end_date<br/>"
        f"--------------------------------------<br/>"
        f"For start_date queries please format:YYYY-MM-DD<br/>"
        f"For start_date/end_date queries please format:YYYY-MM-DD,YYYY-MM-DD"
    )

@app.route("/api/v1.0/percipitation")
def precipitation():

    # session (link) from Python to the DB
    session = Session(engine)

    # Query for percipitation for last year
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_ago).all()

    session.close()

    # Creating a dictionary from the raw data and append to a list of precipitation from perious year
    year_precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        year_precipitation.append(prcp_dict)

    return jsonify(year_precipitation)

@app.route("/api/v1.0/station")
def station():     
    # session (link) from Python to the DB
    session = Session(engine)

    # Query all staions 
    results = session.query(Station.station).all()

    session.close()

    # Convert list of tuples into normal list
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    #Query to find previous year data from most recent date in dataset
    year_ago = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for Most_active station on top
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
    filter(Measurement.station == Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    #Query for previous year temperature observed data
    results = session.query(Measurement.date, Measurement.tobs).\
    filter(Measurement.station == stations[0][0]).\
    filter(Measurement.date >= year_ago).all()

    session.close()

    tobs = list(np.ravel(results))

    return jsonify(tobs)

@app.route("/api/v1.0/<start_date>")
def Start (start_date):

    session = Session(engine)

    # Query for Most_active station on top
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
    filter(Measurement.station == Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    # Query to calculate minimum, maximum and average temperature from the start date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.station == stations[0][0]).\
    filter(Measurement.date >= start_date).all()

    session.close()

    # Creating a dictionary from the raw data and append to a list from start date 
    start_date_t = []
    for min, avg, max in results:
        start_dict = {}
        start_dict["TMIN"] = min
        start_dict["TAVG"] = avg
        start_dict["TMAX"] = max
        start_date_t.append(start_dict)

    return jsonify(start_date_t)

@app.route("/api/v1.0/<start_date>/<end_date>")
def Start_End (start_date, end_date):

    session = Session(engine)

    # Query to get most active station
    stations = session.query(Measurement.station, func.count(Measurement.station)).\
    filter(Measurement.station == Measurement.station).\
    group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()

    # Query to calculate minimum, maximum and average temperature from the start date to end date
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.station == stations[0][0]).\
    filter((Measurement.date >= start_date), (Measurement <= end_date)).all()

    session.close()

    # Creating a dictionary from the raw data and append to a list from start date to end date
    start_end_t = []
    for min, avg, max in results:
        start_end_dict = {}
        start_end_dict["TMIN"] = min
        start_end_dict["TAVG"] = avg
        start_end_dict["TMAX"] = max
        start_end_t.append(start_end_dict)

    return jsonify(start_end_t)

if __name__ == '__main__':
    app.run(debug=True)
