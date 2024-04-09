import streamlit as st
import pickle
import pandas as pd
import plotly.express as px
#import matplotlib.pyplot as plt
import plotly.graph_objects as go
# st.title("Test test please work I need this")


reg_post_covid_df_1 = pd.read_csv('https://headstartdata.sfo2.cdn.digitaloceanspaces.com/regional_df1.csv')
# print(reg_post_covid_df_1.head())

##This is pulling the year out of the region column and then making a new 'year' column. It's easier to plot this way.

reg_post_covid_df_2 = reg_post_covid_df_1

reg_post_covid_df_2['Year'] = reg_post_covid_df_2['Unnamed: 0'].str.extract('(\(.*\))')

reg_post_covid_df_2['Region'] = reg_post_covid_df_2['Unnamed: 0'].str.replace('\s\(.*\)', '', regex=True)

reg_post_covid_df_2.drop('Unnamed: 0', axis=1, inplace=True)

reg_post_covid_df_2['Year'] = reg_post_covid_df_2['Year'].str.replace('[()]', '', regex=True)

region_to_states = {
    'Region 1': ['ME', 'VT', 'NH', 'MA', 'CT', 'RI'],
    'Region 2': ['NY', 'NJ', 'PR', 'VI'],
    'Region 3': ['PA', 'MD', 'DE', 'WV', 'VA'],
    'Region 4': ['FL', 'GA', 'KY', 'TN', 'NC', 'SC', 'MS', 'AL'],
    'Region 5': ['MN', 'WI', 'MI', 'IL', 'IN', 'OH'],
    'Region 6': ['TX', 'NM', 'OK', 'AR', 'LA'],
    'Region 7': ['KS', 'MO', 'NE', 'IA'],
    'Region 8': ['UT', 'CO', 'WY', 'MT', 'ND', 'SD'],
    'Region 9': ['CA', 'NV', 'AZ', 'HI'],
    'Region 10': ['AK', 'WA', 'OR', 'ID']
}
#I'm creating a new dataframe called df_states to use for plotting.
state_to_region = {state: region for region, states in region_to_states.items() for state in states}

df_states = pd.DataFrame([(state, region) for region, states in region_to_states.items() for state in states], columns=['State', 'Region'])
df_states['Year'] = 2021


df_states['Region'] = df_states['Region'].astype(str)
df_states['Year'] = df_states['Year'].astype(str)

reg_post_covid_df_2['Region'] = reg_post_covid_df_2['Region'].astype(str)
reg_post_covid_df_2['Year'] = reg_post_covid_df_2['Year'].astype(str)

df_states = df_states.merge(reg_post_covid_df_2, on=['Region', 'Year'])

#Deriving new columns for the various levels of education as a percentage of their total staff.
df_states['Advanced Degree(HS) %'] = (df_states['Advanced Degree(HS)'] / df_states['Total staff(HS)']) * 100
df_states['Bachelor\'s Degree(HS) %'] = (df_states['Bachelor\'s Degree(HS)'] / df_states['Total staff(HS)']) * 100
df_states['Associate\'s Degree(HS) %'] = (df_states['Associate\'s Degree(HS)'] / df_states['Total staff(HS)']) * 100

df_states['Advanced Degree(EHS) %'] = (df_states['Advanced Degree(EHS)'] / df_states['Total staff(EHS)']) * 100
df_states['Bachelor\'s Degree(EHS) %'] = (df_states['Bachelor\'s Degree(EHS)'] / df_states['Total staff(EHS)']) * 100
df_states['Associate\'s Degree(EHS) %'] = (df_states['Associate\'s Degree(EHS)'] / df_states['Total staff(EHS)']) * 100



initial_metric = 'Advanced Degree(HS) %'

fig = go.Figure(go.Choropleth(
    locations=df_states['State'],
    z=df_states[initial_metric],
    locationmode='USA-states',
    colorscale='Viridis',
    colorbar_title=f"{initial_metric} of Total",
))

