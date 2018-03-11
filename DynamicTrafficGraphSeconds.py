import dash 
from dash.dependencies import Output, Event, Input
import dash_core_components as dcc
import dash_html_components as html
import plotly
import plotly.graph_objs as go 
from collections import deque # keep the max element of a list to n, if a new element is appended, pops out the 0th element
import pandas as pd
import datetime

def update_database(rows,skip): #how many rows should be extracted from the file, and how many rows should be skipped
    db = pd.read_csv('From100G.csv',nrows=rows,skiprows=range(1, skip),usecols=['tpep_picku']) #inporting n about of rows after skipping m
    cum_trips = db.groupby('tpep_picku')['tpep_picku'].count().reset_index(name='count') #reset index turns it dataframe, cumalative 
    x = cum_trips['tpep_picku']
    y = cum_trips['count']
    d = list(map(lambda z: datetime.datetime.strptime(z,"%Y-%m-%d %H:%M:%S"), x))
    return cum_trips, d, y

indexNumber = 0
rows = 100000
skip = 1
cum_trips, d, y = update_database(rows,skip)
X = deque(maxlen=100000) 	#deque(maxlen=len(cum_trips))
Y = deque(maxlen=100000)	#deque(maxlen=len(cum_trips))


app = dash.Dash('traffic_data')
app.layout = html.Div(children = [
	html.H1("The Heartbeat of Taxi Pickups"),
	html.H2("Dynamically updating the line graph to portray a heartbeat"),
	dcc.Graph(id = 'live-graph', animate = True),
	dcc.Interval(id= 'update-graph', interval = 1000) 
	])

@app.callback(Output("live-graph","figure"), events = [Event("update-graph",'interval')]) #wrapper
def graph_update():
	global indexNumber
	global d
	global y
	global skip
	global rows
	global cum_trips
	q = d[indexNumber] #list of times 
	c = y[indexNumber] #cumalative rides at a time
	X.append(q)
	Y.append(c)
	data = go.Scatter(
		x = list(X),
		y = list(Y),
		name = "Scatter",
		mode = "lines"
		)
	if indexNumber == len(cum_trips)-1: #redefine the variables with a new dataset
		indexNumber = 0
		skip = rows
		rows += 10000
		cum_trips, d, y = update_database(rows,skip)
	else:
		indexNumber += 1
	return {"data":[data],"layout": go.Layout(xaxis = dict(range=[min(X),max(X)]), yaxis = dict(range=[-1,20]))} #	yaxis = dict(range=[min(Y),max(Y)]


if __name__ == "__main__":
	app.run_server(debug=True)

