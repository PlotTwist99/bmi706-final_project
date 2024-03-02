import streamlit as st
import pandas as pd
import altair as alt

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('life_expectancy_clean.csv')
    return df

def app():
    df = load_data()
    default_countries = df['Country'].unique()[:5]
    selected_countries = st.multiselect('Select countries', df['Country'].unique(), default=default_countries)

    # year selector for the heatmap
    selected_year = st.slider('Select year for the heatmap', int(df['Year'].min()), int(df['Year'].max()), int(df['Year'].max()))

    # selection for countries
    country_selection = alt.selection_multi(fields=['Country'], name="country_selector")

    # filter the data based on selected countries
    line_bar_df = df[df['Country'].isin(selected_countries)]

    line_chart = alt.Chart(line_bar_df).mark_line(point=True).encode(
        x='Year:O',
        y='Life expectancy:Q',
        color='Country:N',
        tooltip=['Country', 'Year', 'Life expectancy'],
        opacity=alt.condition(country_selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        country_selection
    ).properties(
        title='Life Expectancy over Years',
        width=600,
        height=300
    )

    # Bar Plot for Adult Mortality
    bar_chart = alt.Chart(line_bar_df).mark_bar().encode(
        x='Year:O',
        y='Adult Mortality:Q',
        color='Country:N',
        tooltip=['Country', 'Year', 'Adult Mortality'],
        opacity=alt.condition(country_selection, alt.value(1), alt.value(0.2))
    ).add_selection(
        country_selection
    ).properties(
        title='Adult Mortality Rate over Years',
        width=600,
        height=300
    )

    # the Line and Bar Plot
    st.altair_chart(line_chart, use_container_width=True)
    st.altair_chart(bar_chart, use_container_width=True)

    # Heatmap
    heatmap_df = df[(df['Year'] == selected_year) & (df['Country'].isin(selected_countries))]

    diseases = ['Hepatitis B', 'Polio', 'Diphtheria']
    disease_data = heatmap_df.groupby('Country')[diseases].mean().reset_index()

    disease_data_melted = disease_data.melt(id_vars=['Country'], var_name='Disease', value_name='Immunization')

    # creating the heatmap
    heatmap = alt.Chart(disease_data_melted).mark_rect().encode(
        x='Disease:N',
        y='Country:N',
        color=alt.Color('Immunization:Q', scale=alt.Scale(scheme='yellowgreenblue')),
        tooltip=['Country', 'Disease', 'Immunization']
    ).properties(
        title='Immunization Coverage among 1-year-olds (%) by Country',
        width=600,
        height=400
    )

    st.altair_chart(heatmap, use_container_width=True)
