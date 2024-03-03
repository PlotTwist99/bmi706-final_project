import altair as alt
import pandas as pd
import streamlit as st

# Load data
@st.cache_data
def load_data():
    # May need to change this to load from github so that this will work from streamlit cloud
    life_expectancy = pd.read_csv('life_expectancy_clean.csv')
    return life_expectancy

def app():
    life_expectancy = load_data()

    top_col1, top_col2, top_col3, top_col4 = st.columns([2.5, 1, 2.5, 1])

    default_year = 2012
    default_countries = ['Canada', 'China']

    axis_variables = ['Life expectancy', 'Adult Mortality',
        'infant deaths', 'Alcohol', 'Hepatitis B',
        'Measles', 'BMI', 'under-five deaths', 'Polio', 'Total expenditure',
        'Diphtheria', 'HIV/AIDS', 'GDP', 'Population',
        'Income composition of resources', 'Schooling']

    with top_col1:
        # Y axis variables
        y_variable = st.selectbox(
            "Y-axis:",
            axis_variables, index=axis_variables.index('Life expectancy')
        )

    with top_col2:
        y_scale = st.radio("Scale", ('linear', 'log'), key='y-scale', horizontal=False)

    with top_col3:
        x_variable = st.selectbox(
            "X-axis:",
            axis_variables, index=axis_variables.index('Total expenditure')
        )

    with top_col4:
        x_scale = st.radio("Scale", ('linear', 'log'), key='x-scale', horizontal=False, index=0)

    # Charts
    chart_width = 600
    chart_height = 380
    country_selection = alt.selection_multi(fields=['Country'], empty='none', on='click',
                                             toggle='true', init=[{'Country': country} for country in default_countries])
    year_selection = alt.selection_single(fields=['Year'], empty='none', on='click', init={'Year': default_year})

    top_base = alt.Chart(life_expectancy).properties(width=chart_width, height=chart_height)

    scatter_plot = top_base.mark_point(filled=True).encode(
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
        trend_method = 'linear'  # shouldn't get here.

    trend_line = scatter_plot.transform_regression(
        x_variable, y_variable, method=trend_method
    ).mark_line(color='red')

    # Year Text:
    years_df = pd.DataFrame({
        'Year': range(life_expectancy['Year'].min(), life_expectancy['Year'].max() + 1),
        'LabelPosition': 1
    })

    year_text = alt.Chart(years_df).mark_text(
        align='right',
        baseline='top',
        dx=-5,
        dy=-5
    ).encode(
        x=alt.value(40),
        y=alt.value(8),
        text=alt.Text('Year:N'),
        color=alt.value('blue'),
        size=alt.value(16)
    ).transform_filter(
        year_selection
    )

    # Text Labels to selected countries
    text_labels = top_base.mark_text(align='left', dx=5, dy=-5).encode(
        x=alt.X(x_variable, type='quantitative', scale=alt.Scale(type=x_scale, zero=False)),
        y=alt.Y(y_variable, type='quantitative', scale=alt.Scale(type=y_scale, zero=False)),
        text='Country:N',
        color=alt.condition(country_selection, alt.value('black'), alt.value('transparent'))  # Make text transparent if not selected
    ).transform_filter(
        country_selection  # Apply the selection to filter labels
    ).transform_filter(
        year_selection
    )

    scatter_plot = scatter_plot.encode(
        color=alt.condition(country_selection, alt.value('red'), alt.value('steelblue')),
        size=alt.condition(country_selection, alt.value(100), alt.value(30))
    ).add_selection(
        country_selection
        # Note: year_selection is not added here since it's intended to be modified by another chart
    ).add_selection(year_selection).transform_filter(year_selection)

    top_chart = alt.layer(scatter_plot, trend_line, text_labels, year_text)

    # Display the chart (assuming you're using Streamlit or similar)
    # st.altair_chart(top_chart, use_container_width=True)
    #top_chart

    bottom_base = alt.Chart(life_expectancy).properties(width=chart_width, height=chart_height)
    line_chart = bottom_base.mark_point(filled=True).encode(
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
    ).add_selection(country_selection).transform_filter(country_selection).add_selection(year_selection)

    chart = alt.vconcat(top_chart, line_chart).resolve_scale(
        color='independent',
        size='independent'
    )
    st.altair_chart(chart, use_container_width=False)
