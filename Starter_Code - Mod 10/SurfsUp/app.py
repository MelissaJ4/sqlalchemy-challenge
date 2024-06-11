# Import the dependencies.
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt

# Python SQL toolkit and Object Relational Mapper
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, text, inspect, func

#################################################
# Database Setup
#################################################

# reflect an existing database into a new model
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()

# Save references to each table
Base.prepare(autoload_with=engine)
Base.classes.keys()

hi_station = Base.classes.station
hi_measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################

# Dictionary of needed tables


#Create an app, being sure to pass __name__
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# Define what to do when a user hits the index route
@app.route("/")
def home():
    # List all available api routes.
    return (
    f"Welcome to the Climate App homepage! Get information about precipitation in Hawaii!<br/>"
    f"For specific information, include these endings in the URL bar:<br/>"
    f"Precipitation = /api/v1.0/precipitation<br/>"
    f"Stations = /api/v1.0/stations<br/>"
    f"Tobs = /api/v1.0/tobs<br/>"
    f"start = /api/v1.0/8-23-2016 remove - when choosing a date, MMDDYYYY <br/>"
    f"start_end = /api/v1.0/8-23-2016/8-23-2017  remove - when choosing a date, MMDDYYYY <br/>"
    
)

# Define what to do when a user hits the different routes
@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    yearly_dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    results = session.query(hi_measurement.date, hi_measurement.prcp).filter(hi_measurement.date >= yearly_dates)
   
    # Returns json with date as key and value as precipitation
    # Only returns last year of data

    precipitation = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict[date] = prcp
        precipitation.append(prcp_dict)
     
    session.close()

                 
    return jsonify(precipitation)
   

@app.route("/api/v1.0/stations")
def stations():
    
   # Create our session (link) from Python to the DB
    session = Session(engine)
    
    # Return the station data as json
    # Query Data from all the stations

    results = session.query(hi_station.station).all()


    session.close()
    
    all_stations = list(np.ravel(results))

    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():

    # Create our session (link) from Python to the DB
    session = Session(engine)
    

    # Return the tobs as json
    # jsonified data for the most active station (519281)

    most_active = 'USC00519281'
    
    # Return data from last year of data
    yearly_dates = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    active_results = session.query(hi_measurement.tobs).filter(hi_measurement.date >= yearly_dates).filter_by(station = most_active).all()
    
    session.close()

    tobs = list(np.ravel(active_results))
    return jsonify(tobs)

@app.route("/api/v1.0/<start>")
def start(start):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Accepts start date as parameter from URL
    # Returns min, max, avg temps calculated from given start date to end of the dataset
    start = dt.datetime.strptime(start, "%m%d%Y")
    
    temp_summary = session.query(func.min(hi_measurement.tobs), func.max(hi_measurement.tobs), func.avg(hi_measurement.tobs))\
        .filter(hi_measurement.date >= start).\
        all()
    
    lowest_temp, highest_temp, avg_temp = temp_summary[0]
    summary_of_weather = {"Minimum": lowest_temp,
     "Maximum": highest_temp,
     "Average": avg_temp
    }
    
    session.close()

    return jsonify(summary_of_weather)


@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Accepts start and end date as parameter from URL
    # Returns min, max, avg temps from given start date to given end date (Aug '16-Aug '17)
    start = dt.datetime.strptime(start, "%m%d%Y")
    end = dt.datetime.strptime(end, "%m%d%Y")

    temp_summary = session.query(func.min(hi_measurement.tobs), func.max(hi_measurement.tobs), func.avg(hi_measurement.tobs))\
        .filter(hi_measurement.date >= start and hi_measurement.date <= end).\
        all()
    
    lowest_temp, highest_temp, avg_temp = temp_summary[0]
    summary_of_weather = {"Minimum": lowest_temp,
     "Maximum": highest_temp,
     "Average": avg_temp
    }
    
    
    session.close()

    return jsonify(summary_of_weather)

    session.close()

if __name__ == "__main__":
    app.run(debug=True)

