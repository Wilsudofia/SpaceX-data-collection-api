import dash
from dash import dcc, html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px

# Load the SpaceX launch data
spacex_df = pd.read_csv("https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv")

# Get unique launch site names
launch_sites = spacex_df['Launch Site'].unique().tolist()

# Create the dropdown options including 'All Sites'
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
                   [{'label': site, 'value': site} for site in launch_sites]

# Initialize Dash app
app = dash.Dash(__name__)

# Define min and max payload values
min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()

# Define the layout of your app
app.layout = html.Div([
    # Title of the dashboard
    html.H1("SpaceX Launch Dashboard", style={'textAlign': 'center', 'fontSize': 36}),
    
    # Add the dropdown for selecting the launch site
    dcc.Dropdown(
        id='site-dropdown',
        options=dropdown_options,
        value='ALL',  # Default value
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    
    # The pie chart (success-pie-chart) where the result will be shown
    dcc.Graph(id='success-pie-chart'),
    
    # Add the range slider for selecting payload mass (moved below the pie chart)
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=1000,
        marks={0: '0', 2500: '2500', 5000: '5000', 7500: '7500', max_payload: f'{max_payload}'},  # Dynamic max value
        value=[min_payload, max_payload]  # Default value set to the full range
    ),
    
    # The scatter plot (success-payload-scatter-chart) where the result will be shown
    dcc.Graph(id='success-payload-scatter-chart')
])

# Callback function for pie chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        fig = px.pie(
            spacex_df,
            names='Launch Site',
            values='class',
            title='Total Success Launches for All Sites'
        )
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        site_counts['class'] = site_counts['class'].map({1: 'Success', 0: 'Failure'})
        
        fig = px.pie(
            site_counts,
            names='class',
            values='count',
            title=f'Total Launch Outcome for Site: {entered_site}'
        )
    return fig

# Callback function for scatter plot (success vs payload)
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def get_scatter_plot(entered_site, payload_range):
    # Filter dataframe based on selected payload range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) & 
                            (spacex_df['Payload Mass (kg)'] <= payload_range[1])]

    if entered_site != 'ALL':
        filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
    
    # Plot the scatter plot with Payload vs Launch Outcome (class)
    fig = px.scatter(
        filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title=f'Payload vs Launch Outcome for {entered_site if entered_site != "ALL" else "All Sites"}',
        labels={'class': 'Launch Outcome (0 = Failure, 1 = Success)'}
    )
    return fig

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
