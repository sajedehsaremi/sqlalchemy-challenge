import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

# 1. import Flask - (required)
from flask import Flask

from flask import Flask, jsonify
#################################################
# Database Setup
#################################################

engine = create_engine("sqlite:///hawaii.sqlite")
# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)
Base.classes.keys()

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create a database session object
session = Session(engine)

#################################################
# Flask Setup
#################################################
# 2. Create an app, being sure to pass __name__ (required)
app = Flask(__name__)

# 3. Define what to do when a user hits the index route
# Home page ("/")
@app.route("/")
def welcome():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"Precipitation: /api/v1.0/precipitation<br/>"
        f"List of Stations: /api/v1.0/stations<br/>"
        f"Temperature for one year: /api/v1.0/tobs<br>/"
        f"Temperature stat from the start date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd<br>/"
        f"Temperature stat from the start to end date(yyyy-mm-dd): /api/v1.0/yyyy-mm-dd/yyyy-mm-dd"
    )

# return JSON results to a disctionary using date:'prcp' as the value-- Key:value
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create our session(link) from Python to the DB
    session = Session(engine)
    results = session.query(Measurement.date, Measurement.prcp).\
              order_by(Measurement.date).all()
# create a dictionary from the data and append a list
    prcp_date_list = []
    for date, prcp in results:
        prcp_date_dict = {}
        prcp_date_dict[date] = prcp
        prcp_date_list.append(prcp_date_dict)

    # close the session
    session.close()

    return jsonify(prcp_date_list)

# query all the stations
@app.route("/api/v1.0/stations")
def stations():
    # create our session(link) from Python to the db
    session = Session(engine)
    results = session.query(Station.station, Station.name).all()
    # query all the stations
    stations = {}    
    for s, name in results:
        stations[s] = name

    session.close()

    return jsonify(stations)
#############################################################################################

# query all the tobs 
@app.route("/api/v1.0/tobs")
def tobs():
    # create our session(link) from Python to the db
    session = Session(engine)

    # query the dates and temp observation of the most active station for the last_year
    last_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    last_year_date = (dt.datetime.strptime(last_date[0], '%Y-%m-%d'))\
                    - (dt.timedelta(days = 365))
    
    # Query for the dates and temperature 
    results = session.query(Measurement.date, Measurement.tobs).\
             filter(Measurement.date >= last_year_date).\
             order_by(Measurement.date).all()

    #Convert the results to dictionary and return to jsonify 
    tobs_datelist = []
    for date, tobs in results:
        tobs_date_dict = {}
        tobs_date_dict[date] = tobs
        tobs_datelist.append(tobs_date_dict)

    session.close()
        
    return jsonify(tobs_datelist)
#############################################################################################

# return JSON list of min, avg, and mx temp for given start or start-end range
@app.route("/api/v1.0/<start>")
def get_temp_start(start):
    # print(f"get_temp_start: {start}")
    # Create our session (link) from Python to the DB
    session = Session(engine)
    # calculate min,max, and avg for all dates >= start date
    results = session.query(Measurement.date,\
              func.min(Measurement.tobs),\
              func.avg(Measurement.tobs),\
              func.max(Measurement.tobs)).\
              filter(Measurement.date >= start).\
              group_by(Measurement.date).all()

# Convert list of tuples into normal list
    all_tobs =  []
    for temp_date, min, avg, max in results:
        tobs_dict = {}
        tobs_dict["Date"] = temp_date
        tobs_dict["Min"] = min
        tobs_dict["Avg"] = avg
        tobs_dict["Max"] = max
        all_tobs.append(tobs_dict)
    
    session.close()

    return jsonify(all_tobs)
#############################################################################################

# calcualte min, max, and avg for date between start and end date inclusive
@app.route("/api/v1.0/<begining_date>/<end_date>")
def get_temp_end(begining_date, end_date):
    print(f"----------------------------------get_temp_end: {begining_date, end_date}")
    session = Session(engine)

    results = session.query(
            func.min(Measurement.tobs),\
            func.avg(Measurement.tobs),\
            func.max(Measurement.tobs)).\
            filter(Measurement.date >= begining_date, Measurement.date <= end_date).all()
            
    print(f"----------------------------------------{results}")
    # Convert list of tuples into normal list
    results_list =  []
    for min, avg, max in results:
        results_list_dict =  {}
        results_list_dict["Min"] = min
        results_list_dict["Avg"] = avg
        results_list_dict["Max"] = max
        results_list.append(results_list_dict)

    session.close()

    return jsonify(results_list)
    


if __name__ == '__main__':
    app.run(debug=True)