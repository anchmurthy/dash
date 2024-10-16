import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Load the data
file_path = 'concerts.csv'  # Update this path to where you saved the CSV file
concerts_df = pd.read_csv(file_path)

# Convert the date column to datetime
concerts_df['Date'] = pd.to_datetime(concerts_df['Date'], errors='coerce')
concerts_df = concerts_df.dropna(subset=['Date'])
#Add city
def get_city(location):
    if 'NYC' in location or 'New York' in location:
        return 'New York'
    elif 'Madison' in location:
        return 'Wisconsin'
    elif 'SF' in location or 'Stanford' in location or 'Berkeley' in location or 'San' in location:
        return 'California'
    elif 'Grand Rapids' in location or 'Lansing' in location:
        return 'Michigan'
    else:
        return 'Illinois'

concerts_df['City'] = concerts_df['Location'].apply(get_city)
# Replace the custom delimiter '|' with HTML line breaks '<br>' in the 'Additional Info on Setlist' column
concerts_df['Additional Info on Setlist'] = concerts_df['Additional Info on Setlist'].fillna('').str.replace(';', ',<br>')
concerts_df['Additional Info on Setlist'] = concerts_df['Additional Info on Setlist'].fillna('').str.replace(':,<br>', ':<br>')
concerts_df = concerts_df.sort_values(by=['City', 'Location'])
# Initialize the Dash app
app = Dash(__name__)

# Define CSS styles for custom styling
custom_styles = {
    'background': '#1f1f2e',
    'text': '#f4f4f9',
    'accent': '#4e79a7',
    'font_family': 'Arial, sans-serif'
}

# Layout of the dashboard
app.layout = html.Div(
    style={'backgroundColor': custom_styles['background'], 'color': custom_styles['text'], 'fontFamily': custom_styles['font_family'], 'padding': '20px'},
    children=[
        html.H1("Concerts Seen", style={'textAlign': 'center', 'color': custom_styles['accent']}),
        dcc.Dropdown(
            id='concert-type-filter',
            options=[{'label': ctype, 'value': ctype} for ctype in concerts_df['Concert Type'].unique()],
            value=[],
            multi=True,
            placeholder="Filter by Concert Type",
            style={'backgroundColor': custom_styles['background'], 'color': 'black', 'width': '80%', 'margin': 'auto'}
        ),
        dcc.Graph(id='timeline-plot'),
        html.H2("Artists/Musicals seen:", style={'textAlign': 'center', 'marginTop': '40px'}),
        html.Ul(id='distinct-artists-list', style={'listStyleType': 'none', 'padding': '0', 'textAlign': 'center'})
    ]
)

# Callback to update the timeline plot
@app.callback(
    Output('timeline-plot', 'figure'),
    Input('concert-type-filter', 'value')
)
def update_timeline(selected_types):
    # Filter data based on selected concert types
    if selected_types:
        filtered_df = concerts_df[concerts_df['Concert Type'].isin(selected_types)]
    else:
        filtered_df = concerts_df
    filtered_df['Venue'] = filtered_df['City'] + ': ' + filtered_df['Location']
    # Create the plot
    fig = px.scatter(
        filtered_df,
        x='Date',
        y='Band/Artist',
        color='Venue',
        hover_data={'Location': True, 'Additional Info on Setlist': True},
        title='Timeline of Concerts Seen (hover over data points for info)',
        template='plotly_dark'
    )
    fig.update_traces(hovertemplate=
    "<b>Artist/Show</b>: %{y}<br>" +
    "<b>Date</b>: %{x|%m-%Y}<br>" +
    "<b>Location</b>: %{customdata[0]}<br>" +
    "<b>Setlist Info</b>: %{customdata[1]}<br>" 
    )
    fig.update_traces(marker=dict(size=12, opacity=0.7, line=dict(width=1, color='white')))
    # Add a range slider to allow zooming on specific months
    fig.update_xaxes(rangeslider_visible=True,title='Year (with range sliders)')
    # Remove the Y-axis (since we're not using it meaningfully)
    fig.update_yaxes(showticklabels=False,title='Artist/Musical')
    fig.update_layout(
        title=dict(x=0.5),
        plot_bgcolor=custom_styles['background'],
        paper_bgcolor=custom_styles['background'],
        font=dict(color=custom_styles['text'])
    )
    fig.update_layout(
    hoverlabel=dict(
        font_size=16,  # Increase hover text font size
        font_family="Arial",  # Change font family if needed
        bgcolor="lightgray"  # Optional: adjust background color of hover
        )
    )
    return fig

# Callback to update the distinct artists list
@app.callback(
    Output('distinct-artists-list', 'children'),
    Input('concert-type-filter', 'value')
)
def update_artist_list(selected_types):
    # Filter data based on selected concert types
    if selected_types:
        filtered_df = concerts_df[concerts_df['Concert Type'].isin(selected_types)]
    else:
        filtered_df = concerts_df

    # Get a list of distinct artists
    distinct_artists = filtered_df['Band/Artist'].unique().tolist()
    return [html.Li(artist, style={'padding': '5px', 'fontSize': '18px'}) for artist in distinct_artists]

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
