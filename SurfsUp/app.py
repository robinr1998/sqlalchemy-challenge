# Import the dependencies.
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from pathlib import Path
from sqlalchemy import create_engine, text

from flask import Flask, jsonify

#################################################
# Database Setup
#################################################

# Create a reference to the file. 
database_path = "Resources/hawaii.sqlite"

# Create an engine that can talk to the database
engine = create_engine(f"sqlite:///{database_path}")
#connection = engine.connect()

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################
# List all available routes
@app.route("/")
def homepage():
    """List all available api routes."""
    return (
        f"Available Routes:</br>"
        f"/api/v1.0/precipitation</br>"  
        f"/api/v1.0/stations</br>"
        f"/api/v1.0/tobs</br>"
        f"/api/v1.0/start/<start></br>"
        f"/api/v1.0/start/end/<start>/<end></br>"
        )

# app route for precipitation for past 12 months
@app.route("/api/v1.0/precipitation")
def precipitation():
    # create session link
    session = Session(engine)
    # query last 12 months of precipitation data (from climate.ipynb)
    # query_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    query_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= query_date).all()
    session.close()

# Create a dictionary of the precipitation data 
    prcp_data = []
    for date, prcp in results:
        prcp_dc = {}
        prcp_dc["DATE"] = date
        prcp_dc["Precipitation"] = prcp
        prcp_data.append(prcp_dc)

# Return the JSON representation of the dictionary
    return jsonify(prcp_data)


 #app routing for station list
@app.route("/api/v1.0/stations")
def stations():
    #create session link
    session = Session(engine)
    #query the names of all stations in the list
    results = session.query(Measurement.station).distinct().all()
    session.close()

    #create a dictionary of the active stations and their counts
    station_data = []
    for station in results:
        station_dc = {}
        station_dc["Station Name"] = station[0]
        station_data.append(station_dc)

    return jsonify(station_data)

#app routing for t_observed for the past 12 months
@app.route("/api/v1.0/tobs")
def tobs():
    #create session link
    session = Session(engine)
    #query the last 12 months of temperature data from the most active observation station 
    tobs_date = dt.date(2017,8,23) - dt.timedelta(days=365)
    tobs_date = '2016-08-23'
    results = session.query(Measurement.date, Measurement.tobs).\
        filter((Measurement.station == 'USC00519281', Measurement.date >= tobs_date)).all()
    session.close()

    #create a dictionary of tobs data for the most active station for the prior year
    tobs_data = []
    for date, tobs in results:
        tobs_dc = {}
        tobs_dc["Date"] = date
        tobs_dc["Oberved Temperature"] = tobs
        tobs_data.append(tobs_dc)

    return jsonify(tobs_data)

#app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/start/<start_date>")
def temp_start(start_date):

    session = Session(engine)
    
    results = session.query(func.min(Measurement.tobs).label('min_temperature'),
                        func.max(Measurement.tobs).label('max_temperature'),
                        func.avg(Measurement.tobs).label('avg_temperature')).\
                        filter((Measurement.date >= start_date)).all()
    session.close()

# Add temps to dictionary
    temp_data = []
    for tobs in results:
        temp_dc = {}
        temp_dc["Minimum Temp"] = results[0][0]
        temp_dc["Maximum Temp"] = results[0][1]
        temp_dc["Average Temp"] = results[0][2]
        temp_data.append(temp_dc)

    return jsonify(temp_data)

#app routing for min, max, avg temp for a given start date
@app.route("/api/v1.0/start/end/<start_date>/<end_date>")
def temps_start_end(start_date=None, end_date=None):
    session = Session(engine)

    results = session.query(func.min(Measurement.tobs).label('min_temperature'),
                        func.max(Measurement.tobs).label('max_temperature'),
                        func.avg(Measurement.tobs).label('avg_temperature')).\
                        filter((Measurement.date.between(start_date, end_date))).all()
    session.close()

    temp_data = []
    for tobs in results:
        temp_dc = {}
        temp_dc["Minimum Temp"] = results[0][0]
        temp_dc["Maximum Temp"] = results[0][1]
        temp_dc["Average Temp"] = results[0][2]
        temp_data.append(temp_dc)

    return jsonify(temp_data)

if __name__ == "__main__":
    app.run(debug=True)
