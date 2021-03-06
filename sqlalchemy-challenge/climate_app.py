import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import pandas as pd
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#create one for measurement
measurement = Base.classes.measurement 

#create one for station 

station = Base.classes.station


#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################  HOMEPAGE

@app.route("/")
def homepage():
    """List all available api routes."""
    return (
       f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
        f"Note: add start and end dates in Y-M-D format."
        
    )

#################################################  PRECIPITATION 

@app.route("/api/v1.0/precipitation")
def precipitation():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Using this date, retrieve the previous 12 months of precipitation data by querying the 12 previous months of data. **Note:** Do not pass in the date as a variable to your query.
   
    #create the query using `date` as the key and `prcp` as the value 
    date17 = session.query(measurement.date).order_by(measurement.date.desc()).first()
    
    #find the last 12 months of data
    date16 = dt.date(2017, 8, 23) - dt.timedelta(days=365)
    
    #take 
    results = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date > date16).\
        order_by(measurement.date).all()
    
    session.close()
    
    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value 
    date_prcp_query = []
    for result in results:
        query = {}
        query['date']= result[0]
        query['prcp'] = result[1]
        date_prcp_query.append(query)
    print(date_prcp_query)

    # Return the JSON representation of your dictionary

    return jsonify(date_prcp_query)

#################################################  STATIONS

@app.route("/api/v1.0/stations")
def stations():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #query the stations
    query_station = session.query(station.name, station.station).all()
  
    session.close()
    # Return a JSON list of stations from the dataset.
  
    stat_query = []
    for st in query_station:
        row = {}
        row['name'] = st[0]
        row['station'] = st[1]
        stat_query.append(row)
        
   #return jsonify

    return jsonify(stat_query)


#################################################  TOBS/TEMP

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query the dates and temperature observations of the most active station for the previous year of data.
    temp_obs = session.query(measurement.tobs, measurement.date).\
        filter(measurement.date  < '2017-08-23').\
        filter(measurement.date > '2016-08-23').\
        filter(measurement.station == 'USC00519281').\
        order_by(measurement.tobs).\
        all()
    session.close()
    #find the first one of active
    print(temp_obs)
    
    temp_query = []
    for temp in temp_obs:
        row = {}
        row['tobs'] = temp[0]
        row['date'] = temp[1]
        temp_query.append(row)
    

    
    #Return a JSON list of temperature observations (TOBS) for the previous year.
    return jsonify(temp_query)

################################################# START DATE

#When given the start only, calculate `TMIN`, `TAVG`, and `TMAX` for all dates greater than or equal to the start date.
#use the <> to have people add in the start date

@app.route("/api/v1.0/<start>")
def start_date(start):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

   #create a query for all the values for start
    
    start_temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                 filter(measurement.date  <= start ).all()     
    session.close()
    
    # #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
    start_tobs = []
    for min, max, avg in start_temp:
        starting = {}
        starting["min"] = min
        starting["max"] = max
        starting["average"] = avg
        start_tobs.append(starting)

    return jsonify(start_tobs)


################################################# START-STOP DATE

#When given the start and the end date, calculate the `TMIN`, `TAVG`, and `TMAX` for dates from the start date through the end date (inclusive).


@app.route("/api/v1.0/<start>/<stop>")
def start_stop_date(start, stop):
    
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #Return a JSON list of the minimum temperature, the average temperature, and the maximum temperature for a given start or start-end range.
    
    ss_temp = session.query(func.min(measurement.tobs), func.max(measurement.tobs), func.avg(measurement.tobs)).\
                 filter(measurement.date >= start).filter(measurement.date <= stop).all()
    session.close()
    
    #create a list
    ss_tobs = []
    for min, max, avg in ss_temp:
        ss = {}
        ss["min"] = min
        ss["max"] = max
        ss["average"] = avg
        ss_tobs.append(ss)

    return jsonify(ss_tobs)


################################################# End


if __name__ == '__main__':
    app.run(debug=True)


