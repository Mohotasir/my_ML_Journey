import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# Read CSV data
df = pd.read_csv('historical_automobile_sales.csv')

# Initialize the Dash app
app = dash.Dash(__name__)

# Define the layout of the dashboard
app.layout = html.Div([
    html.H1("Automobile Sales Dashboard", style={'textAlign': 'center'}),

    # Dropdown for report selection
    html.Div([
        html.Label("Select Report Type"),
        dcc.Dropdown(
            id='report-type',
            options=[
                {'label': 'Yearly Statistics', 'value': 'Yearly Statistics'},
                {'label': 'Recession Period Statistics', 'value': 'Recession Period Statistics'}
            ],
            value='Yearly Statistics'
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Dropdown for year selection
    html.Div([
        html.Label("Select Year"),
        dcc.Dropdown(
            id='year-dropdown',
            options=[{'label': str(year), 'value': year} for year in df['Year'].unique()],
            disabled=False
        )
    ], style={'width': '48%', 'display': 'inline-block'}),

    # Output container for the graphs
    html.Div(id='output-container'),
])

# Callback to enable/disable year dropdown based on report type
@app.callback(
    Output('year-dropdown', 'disabled'),
    Input('report-type', 'value')
)
def update_year_dropdown(report_type):
    # Disable year dropdown for "Recession Period Statistics"
    return report_type == 'Recession Period Statistics'

# Callback for generating graphs
@app.callback(
    Output('output-container', 'children'),
    [Input('report-type', 'value'), Input('year-dropdown', 'value')]
)
def update_graphs(selected_statistics, input_year):
    try:
        if selected_statistics == 'Recession Period Statistics':
            # Filter data for recession period (assuming 'Recession' column indicates recession periods)
            recession_data = df[df['Recession'] == 1]
            
            if recession_data.empty:
                return "No data available for recession periods."

            # Line chart for automobile sales over the recession period
            yearly_rec = recession_data.groupby('Year')['Automobile_Sales'].mean().reset_index()
            R_chart1 = dcc.Graph(figure=px.line(yearly_rec, x='Year', y='Automobile_Sales', title="Automobile Sales Over Recession Period"))
            
            # Bar chart for average sales by vehicle type during recession
            average_sales = recession_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
            R_chart2 = dcc.Graph(figure=px.bar(average_sales, x='Vehicle_Type', y='Automobile_Sales', title="Average Sales by Vehicle Type"))
            
            # Pie chart for total advertising expenditure during recession
            exp_rec = recession_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
            R_chart3 = dcc.Graph(figure=px.pie(exp_rec, values='Advertising_Expenditure', names='Vehicle_Type', title="Total Expenditure by Vehicle Type"))
            
            # Bar chart for the effect of unemployment rate on sales
            unemp_data = recession_data.groupby(['unemployment_rate', 'Vehicle_Type'])['Automobile_Sales'].mean().reset_index()
            R_chart4 = dcc.Graph(figure=px.bar(unemp_data, x='unemployment_rate', y='Automobile_Sales', color='Vehicle_Type',
                                               labels={'unemployment_rate': 'Unemployment Rate', 'Automobile_Sales': 'Avg Sales'},
                                               title='Effect of Unemployment Rate on Sales'))
            
            return [
                html.Div([R_chart1, R_chart2], style={'display': 'flex'}),
                html.Div([R_chart3, R_chart4], style={'display': 'flex'})
            ]
        
        elif selected_statistics == 'Yearly Statistics' and input_year:
            # Check if input_year is valid
            if input_year not in df['Year'].values:
                return "Invalid year selected. Please choose a valid year."
            
            yearly_data = df[df['Year'] == input_year]
            
            # Line chart for yearly automobile sales
            yas = df.groupby('Year')['Automobile_Sales'].mean().reset_index()
            Y_chart1 = dcc.Graph(figure=px.line(yas, x='Year', y='Automobile_Sales', title="Yearly Automobile Sales"))
            
            # Line chart for total monthly sales
            mas = df.groupby('Month')['Automobile_Sales'].sum().reset_index()
            Y_chart2 = dcc.Graph(figure=px.line(mas, x='Month', y='Automobile_Sales', title="Total Monthly Sales"))
            
            # Bar chart for average vehicles sold by type in the selected year
            avr_vdata = yearly_data.groupby('Vehicle_Type')['Automobile_Sales'].mean().reset_index()
            Y_chart3 = dcc.Graph(figure=px.bar(avr_vdata, x='Vehicle_Type', y='Automobile_Sales',
                                               title=f"Average Vehicles Sold by Type in {input_year}"))
            
            # Pie chart for total advertisement expenditure by vehicle type in the selected year
            exp_data = yearly_data.groupby('Vehicle_Type')['Advertising_Expenditure'].sum().reset_index()
            Y_chart4 = dcc.Graph(figure=px.pie(exp_data, values='Advertising_Expenditure', names='Vehicle_Type',
                                               title='Total Advertisement Expenditure by Vehicle'))
            
            return [
                html.Div([Y_chart1, Y_chart2], style={'display': 'flex'}),
                html.Div([Y_chart3, Y_chart4], style={'display': 'flex'})
            ]
        
        return "Please select a valid report type and year."
    
    except Exception as e:
        return f"Error: {str(e)}"

if __name__ == '__main__':
    app.run_server(debug=True)
