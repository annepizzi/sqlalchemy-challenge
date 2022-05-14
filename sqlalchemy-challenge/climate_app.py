import numpy as np

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

   
    #create the query using `date` as the key and `prcp` as the value 
    results = (session.query(measurement.date, measurement.prcp)
                      .order_by(measurement.date))

    session.close()
    
    #Convert the query results to a dictionary using `date` as the key and `prcp` as the value 
    date_prcp_query = []
    for result in results:
        query = {}
        query["date"]= result.date
        query["prcp"] = result.prcp
        date_prcp_query.append(query)
    

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
        row["name"] = query_station[0]
        row["station"] = query_station[1]
        stat_query.append(row)
        
   #return jsonify

    return jsonify(stat_query)


#################################################  TOBS/TEMP

@app.route("/api/v1.0/tobs")
def tobs():
    
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #Query the dates and temperature observations of the most active station for the previous year of data.
    temp_obs = session.query(measurement.tobs).\
        filter(measurement.date  < '2017-08-23').\
        filter(measurement.date > '2016-08-23').\
        filter(measurement.station == 'USC00519281').\
        order_by(measurement.tobs).\
        all()
    session.close()
    #find the first one of active
    
    temp_query = []
    for temp in temp_obs:
        row = {}
        row["date"] = temp_obs[0]
        row["tobs"] = temp_obs[1]
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
                 filter(measurement.station  <= start ).all()     
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
def start_stop_date(StartStop):
    
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


