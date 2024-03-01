import altair as alt
import pandas as pd
import streamlit as st

# Load data
def load_data():
    # May need to change this to load from github so that this will work from streamlit cloud
    life_expectancy = pd.read_csv('./life_expectancy_clean.csv')
    return life_expectancy


life_expectancy = load_data()
min_year = life_expectancy.Year.min()
max_year = life_expectancy.Year.max()

top_col1, top_col2 = st.columns([1, 5])

with top_col1:
    toggle_option = st.radio(
        "Choose:",
        ('Year', 'Countries')
    )

with top_col2:
    if toggle_option == 'Year':
        year = st.slider('Select a Year', min_value=min_year, max_value=max_year, value=2010)
    elif toggle_option == 'Countries':
        countries = st.multiselect('Select Countries', life_expectancy['Country'].unique(),
                                   default=['Canada', 'China'])

if toggle_option == 'Year':
    st.write(f"Displaying data for the year: {year}")
    pass
elif toggle_option == 'Countries':
    st.write(f"Displaying data for countries: {', '.join(countries)}")


bottom_col1, bottom_col2 = st.columns([1, 4])

axis_variables = ['Life expectancy', 'Adult Mortality',
       'infant deaths', 'Alcohol', 'percentage expenditure', 'Hepatitis B',
       'Measles', 'BMI', 'under-five deaths', 'Polio', 'Total expenditure',
       'Diphtheria', 'HIV/AIDS', 'GDP', 'Population',
       'Income composition of resources', 'Schooling']

with bottom_col1:
    # Y axis variables
    y_variable = st.selectbox(
        "Y-axis:",
        axis_variables, index=axis_variables.index('Life expectancy')
    )
    y_scale = st.radio("Y-axis scale:", ('linear', 'log'))

    # X variable will be x axis or size depending on chart type.
    x_name = "X-axis" if toggle_option == 'Year' else "Size"
    x_variable = st.selectbox(
        f"{x_name}:",
        axis_variables, index=axis_variables.index('GDP')
    )
    x_scale = st.radio(f"{x_name} scale:", ('linear', 'log'))

    if toggle_option == 'Year':
        pass
    elif toggle_option == 'Countries':
        pass

with bottom_col2:
    if toggle_option == 'Year':
        base_chart = alt.Chart(life_expectancy[life_expectancy.Year==year])

        # Create the base scatter plot
        scatter_plot = base_chart.mark_point(filled=True).encode(
            x=alt.X(x_variable, type='quantitative', scale=alt.Scale(type=x_scale, zero=False)),
            y=alt.Y(y_variable, type='quantitative', scale=alt.Scale(type=y_scale, zero=False)),
                tooltip=[
                alt.Tooltip('Country:N'),
                alt.Tooltip(f'{y_variable}:Q'),
                alt.Tooltip(f'{x_variable}:Q')
                ]
        )

        if y_scale == x_scale:
            trend_method = 'linear'
        elif y_scale == 'linear' and x_scale == 'log':
            trend_method = 'log'
        elif y_scale == 'log' and x_scale == 'linear':
            trend_method = 'exp'
        else:
            trend_method = 'linear' # shouldn't get here.
        trend_line = scatter_plot.transform_regression(
            x_variable, y_variable, method=trend_method
        ).mark_line(color='red')


        chart = scatter_plot + trend_line

        # Display the chart
        st.altair_chart(chart, use_container_width=True)
    elif toggle_option == 'Countries':
        base_chart = alt.Chart(life_expectancy[life_expectancy['Country'].isin(countries)])
        line_chart = base_chart.mark_point(filled=True).encode(
            x='Year:O',
            y=alt.Y(y_variable, type='quantitative', scale=alt.Scale(type=y_scale, zero=False)),
            #order='Year:O',
            color='Country:N',
            size=alt.Size(x_variable, type='quantitative', scale=alt.Scale(type=x_scale)),
            tooltip=[
            alt.Tooltip('Country:N'),
            alt.Tooltip(f'{y_variable}:Q'),
            alt.Tooltip(f'{x_variable}:Q'),
            alt.Tooltip('Year:Q')
            ]
        )
        st.altair_chart(line_chart, use_container_width=True)     