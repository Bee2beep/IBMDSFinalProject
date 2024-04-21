# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                html.Br(),

                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                    html.Div([
                                        dcc.Dropdown(
                                            id='site-dropdown',
                                            options=[{'label': 'All Sites', 'value': 'ALL'}] +
                                                    [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
                                            value='ALL',
                                            placeholder='Select a Launch Site',
                                            searchable=True
                                        )
                                    ]),
                                    html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                    html.Div([
                                        dcc.RangeSlider(
                                            id='payload-slider',
                                            min=min_payload,
                                            max=max_payload,
                                            step=1000,
                                            marks={i: str(i) for i in range(int(min_payload), int(max_payload) + 1, 2000)},
                                            value=[min_payload, max_payload]
                                        )
                                    ]),
                                    html.Br(),                              
                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart', 'figure'),
    [Input('site-dropdown', 'value')]
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Filter for successful launches
        success_df = spacex_df[spacex_df['class'] == 1]

        # Group by 'Launch Site' and count the number of successful launches at each site
        site_success_counts = success_df.groupby('Launch Site').size()

        # Create a pie chart with launch sites and their success counts
        pie_fig = px.pie(
            values=site_success_counts.values,
            names=site_success_counts.index,
            title='Total Success Launches By Site'
        )
    else:
        data = spacex_df[spacex_df['Launch Site'] == selected_site]
        success_count = len(data[data['class'] == 1])
        fail_count = len(data[data['class'] == 0])
        pie_fig = px.pie(values=[success_count, fail_count], names=['Success', 'Failure'], title=f'Success vs Failure at {selected_site}')
    return pie_fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart', 'figure'),
    [Input('site-dropdown', 'value'), 
     Input('payload-slider', 'value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df[
            (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= payload_range[1])
        ]
    else:
        filtered_df = spacex_df[
            (spacex_df['Launch Site'] == selected_site) &
            (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
            (spacex_df['Payload Mass (kg)'] <= payload_range[1])
        ]

    scatter_fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs Launch Success for {selected_site if selected_site != "ALL" else "All Sites"}'
    )
    return scatter_fig

# Run the app
if __name__ == '__main__':
    app.run_server()
