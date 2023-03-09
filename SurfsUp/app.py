import numpy as np
import datetime as dt

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


engine = create_engine("sqlite:///../Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(autoload_with=engine)

# Save reference to the table
measurement = Base.classes.measurement
station = Base.classes.station


app = Flask(__name__)

#home page
@app.route("/")
def home():
    print("Server received request for 'Home' page...")
    return (f"Available routes: <br/>"
            f"/api/v1.0/precipitation <br/>"
            f"/api/v1.0/stations <br/>"
            f"/api/v1.0/tobs <br/>"
            f"/api/v1.0/start_date <br/>"
            f"/api/v1.0/start_date/end_date <br/>"
            f"<br/>replace start_date/end_date in the form of yyyy-mm-dd"
    )

#precipitation page
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    #date variable 
    date = dt.datetime(2017,8,23)-dt.timedelta(days=365)

    #query all data
    results = session.query(measurement.date,measurement.prcp).\
        filter(func.strftime(measurement.date)>=date).group_by(measurement.date).all()

    session.close()

    #dictionary for data and append to a list 
    last_year = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["precopitation"] = prcp
        last_year.append(prcp_dict)

    return jsonify(last_year)


#stations page
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)

    """Return a list of all station names"""
    station_names = session.query(station.name).all()

    session.close()

    # Convert list of tuples into normal list
    all_names = list(np.ravel(station_names))

    return jsonify(all_names)


#tobs page
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    #date variable
    date2 = dt.datetime(2017,8,18)-dt.timedelta(days=365)

    #query all data
    year_temperature_active = session.query(measurement.date,measurement.tobs).\
        filter(measurement.station == "USC00519281").filter(measurement.date > date2).all()

    session.close()

    #dictionary for data and append to a list 
    last_year_active = []
    for date, temp in year_temperature_active:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["temperature"] = temp
        last_year_active.append(temp_dict)

    return jsonify(last_year_active)


#start date search 
@app.route("/api/v1.0/<start_date_str>")
def start(start_date_str):

    session = Session(engine)

    #start date variable
    start_date = dt.datetime.strptime(start_date_str,"%Y-%m-%d")

    #query for min,max,avg
    lowest = session.query(func.min(measurement.tobs)).\
        filter(measurement.station == "USC00519281").\
            filter(measurement.date > start_date).first()

    highest = session.query(func.max(measurement.tobs)).\
        filter(measurement.station == "USC00519281").\
            filter(measurement.date > start_date).first()

    average = session.query(func.avg(measurement.tobs)).\
        filter(measurement.station == "USC00519281").\
            filter(measurement.date > start_date).all()
    
    session.close()
    
    return (f"Station: USC00519281 <br/>\n\
            Lowest temperature:{lowest}<br/>\n\
            Highest temperature:{highest}<br/>\n\
            Average temperature:{average}")

    


#start date and end date search 
@app.route("/api/v1.0/<start_date_str>/<end_date_str>")
def end(start_date_str,end_date_str):

    session = Session(engine)

    #start and end date variable
    start_date = dt.datetime.strptime(start_date_str,"%Y-%m-%d")
    end_date = dt.datetime.strptime(end_date_str,"%Y-%m-%d")

    #query for min,max,avg
    lowest = session.query(func.min(measurement.tobs)).\
        filter(measurement.station == "USC00519281").\
            filter(measurement.date > start_date).\
                filter(measurement.date < end_date).first()

    highest = session.query(func.max(measurement.tobs)).\
        filter(measurement.station == "USC00519281").\
            filter(measurement.date > start_date).\
                filter(measurement.date < end_date).first()

    average = session.query(func.avg(measurement.tobs)).\
        filter(measurement.station == "USC00519281").\
            filter(measurement.date > start_date).\
                filter(measurement.date < end_date).all()
    
    session.close()
    
    return (f"Station: USC00519281 <br/>\n\
            Lowest temperature:{lowest}<br/>\n\
            Highest temperature:{highest}<br/>\n\
            Average temperature:{average}")
    


if __name__ == "__main__":
    app.run(debug=True)
