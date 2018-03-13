import dash 
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go 
import plotly.plotly as py
from plotly.graph_objs import *
from collections import deque # keep the max element of a list to n, if a new element is appended, pops out the 0th element
import pandas as pd
import datetime

mapbox_access_token = 'pk.eyJ1IjoiamF2aWRhbWlyIiwiYSI6ImNqZW9yYmRncjYwcnUyd28xNGg3bnUzOGwifQ.f9YGf4DrA_8iC6EDdG2TSg'

def update_database(rows,skip): #how many rows should be extracted from the file, and how many rows should be skipped
    db = pd.read_csv('From100G.csv',nrows=rows,skiprows=range(1, skip),usecols=['tpep_picku']) #inporting n about of rows after skipping m
    cum_trips = db.groupby('tpep_picku')['tpep_picku'].count().reset_index(name='count') #reset index turns it dataframe, cumalative 
    x = cum_trips['tpep_picku']
    y = cum_trips['count']
    d = list(map(lambda z: datetime.datetime.strptime(z,"%Y-%m-%d %H:%M:%S"), x))
    min_date = min(d)
    max_date = max(d)
    return cum_trips, x, y, min_date, max_date

def update_lonlat(date_str): #input a q value 
    db = pd.read_csv("From100G.csv",usecols=['tpep_picku','pickup_lon','pickup_lat'])
    lon_lat_db = db[db.tpep_picku == date_str]
    lon = lon_lat_db.pickup_lon
    lat = lon_lat_db.pickup_lat
    return lon, lat

indexNumber = 0
rows = 100000
skip = 1
cum_trips, x, y, min_date, max_date = update_database(rows,skip)
X = deque(maxlen=1000) 	#deque(maxlen=len(cum_trips))
Y = deque(maxlen=1000)	#deque(maxlen=len(cum_trips))


app = dash.Dash('traffic_data')
app.layout = html.Div(children = [
	html.H1("Taxi Pickups"),
	html.H2("Dynamically updating the line graph to portray a heartbeat"),
	dcc.Graph(id = 'map-graph', animate = True),
	dcc.Graph(id = 'live-graph', animate = True),
	dcc.Interval(id= 'update-graph', interval = 2000) 
	])

@app.callback(Output("live-graph","figure"), events = [Event("update-graph",'interval')]) #wrapper
def map_update():
	global indexNumber, x, y, skip, rows, cum_trips, min_date, max_date, date_str

	#updating line graph
	date_str = x[indexNumber]
	date_date = datetime.datetime.strptime(date_str,"%Y-%m-%d %H:%M:%S")  #change from string to datetime
	ride_count = y[indexNumber] #cumalative rides at a time
	X.append(date_date)
	Y.append(ride_count)
	live_data = go.Scatter(x = list(X), y = list(Y), name = "Scatter", mode = "lines")
	live_fig = {"data":[live_data],"layout": go.Layout( xaxis = dict(range= [datetime.datetime(2015, 12, 17, 10, 47, 1),datetime.datetime(2015, 12, 17, 10, 55, 0)]) ,yaxis = dict(range=[-1,20]))} #	yaxis = dict(range=[min(Y),max(Y)]
	if indexNumber == len(cum_trips)-1: #redefine the variables with a new dataset
		indexNumber = 0
		skip = rows
		rows += 100000
		cum_trips, x, y, min_date, max_date = update_database(rows,skip)
	else:
		indexNumber += 1
	return live_fig


@app.callback(Output("map-graph","figure"), events = [Event("update-graph","interval")])
def graph_update():
	#updating map
	lon,lat = update_lonlat(date_str)
	map_data = Data([Scattermapbox(lat=lat,lon=lon,mode='markers',marker=Marker(size=14),text=['Montreal'],)])
	map_layout = Layout(autosize=True,hovermode='closest',height=900,margin={'l':200,'r':200,'t':50,'b':1},mapbox=dict(accesstoken=mapbox_access_token,bearing=0,center=dict(lat=40.75,lon=-73.9), pitch=0,zoom=10),)
	map_fig = dict(data=map_data, layout=map_layout)
	return map_fig

	
if __name__ == "__main__":
	app.run_server(debug=True)

