import streamlit as st
import pandas as pd
import altair as alt
from vega_datasets import data

# load data
@st.cache_data
def load_data():
    data = pd.read_csv("life_expectancy_clean.csv")
    return data
df = load_data()
# update column names of df
new_df = df.rename(columns={'Life expectancy': 'Life Expectancy',
    'under-five deaths': 'Mortality for Children', 
    'Adult Mortality': 'Mortality for Adults', 
    'infant deaths': 'Mortality for Infants'})

# metric selection
metric_options = {
    'Life Expectancy': 'Life Expectancy',
    'Mortality for Children': 'Mortality for Children', 
    'Mortality for Adults': 'Mortality for Adults',
    'Mortality for Infants': 'Mortality for Infants'
}
metric = st.radio('Select Metric for Visualization', list(metric_options.keys()))

# title of the Streamlit app
st.title('World ' + metric + ' Trends')

# interactive selection of countries & year
default_countries = ['United States of America', 'Canada']
selected_countries = st.multiselect('Select Countries', options=new_df['Country'].unique(), default=default_countries)
years = st.slider("Select Year Range", int(new_df['Year'].min()), int(new_df['Year'].max()), (2000, 2015))

# update filtered data based on selections
filtered_data = new_df[(new_df['Country'].isin(selected_countries)) & (new_df['Year'] >= years[0]) & (new_df['Year'] <= years[1])]

# aggregate the data for the map visualization 
aggregated_data = filtered_data.groupby('Country')[metric_options[metric]].mean().reset_index()
country_codes = new_df[['Country', 'country_code_numeric']].drop_duplicates()
aggregated_data = pd.merge(aggregated_data, country_codes, on='Country', how='left')

# map visualization
source = alt.topo_feature(data.world_110m.url, 'countries')
background = alt.Chart(source).mark_geoshape(fill='lightgray', stroke='white').properties(width=800, height=400).project('equirectangular')

# define a color scale based on the selected metric's aggregated values
metric_scale = alt.Scale(domain=[aggregated_data[metric].min(), aggregated_data[metric].max()], scheme='yellowgreenblue')
metric_color = alt.Color(metric, type="quantitative", scale=metric_scale, legend=alt.Legend(title=metric))

# add colored countries based on selection and the aggregated metric's value
countries_layer = alt.Chart(source).transform_lookup(
    lookup='id',
    from_=alt.LookupData(aggregated_data, 'country_code_numeric', [metric, 'Country']),
    default='Other'
).mark_geoshape(stroke='white').encode(
    color=metric_color,
    tooltip=['Country:N', alt.Tooltip(f'{metric_options[metric]}:Q', title=metric)]
).properties(
    width=800,
    height=400
).project('equirectangular')

# combine the background and countries layer
map_chart = background + countries_layer
st.altair_chart(map_chart, use_container_width=True)

# function to create line charts for different metrics
def create_line_chart(data, metric_col):
    chart = alt.Chart(data).mark_line(point=True).encode(
        x='Year:N',
        y=alt.Y(f'{metric_col}:Q', title=metric),
        color='Country:N',
        tooltip=['Country:N', 'Year:N', alt.Tooltip(f'{metric_col}:Q', title=metric)]
    ).properties(title=f'{metric} Trends by Country from {years[0]} to {years[1]}', width=800, height=400).interactive()
    return chart

# display conditional plots based on the selected metric
chart_metric = metric_options[metric]
chart = create_line_chart(filtered_data, chart_metric)
st.altair_chart(chart, use_container_width=True)
