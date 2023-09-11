# Import the dependencies.

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
def Homepage():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():

    """Return the JSON representation of your dictionary"""

#    * Convert the query results from your precipitation analysis (i.e. retrieve only the last 12 months of data)
#       to a dictionary using date as the key and prcp as the value.
    
    last_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    query_result = session.query(Measurement.date, Measurement.prcp).\
        filter(Measurement.date >= last_year).\
        order_by(Measurement.date).all()
    session.close()

# Create a list of dicts with `date` and `prcp` as the keys and values
    precipitation = []
    for result in query_result:
        row = {}
        row[result[0]] = result[1]
        precipitation.append(row)

    return jsonify(precipitation)

#################################################
@app.route("/api/v1.0/stations")
def stations():

#     """Return a JSON list of stations from the dataset"""

    total_stations = session.query(Station.station).all()
    session.close()
    stations = list(np.ravel(total_stations))
    return jsonify(stations = stations)

#################################################
@app.route("/api/v1.0/tobs")
def tobs():
    """Return a JSON list of temperature observations for the previous year"""
#    * Query for the dates and temperature observations of the most-active station for the previous year of data

    last_twelve_months = dt.datetime(2017,8,23) - dt.timedelta(days=365)
    
    most_active_stations = session.query(Measurement.station, func.count(Measurement.station)).\
        group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).all()
    
    highest_station = most_active_stations[0][0]
    temp_obs_data = session.query(Measurement.date, Measurement.station, Measurement.tobs).\
        filter(Measurement.station == highest_station).filter(Measurement.date >= last_twelve_months).all()
    session.close()
    tobs = list(np.ravel(temp_obs_data))
    return jsonify(tobs = tobs)

#################################################
@app.route("/api/v1.0/<start>")
def start(start):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a 
#      specified start"""
#      For a specified start, calculate TMIN, TAVG, and TMAX for all the dates greater than or equal to the start date.
 
    start = dt.datetime.strptime(start, "%m%d%Y")
    start_temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()
    start_temp = list(np.ravel(start_temp_data))
    return jsonify(start_temp)

#################################################
@app.route("/api/v1.0/<start>/<end>")
def start_end(start,end):
    """Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a specified 
        start or start-end range."""
#       For a specified start date and end date, calculate TMIN, TAVG, and TMAX for the dates from the start date to 
#       the end date, inclusive.
       
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")
    start_end_temp_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).filter(Measurement.date <= end).all()
    session.close()
    start_end_temp = list(np.ravel(start_end_temp_data))
    return jsonify(start_end_temp)


if __name__ == '__main__':
    app.run(debug=True)
