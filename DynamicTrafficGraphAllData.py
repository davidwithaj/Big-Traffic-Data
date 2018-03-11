import dash 
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go  # keep the max element of a list to n, if a new element is appended, pops out the 0th element
import pandas as pd
import datetime

def update_database(rows,skip): #how many rows should be extracted from the file, and how many rows should be skipped
    db = pd.read_csv('From100G.csv',nrows=rows,skiprows=range(1, skip),usecols=['tpep_picku']) #inporting n about of rows after skipping m
    cum_trips = db.groupby('tpep_picku')['tpep_picku'].count().reset_index(name='count') #reset index turns it dataframe, cumalative 
    x = cum_trips['tpep_picku']
    y = cum_trips['count']
    d = list(map(lambda z: datetime.datetime.strptime(z,"%Y-%m-%d %H:%M:%S"), x))
    return cum_trips, d, list(y)

rows = 100000
skip = 1
cum_trips, x, y = update_database(rows,skip)


app = dash.Dash('traffic_data')
app.layout = html.Div(children = [
	html.H1("The Heartbeat of Taxi Pickups"),
	html.H2("Dynamically updating the line graph to portray a heartbeat"),
	dcc.Graph(id = "graph",figure = {'data':[{ 'x':d, 'y':y, 'type':"line",'name':'Taxis'}], 'layout':{'title':'Taxi Data'}}	
		)
	])

if __name__ == "__main__":
	app.run_server(debug=True)

