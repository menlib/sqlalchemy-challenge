# Import the dependencies.
import numpy as np
import datetime as dt
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################


# create engine to hawaii.sqlite
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Station = Base.classes.station
Measurement = Base.classes.measurement 

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
    return (
        f"Welcome to the Climate Analysis API!<br>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/<start><br/>"
        f"/api/v1.0/<start>/<end><br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    # Year of the last entry
    recent_date = session.query(func.max(Measurement.date)).first()
    # One year before the last entry
    year_before = dt.date(2017,8,23) - dt.timedelta(days=365)
    # Precipitation scores data within the last year
    one_year = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= year_before).all()
    precip = {date:prcp for date, prcp in one_year}
    session.close()
    # Create list of tuples into normal list 
    precip_list = list(np.ravel(one_year))
    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
     
    session = Session(engine)   
    # Query list of stations
    total_stations = session.query(func.count(Station.station)).all()  
    total_stations = str(total_stations)
    session.close()
    #Convert list of tuples into normal list
    stations_list =list(np.ravel(total_stations))
    return jsonify(stations_list)

@app.route("/api/v1.0/tobs")
def tobs():
# Calculate the date one year from the last date in database toreturn temp observation for previous year.
    year_before = dt.date(2017,8,23) - dt.timedelta(days=365)

    session = Session(engine)  
    # Query temperature observations (tobs) of the most active station
    temp_observations= session.query(Measurement.tobs).\
    filter(Measurement.station =='USC00519281'). \
    filter(Measurement.date >=year_before).all()
    session.close() 
    # Convert list of tuples into normal list
    tobs_list = list(np.ravel(temp_observations)) 
    return jsonify(tobs_list = tobs_list)


@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")

#Calculate temperature statistics based on start and end dates
def stats (start=None, end=None):
    
    temp_aggregates =[func.min(Measurement.tobs), func.max(Measurement.tobs),func.avg(Measurement.tobs)]
    
        # Calculate temp min, temp max, temp average for all the dates greater than or equal to the start date
    results = session.query(*temp_aggregates).filter(Measurement.date>=start).all()

    #Convert list of tupules into normal list
    temp_data=list(np.ravel(results))
    session.close()
    return jsonify(temp_data)

    # Calculate temp min, temp max, temp average for the dates from the start date to the end date, inclusive.
    results = session.query(*temp_aggregates).\
    filter (Measurement.date>=start).\
    filter(Measurement.date<=end).all()

    #Convert list of tupules into normal list
    temp_data=list(np.ravel(results))
    session.close()
    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)