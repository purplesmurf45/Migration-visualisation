import pathlib

import dash
from dash import dcc
from dash import html
import pandas as pd
import numpy as np
from dash.dependencies import Input, Output, State
import cufflinks as cf
import plotly.graph_objects as go
import networkx as nx
from sklearn import preprocessing

# Initialize app

app = dash.Dash(
    __name__,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"}
    ],
)
app.title = "UNHCR Migration Data"
server = app.server

# Load data

APP_PATH = str(pathlib.Path(__file__).parent.resolve())

df_od = pd.read_csv('https://raw.githubusercontent.com/purplesmurf45/Migration-visualisation/main/data/dest.csv')


df_refugees = pd.read_csv(
    "https://raw.githubusercontent.com/purplesmurf45/Migration-visualisation/main/data/country_codes.csv"
)

df_refugees_out = pd.read_csv(
    "https://raw.githubusercontent.com/purplesmurf45/Migration-visualisation/main/data/outflow_country_codes.csv"
)



YEARS = list(range(2000, 2017, 1))


DEFAULT_OPACITY = 0.8


# App layout

app.layout = html.Div(
    id="root",
    children=[
        html.Div(
            id="header",
            children=[
                html.A(
                    html.Button("Source Code", className="link-button"),
                    href="https://github.com/purplesmurf45/Migration-visualisation",
                ),
                html.H4(children="UNHCR Migration Data"),
                html.P(
                    id="description",
                    children="† World migration data is given over the years 2000 to 2016. \
                        ",
                ),
            ],
        ),
        html.Div(
            id="app-container",
            children=[
                html.Div(
                    id="left-column",
                    children=[
                        html.Div(
                            id="slider-container",
                            children=[
                                html.P(
                                    id="slider-text",
                                    children="Drag the slider to change the year:",
                                ),
                                dcc.Slider(
                                    id="years-slider",
                                    min=min(YEARS),
                                    max=max(YEARS),
                                    value=min(YEARS),
                                    step=1,
                                    tooltip={"placement": "top"},
                                    marks={
                                        str(year): {
                                            # "label":,
                                            "style": {"color": "#001E6C"},
                                        }
                                        for year in YEARS
                                    },
                                ),
                            ],
                        ),
                        html.Div(
                            id="flow-container",
                            children=[
                                html.P(
                                    "Select inflow/outflow",
                                    id="flow-button-title",
                                ),
                                dcc.RadioItems(
                                    id="chart-type",
                                            options=[
                                                {"label": "Inflow", "value": "in"},
                                                {
                                                    "label": "Outflow",
                                                    "value": "out",
                                                },
                                            ],
                                            value="in",
                                            labelStyle = {'display': 'block', 'cursor': 'pointer', 'margin-left':'20px'},
                                            inline=True
                                    ),

                            ]
                        ),
                        html.Div(
                            id="heatmap-container",
                            children=[
                                html.P(
                                    "Choropleth of migration  \
                            in year {0}".format(
                                        min(YEARS)
                                    ),
                                    id="heatmap-title",
                                ),
                                dcc.Graph(
                                    id="country-choropleth",
                                    figure=dict(
                                        layout=dict(
                                            autosize=True,
                                        ),
                                    ),
                                ),
                            ],
                        ),
                    ],
                ),
                html.Div(
                    id="graph-container",
                    children=[
                        html.P(id="chart-selector", children="Select chart:"),
                        
                        dcc.Dropdown(
                            options=[
                                {
                                    "label": "Bar Chart",
                                    "value": "Bar Chart",
                                },
                                {
                                    "label": "Sankey Diagram",
                                    "value": "Sankey Diagram",
                                },
                                {
                                    "label": "Node-link Diagram",
                                    "value": "Node-link Diagram",
                                },
                            ],
                            value="Bar Chart",
                            id="chart-dropdown",
                            # children="This is a viz32re"
                        ),
                        html.P(
                            id="viz-desc",
                            children="NOTE: If choosing Sankey Diagram, choosing too many countries at a time is not adviced here. This is due to exponential increase in visualization complexity."
                        ),
                        dcc.Graph(
                            id="selected-data",
                            figure=dict(
                                data=[dict(x=0, y=0)],
                                layout=dict(
                                    paper_bgcolor="#F4F4F8",
                                    plot_bgcolor="#F4F4F8",
                                    autofill=True,
                                    margin=dict(t=75, r=50, b=100, l=50),
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        ),
    ],
)

# @app.callback(
#     Output("viz-desc", "desc"),
#     [Input("chart-dropdown", "value")],
#     [State("viz-desc", "desc")],
# )

# def update_desc (option, desc):
#     if option == "Bar Chart":
#         desc = "This is a bar chart"
#     elif option == "Sankey Diagram":
#         desc = "This is a Sankey diagram"
#     else:
#         desc = "This is a Node-link diagram"
#     return desc

@app.callback(
    Output("country-choropleth", "figure"),
    [Input("years-slider", "value"), Input("chart-type", "value")],
    [State("country-choropleth", "figure")],
)

def display_map(year, type ,figure):
    if (type == "in"):
        df_temp = df_refugees[df_refugees['Year'] == year]
        val = df_temp['Destination']
    else:
        df_temp = df_refugees_out[df_refugees_out['Year'] == year]
        val = df_temp['Origin']
    fig = go.Figure(data=go.Choropleth(
    locations = df_temp['CODE'],
    z = np.log10(df_temp['Refugees']),
    zmin = 0,
    zmax = 6.6,
    text = val,
    colorscale = 'tealrose',
    autocolorscale=False,
    reversescale=True,
    marker_line_color="#001E6C",        #mint
    marker_line_width=0.2,
    colorbar_title = 'Number of<br>Refugees',
))

    fig.update_layout(
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type='equirectangular',
            
        ),
        margin={"r":0,"t":0,"l":0,"b":0},
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        annotations = [
        dict(
            showarrow=False,
            align="right",
            text="Number of <br>Refugees",
            font=dict(color="#001E6C"),
            bgcolor="#1f2630",
            x=1.4,
            y=1.4,
        )
    ]
    )
    fig.update_geos(bgcolor="rgba(0,0,0,0)")
    fig_layout = fig["layout"]
    fig_layout["font"]["color"] = "#001E6C"
    fig_layout["title"] = ""
    fig_layout["title"]["font"]["color"] = "#001E6C"
    fig_layout["xaxis"]["tickfont"]["color"] = "#001E6C"
    fig_layout["yaxis"]["tickfont"]["color"] = "#001E6C"
    fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
    fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
    return fig



le = preprocessing.LabelEncoder()
a = np.unique(np.concatenate((df_od['Origin'],df_od['Destination']),0))
le.fit(a)
@app.callback(Output("heatmap-title", "children"), [Input("years-slider", "value")])
def update_map_title(year):
    return "Choropleth of immigrants per country \
				in year {0}".format(
        year
    )

def get_trace (graph, nodes, edges, node_length):
  nlayout = nx.kamada_kawai_layout(graph)
  x_node = [nlayout[k][0] for k in nodes]
  y_node = [nlayout[k][1] for k in nodes]
  node_hover = []
  for node, adjacencies in enumerate(graph.adjacency()):
    node_hover.append(str(adjacencies[0])+"<br>"+str(len(adjacencies[1])))

  node_trace = go.Scatter(  x = x_node,
                            y = y_node,
                            mode = 'markers',
                            hoverinfo = 'text',
                            hovertext = node_hover,
                            ids = nodes,
                            marker = dict(  showscale = True,
                                            colorscale = 'tealrose',
                                            reversescale = True,
                                            size = 10,
                                            colorbar = dict(
                                                thickness = 10,
                                                title = 'Degree of Node',
                                                xanchor = 'left',
                                                titleside = 'right'
                                            ),
                                            line_width = 2))
  
  x_edge = []
  y_edge = []
  for edge in edges:
      x_edge += [nlayout[edge[0]][0], nlayout[edge[1]][0], None]
      y_edge += [nlayout[edge[0]][1], nlayout[edge[1]][1], None]

  edge_trace = go.Scatter(  x = x_edge,
                            y = y_edge,
                            line = dict(width = 0.5, color = '#888'),
                            hoverinfo = 'none',
                            mode = 'lines')
  
  return node_trace, edge_trace

def get_node_link_diagram(graph, nodes, edges, node_length):
  node_trace, edge_trace = get_trace (graph, nodes, edges, node_length)
  node_adjacencies = []
  node_text = []
  for node, adjacencies in enumerate(graph.adjacency()):
      node_adjacencies.append(len(adjacencies[1]))
      node_text.append(node)
  node_trace.text = node_adjacencies   
  node_trace.marker.color = node_adjacencies
  node_trace.marker.size = 5
  fig = go.Figure(  data = [edge_trace, node_trace],
                    layout = go.Layout(
                        showlegend = False,
                        hovermode = 'closest',
                        xaxis = dict(showgrid = False, zeroline = False, showticklabels = False),
                        yaxis = dict(showgrid = False, zeroline = False, showticklabels = False))
                        )
  return fig

@app.callback(
    Output("selected-data", "figure"),
    [
        Input("country-choropleth", "selectedData"),
        Input("chart-dropdown", "value"),
        Input("years-slider", "value"),
        Input("chart-type", "value")
    ],
)
def display_selected_data(selectedData, chart_dropdown, year, type):
    if selectedData is None:
        return dict(
            data=[dict(x=0, y=0)],
            layout=dict(
                title="Click-drag on the map to select countries",
                # paper_bgcolor="#1f2630",
                # plot_bgcolor="#1f2630",
                font=dict(color="#001E6C"),
                margin=dict(t=75, r=50, b=100, l=75),
            ),
        )
    pts = selectedData["points"]
    # print(pts)
    locations = [pt["text"] for pt in pts]
    # print(locations)
    if type == "in":
        dff = df_refugees
        dff = dff[dff["Destination"].isin(locations)]
        val = "Destination"
    else:
        dff = df_refugees_out
        dff = dff[dff["Origin"].isin(locations)]
        val = "Origin"

    if chart_dropdown != "death_rate_all_time":
        title = "Refugees in year <b>{0}</b>".format(year)
        AGGREGATE_BY = "Refugees"
        KIND = "bar"
        if "Bar Chart" == chart_dropdown:
            dff = dff[dff.Year == year]
            title = "Refugees in year <b>{0}</b>".format(year)
            AGGREGATE_BY = "Refugees"
            KIND = "bar"
            dff[AGGREGATE_BY] = pd.to_numeric(dff[AGGREGATE_BY], errors="coerce")
            refugee_agg = dff.groupby(val)[AGGREGATE_BY].sum()
            refugee_agg = refugee_agg.sort_values()

            # Only look at non-zero rows:
            refugee_agg = refugee_agg[refugee_agg > 0]
            fig = refugee_agg.iplot(
                kind=KIND, y=AGGREGATE_BY, title=title, asFigure=True
            )
            fig_data = fig["data"]
            fig_layout = fig["layout"]

            fig_data[0]["text"] = refugee_agg.values.tolist()
            fig_data[0]["marker"]["color"] = "#001E6C"
            fig_data[0]["marker"]["opacity"] = 1
            fig_data[0]["marker"]["line"]["width"] = 0
            fig_data[0]["textposition"] = "outside"
            
        elif "Sankey Diagram" == chart_dropdown:
            dff = df_od
            dff = dff[dff[val].isin(locations)]
            dff = dff[dff.Year == year]
            title = "Refugees in the year, <b>{0}</b>".format(year)
            fig = go.Figure(data=[go.Sankey(
            node = dict(
            pad = 15,
            thickness = 20,
            line = dict(color = "white", width = 0.5),
            label = le.classes_,
            color = "blue"
            ),
            link = dict(
            source = le.transform(dff['Origin']), # indices correspond to labels, eg A1, A2, A1, B1, ...
            target = le.transform(dff['Destination']),
            value = dff['Refugees'],
        ))])
            fig["layout"]["title"] = "Migration flow between countries in the year <b>{0}</b>".format(year)
            fig["layout"]["plot_bgcolor"] = "#1f2630"
        elif "Node-link Diagram" == chart_dropdown:
            dff = df_od
            dff = dff[dff[val].isin(locations)]
            dff = dff[dff.Year == year]
            nodes = []
            edges = []
            for i in range(len(dff)):
                nodes.append(dff.iloc[i]["Destination"]) 
                nodes.append(dff.iloc[i]["Origin"]) 
                edges.append((dff.iloc[i]["Destination"],dff.iloc[i]["Origin"]))
            nodes = list(set(nodes))
            #initializing graph and adding nodes and edges to it
            graph = nx.Graph()
            for node in nodes:
                graph.add_node(node)
            for edge in edges:
                graph.add_edge(*edge)
            node_length = len(nodes)
            fig = get_node_link_diagram(graph, nodes, edges, node_length)
            fig["layout"]["title"] = "Connectivity between countries in the year <b>{0}</b>".format(year)


        fig_layout = fig["layout"]
        # fig_layout["paper_bgcolor"] = "#1f2630"
        # fig_layout["plot_bgcolor"] = "#1f2630"
        fig_layout["font"]["color"] = "#001E6C"
        fig_layout["title"]["font"]["color"] = "#001E6C"
        fig_layout["xaxis"]["tickfont"]["color"] = "#001E6C"
        fig_layout["yaxis"]["tickfont"]["color"] = "#001E6C"
        fig_layout["xaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["yaxis"]["gridcolor"] = "#5b5b5b"
        fig_layout["margin"]["t"] = 75
        fig_layout["margin"]["r"] = 50
        fig_layout["margin"]["b"] = 100
        fig_layout["margin"]["l"] = 50

        return fig


if __name__ == "__main__":
    app.run_server(debug=True)
