#################################################
# Import Dependencies
#################################################

import numpy as np
import pandas as pd
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect = True)

Station = Base.classes.station
Measurement = Base.classes.measurement

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """All available api routes"""
    return(
         """<html>
                <h2>Available Routes</h2>
                <ul>
                    <li> <a href = "api/v1.0/precipitation">/api/v1.0/precipitation</a></li>
                    <li> <a href = "/api/v1.0/stations">/api/v1.0/stations</a></li>
                    <li> <a href = "/api/v1.0/tobs">/api/v1.0/tobs</a></li>
                    <li> <a href = "/api/v1.0/2017-01-01">/api/v1.0/start<a/></li>
                    <li> <a href = "/api/v1.0/2016-11-11/2017-11-11">/api/v1.0/start/end<a/></li>
                    
                </ul>        
       
    """)
#<input type="text" name = "name">/<input type="text" name = "name">    
@app.route("/api/v1.0/precipitation")
def precipitation():
    #Create a session from Python to the DataBase
    session = Session(engine)
    
    """Return a list of all dates and precipitation"""
    # Query all precipitation and the date recorded    
    results = pd.DataFrame(session.query(Measurement.date,Measurement.prcp).all())
    session.close()
    
    # Convert list of tuples into Dictionary
    dictionary = {}
    for i in range(0,len(results)):
        dictionary.update({results.date[i]:results.prcp[i]})
    return jsonify(dictionary)

@app.route("/api/v1.0/stations")
def stations():
    # Create our session from Python to the Database
    session = Session(engine)

    """Return a list of all station names"""
    # Query all stations
    results = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    # Convert list of tuples into normal list
   
    return jsonify(list(results))
    
@app.route("/api/v1.0/tobs")
def temperature():
    # Create our session from Python to the Database
    session = Session(engine)

    """Return a list of all station names"""
    # Query the dates and temperature observations of the most active station for the last year
    last_day = session.query(Measurement.date).order_by(Measurement.id.desc()).first()
    last_day = str(last_day).split("'")[1]
    last_year = dt.datetime.strptime(last_day, "%Y-%m-%d")-dt.timedelta(365)
    
    
    results = session.query(Measurement.station,func.count(Measurement.tobs))\
                            .group_by(Measurement.station)\
                            .order_by(func.count(Measurement.station).desc())\
                            .first()
    top_result = session.query(Measurement.date,Measurement.tobs)\
                            .filter(Measurement.date>last_year)\
                            .filter(Measurement.station ==results[0])

    session.close()

    # Convert list of tuples into normal list
    
    return jsonify(list(top_result))    

    
@app.route("/api/v1.0/<start>")
def start(start=None):
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).all()
    session.close()

    return jsonify(list(results)) 

    
   
@app.route("/api/v1.0/<start>/<end>")
def start_end(start = None, end= None):
    
    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date >= start).\
        filter(Measurement.date <= end).all()
    session.close()
    

    return jsonify(list(results))     
if __name__==  '__main__':
    app.run(debug=True)