buttons = [
    {
        "label": f"{metric} %",
        "method": "update",
        "args": [{"z": [df_states[f"{metric} %"]], "colorbar": {"title": f"{metric} % of Total"}}]
    }
    for metric in ['Advanced Degree(HS)', 'Bachelor\'s Degree(HS)', 'Associate\'s Degree(HS)']
]


fig.update_layout(
    title_text='US Educational Staff Metrics by Region (%)',
    geo_scope='usa',
    updatemenus=[{
        "buttons": buttons,
        "direction": "down",
        "showactive": True,
    }]
)

st.title("HeadStart Regional Data Visualized")

# Use Streamlit to display the Plotly figure
st.plotly_chart(fig)


# Assuming reg_post_covid_df_1 is structured with one row per region-year-feature combination
# Initialize the figure


############################################

fig1 = go.Figure()
# Feature list for the dropdown
features = [
    'HS dropouts who did not re-enroll', 'HS dropouts within 45 days', 'Predicted HS to kindergarten',
    'EHS dropouts who did not re-enroll', 'EHS dropouts within 45 days',
    'aged out of Early Head Start', 'EHS to HS',
    'EHS to nonHS early childhood program', 'EHS aged out to no further early child education'
]

# Initial plot - using the first feature as an example
for region in reg_post_covid_df_1['Region'].unique():
    df_filtered = reg_post_covid_df_1[reg_post_covid_df_1['Region'] == region]
    fig1.add_trace(go.Scatter(
        x=df_filtered['Year'],
        y=df_filtered[features[0]],  # Initial feature
        mode='lines+markers',
        name=region
    ))

# Dropdown buttons for selecting features
buttons1 = [
    {
        "label": feature,
        "method": "update",
        "args": [{"y": [
                    reg_post_covid_df_1[reg_post_covid_df_1['Region'] == region][feature]
                    for region in reg_post_covid_df_1['Region'].unique()
                 ],
                  "x": [
                    reg_post_covid_df_1[reg_post_covid_df_1['Region'] == region]['Year']
                    for region in reg_post_covid_df_1['Region'].unique()
                 ]}]
    } for feature in features
]

# Add dropdowns to the figure
fig1.update_layout(
    updatemenus=[{
        "buttons": buttons1,
        "direction": "down",
        "showactive": True,
    }],
    title_text="Yearly Metrics by Region"
)

# Show the figure
st.plotly_chart(fig1)

#######################################################


health_vars = ['Children with health insurance %',
       'Children diagnosed with any chronic condition %',
       'Children receiving treatment for chronic condition %',
       'Children with access to dental care %']

for var in health_vars:
    original_var = var.replace(' %', '')
    reg_post_covid_df_2[var] = reg_post_covid_df_2[original_var] / reg_post_covid_df_2['Total Enrollment'] * 100

dropout_columns = ['HS dropouts who did not re-enroll', 'EHS dropouts who did not re-enroll']
reg_post_covid_df_2['Cumulative Dropout Rate (%)'] = reg_post_covid_df_2[dropout_columns].sum(axis=1) / reg_post_covid_df_2['Total Enrollment'] * 100

# Define a color for each region (you can choose your own colors)
region_colors = {
    'Region 1': 'blue', 'Region 2': 'green', 'Region 3': 'red', 'Region 4': 'cyan',
    'Region 5': 'magenta', 'Region 6': 'yellow', 'Region 7': 'black', 'Region 8': 'purple',
    'Region 9': 'orange', 'Region 10': 'grey'
}

# Apply the color mapping to your DataFrame
reg_post_covid_df_2['Color'] = reg_post_covid_df_2['Region'].map(region_colors)

import plotly.graph_objects as go

# Ensure the DataFrame `reg_post_covid_df_1` has the percentage columns
# ...

# Initialize the figure with the first health variable
initial_var = health_vars[0]
fig2 = go.Figure()

# Create and add the scatter plot for the initial variable
fig2.add_trace(
    go.Scatter(
        x=reg_post_covid_df_2[initial_var],
        y=reg_post_covid_df_2['Cumulative Dropout Rate (%)'],
        mode='markers',
        marker=dict(color=reg_post_covid_df_2['Color']),
        text=reg_post_covid_df_2.apply(lambda row: f"{row['Region']} {row['Year']}", axis=1),
        hoverinfo='text'
    )
)

# Create the buttons for the update menu, using the correct column names
buttons2 = [
    dict(
        args=[
            {"x": [reg_post_covid_df_2[var].tolist()]},  # Updates the x-axis data
            {"xaxis": {"title": var}}  # Updates the x-axis title
        ],
        label=var,
        method='update'
    )
    for var in health_vars
]


# Update the layout to include dropdown buttons
fig2.update_layout(
    updatemenus=[
        {
            "buttons": buttons2,
            "direction": "down",
            "pad": {"r": 10, "t": 10},
            "showactive": True,
            "x": 0.1,
            "xanchor": "left",
            "y": 1.1,
            "yanchor": "top"
        }
    ],
    title='Cumulative Dropout Rate vs. Health Metrics (%) by Region',
    xaxis=dict(title=initial_var),  # Set initial x-axis title
    yaxis=dict(title='Cumulative Dropout Rate (%)')  # Set y-axis title
)

# Show the figure
st.plotly_chart(fig2)

###############################################

import plotly.graph_objects as go
# Assuming reg_post_covid_df_2 has the necessary data prepared, including the 'Color' column

# Convert features into percentages of Total Enrollment
features = [
    'HS dropouts who did not re-enroll', 'HS dropouts within 45 days', 'Predicted HS to kindergarten',
    'EHS dropouts who did not re-enroll', 'EHS dropouts within 45 days',
    'aged out of Early Head Start', 'EHS to HS',
    'EHS to nonHS early childhood program', 'EHS aged out to no further early child education'
]
for feature in features:
    percentage_feature_name = f"{feature} (% of Total Enrollment)"
    reg_post_covid_df_2[percentage_feature_name] = (reg_post_covid_df_2[feature] / reg_post_covid_df_2['Total Enrollment']) * 100

# Initialize the figure
fig3 = go.Figure()

# Add a trace for the initial feature for each region
percentage_features = [f"{feature} (% of Total Enrollment)" for feature in features]
initial_feature = percentage_features[0]

# Assuming 'Region' and 'Year' are appropriate columns in your DataFrame
for region in reg_post_covid_df_2['Region'].unique():
    df_filtered = reg_post_covid_df_2[reg_post_covid_df_2['Region'] == region]
    fig3.add_trace(go.Scatter(
        x=df_filtered['Year'],
        y=df_filtered[initial_feature],
        mode='lines+markers',
        name=region,
        text=region,  # Display 'Region' on hover
        hoverinfo='text+y+x'
    ))

# Create dropdown buttons for selecting features
dropdown_buttons = [
    dict(
        args=[
            {"y": [reg_post_covid_df_2[reg_post_covid_df_2['Region'] == region][feature].values.tolist() for region in reg_post_covid_df_2['Region'].unique()],
             "x": [reg_post_covid_df_2[reg_post_covid_df_2['Region'] == region]['Year'].values.tolist() for region in reg_post_covid_df_2['Region'].unique()]},
            {"xaxis": {"title": feature}, "yaxis": {"title": "Percentage of Total Enrollment"}}
        ],
        label=feature,
        method="update"
    )
    for feature in percentage_features
]

# Update the layout to include dropdown buttons
fig3.update_layout(
    updatemenus=[
        {
            "buttons": dropdown_buttons,
            "direction": "down",
            "pad": {"r": 10, "t": 10},
            "showactive": True,
            "x": 0.1,
            "xanchor": "left",
            "y": 1.15,
            "yanchor": "top"
        }
    ],
    title="Completion and Attrition Rates by Region and Year",
    xaxis_title="Year",
    yaxis_title="Percentage of Total Enrollment"
)

# Show the figure
st.plotly_chart(fig3)

###############################################
