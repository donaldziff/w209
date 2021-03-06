from altair import Chart, X, Y, Axis, Data, DataFormat
import pandas as pd
import numpy as np
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify, abort
from web import app
from web.utils import utils
import json
import altair as alt


alt.data_transformers.disable_max_rows()

def make_plots(source):

    # category selection

    cat_selection = alt.selection_single(empty = 'all', fields=['Category'], clear=alt.EventStream(type='dblclick'))
    cat_color = alt.condition(cat_selection, 'Category:N', alt.ColorValue('whitesmoke'), legend=None)
    cat_legend = alt.Chart(source, title=['Category', 'Click here']).mark_circle(size=80).encode(
        y=alt.Y('Category:N', title=" ", axis=alt.Axis(orient='right')),
        color=cat_color
    ).add_selection(
        cat_selection
    )

    # scatterplot global configuration - with single selection
    width=300
    height=300
    circle_size=60
    single_select = alt.selection_single(empty = 'all', fields=['ASIN'], clear=alt.EventStream(type='dblclick'))
    color = alt.condition(single_select, 'Category:N', alt.ColorValue('transparent'), legend=None)

    tooltip=[alt.Tooltip('Product_Name', title='Name'), 'ASIN', alt.Tooltip('Est_Monthly_Sales', title='Monthly Sales'),
         'Category', 'Reviews', 'LQS', 'Net', 'Price']


    def make_base_chart(x, title):
        result = alt.Chart(source, title=title).mark_circle(size=circle_size).encode(
            x = alt.X(x, title=x),
            # x = x,
            y = alt.Y('Est_Monthly_Sales', title='Monthly Sales', scale=alt.Scale(domain=[0, 1600])),
            color=color,
            tooltip=tooltip
        ).transform_filter(
            cat_selection
        ).add_selection(
            single_select
        ).properties(
            height=height,
            width=width
        )
        return result

    from altair import datum

    # sliders galore
    def make_slider_set(dimension, min, max, step, name=None):
        if name is None:
            name = dimension
        range_start = alt.binding_range(min=min, max=max, step=step, name=name + ' (min)')
        range_end = alt.binding_range(min=min, max=max, step=step, name=name + ' (max)')

        select_range_start = alt.selection_single(name=dimension + "_select_range_start", fields=[dimension], bind=range_start, init={dimension: min})
        select_range_end   = alt.selection_single(name=dimension + "_select_range_end"  , fields=[dimension], bind=range_end,   init={dimension: max})

        return {'start': select_range_start,
                'end': select_range_end}

    sliders = {}
    sliders['Est_Monthly_Sales'] = make_slider_set('Est_Monthly_Sales', 0, 1600, 10, name='Monthly Sales')
    sliders['LQS'] = make_slider_set('LQS', 0, 8, .5)
    sliders['Reviews'] = make_slider_set('Reviews', 0, 60, 1)
    sliders['Net'] = make_slider_set('Net', 0, 45, 1)
    sliders['Rating'] = make_slider_set('Rating', 0, 5, .5)

    def add_sliders(c):
        for dimension in ['Est_Monthly_Sales', 'LQS', 'Reviews', 'Net', 'Rating']:
            c = c.add_selection(sliders[dimension]['start'], sliders[dimension]['end']
            ).transform_filter(
                (datum[dimension] >= sliders[dimension]['start'][dimension]) &
                (datum[dimension] <= sliders[dimension]['end'][dimension])
            )
        return c

    reviews_vs_sales = add_sliders(make_base_chart('Reviews', ["Reviews vs. Demand", "Number of Reviews indicates Competition"]))
    lqs_vs_sales = add_sliders(make_base_chart('LQS', ["Listing Quality Score vs. Demand", "Low LQS indicates Bad Marketing"]))
    net_vs_sales = add_sliders(make_base_chart('Net', ["Estimated Net vs Demand", "Indicates Return on Investment"]))
    rating_vs_sales = add_sliders(make_base_chart('Rating', ["Quality Rating vs Demand", "Low Quality indicates Opportunity"]))

    # guide lines

    sales_y = alt.Chart(pd.DataFrame({'y': [200]})).mark_rule(color='red').encode(y='y')
    reviews_x = alt.Chart(pd.DataFrame({'x': [50]})).mark_rule(color='red').encode(x='x')
    lqs_x = alt.Chart(pd.DataFrame({'x': [5.5]})).mark_rule(color='red').encode(x='x')
    net_x = alt.Chart(pd.DataFrame({'x': [15]})).mark_rule(color='red').encode(x='x')
    rating_x = alt.Chart(pd.DataFrame({'x': [3.7]})).mark_rule(color='red').encode(x='x')

    reviews_plot = reviews_vs_sales + sales_y + reviews_x
    lqs_plot = lqs_vs_sales + sales_y + lqs_x
    net_plot = net_vs_sales + sales_y + net_x
    rating_plot = rating_vs_sales + sales_y +rating_x

    plots = {'reviews': reviews_plot,
             'lqs': lqs_plot,
             'net': net_plot,
             'rating': rating_plot,
             'cat_legend': cat_legend}
    return plots

@app.route("/")
@app.route("/allcategory")
def plot_all_category_global():
    # Loading raw data and clean it
    df = utils.load_data()
    df = utils.clean_data(df)

    ## drop off outliers
    df = df.loc[(df['Est_Monthly_Sales'] <1500) & (df['Reviews'] <60)]

    plots = make_plots(df)
    reviews_plot = plots['reviews']
    lqs_plot = plots['lqs']
    cat_legend = plots['cat_legend']
    net_plot = plots['net']
    rating_plot = plots['rating']

    plot_product_scatterchart =  ( reviews_plot | lqs_plot | cat_legend ) & ( net_plot | rating_plot)

    plot_product_scatterchart_json = plot_product_scatterchart.to_json()


    '''
    # 3/31/2021 (Ivan) Begin: Comment out this block of code to remove the 4 graphs.

    #########################################
    # ploting - AMZN Product Data Bar Chart
    #########################################

    plot_product_bar = alt.Chart(df).mark_bar().encode(
    x='LQS',
    y='Net:Q',
    color= 'Category:N',
    tooltip=['Sellers', 'LQS', 'Reviews', 'Rank', 'Fees', 'Net', 'Est_Monthly_Sales','Est_Monthly_Revenue', 'Category', 'Product_Name']
).properties(width=375, height=200)

    plot_product_bar_json = plot_product_bar.to_json()

    #########################################
    # ploting - AMZN Product Data Line Chart
    #########################################

    plot_product_line = alt.Chart(df).mark_line().encode(
    x='Rank',
    y='Reviews:Q',
    color= 'Category:N',
    tooltip=['Sellers', 'LQS', 'Reviews', 'Rank', 'Fees', 'Net', 'Est_Monthly_Sales','Est_Monthly_Revenue', 'Category', 'Product_Name']
).properties(width=375, height=200)

    plot_product_line_json = plot_product_line.to_json()

    ###############################################
    # ploting - AMZN Product Data Bar Chart by Year
    ###############################################

    plot_product_bar_year = alt.Chart(df).mark_bar().encode(
    x='year(Date_First_Available):T',
    y='Price',
    color='Category',
    tooltip=['year(Date_First_Available)', 'Sellers', 'LQS', 'Reviews', 'Rank', 'Fees', 'Net', 'Est_Monthly_Sales','Est_Monthly_Revenue', 'Category', 'Product_Name']
).properties(
            height=200,
            width=375,
            ).interactive()

    plot_product_bar_year_json = plot_product_bar_year.to_json()

    #########################################################
    # ploting - AMZN Product Data Bar Chart by Year/Qtr/Month
    #########################################################

    plot_product_bar_yearqtrmonth = alt.Chart(df).mark_bar().encode(
    x='yearquartermonth(Date_First_Available):T',
    y='Price',
    color='Category',
    tooltip=['yearquartermonth(Date_First_Available)', 'Sellers', 'LQS', 'Reviews', 'Rank', 'Fees', 'Net', 'Est_Monthly_Sales','Est_Monthly_Revenue', 'Category', 'Product_Name']
).properties(
            height=200,
            width=375,
            ).interactive()

    plot_product_bar_yearqtrmonth_json = plot_product_bar_yearqtrmonth.to_json()


    # 3/31/2021 (Ivan) End: Comment out this block of code to remove the 4 graphs.
    '''

    ################################
    # finalize data send to template
    ################################
    total_category_count = df['Category'].unique().shape[0]
    total_product_count = df.shape[0]
    average_rank = round(df["Rating"].mean(),2)

    '''
    # 3/31/2021 (Ivan) Begin: Comment out this block of code to remove the 4 graphs.

    context = {"total_category_count": total_category_count,
               "total_product_count": total_product_count,
               "average_rank": average_rank,
               "plot_scatterchart_product": plot_product_scatterchart_json,
               "plot_bar_product": plot_product_bar_json,
               "plot_line_product": plot_product_line_json,
               "plot_bar_year_product": plot_product_bar_year_json,
               "plot_bar_yearqtrmonth_product": plot_product_bar_yearqtrmonth_json
               }

    # 3/31/2021 (Ivan) End: Comment out this block of code to remove the 4 graphs.
    '''
    context = {"total_category_count": total_category_count,
               "total_product_count": total_product_count,
               "average_rank": average_rank,
               "plot_scatterchart_product": plot_product_scatterchart_json
               }

    return render_template('all_category.html', context=context )

# Ivan changed code 2-3-2021
@app.route("/category", methods=['POST'])
def plot_category():
    category_name = request.form['category_name'] + " "

    # Loading raw data and clean it
    df = utils.load_category_data(category_name)
    df = utils.clean_data(df)


    ################################
    # Plot per category data
    ################################

    brush = alt.selection_interval()

    category_points = alt.Chart(df).mark_circle().encode(
        x='Est_Monthly_Sales:Q',
        y='Est_Monthly_Revenue:Q',
        color=alt.condition(brush, 'Category:N', alt.value('lightgray')),
        tooltip=['Sellers', 'LQS', 'Reviews', 'Rank', 'Fees', 'Net', 'Est_Monthly_Sales','Est_Monthly_Revenue', 'Category', 'Product_Name']
    ).properties(width=1000, height=500).add_selection(
        brush
    )

    category_bars = alt.Chart(df).mark_bar().encode(
        y='Category:N',
        color='Category:N',
        x='count(Category):Q'
    ).properties(width=1000, height=100).transform_filter(
        brush
    )

    plot_category_product_scatterchart =  category_points & category_bars

    plot_category_product_scatterchart_json = plot_category_product_scatterchart.to_json()


    ################################
    # finalize data send to template
    ################################
    total_product_count = df.shape[0]
    average_rank = df[['Rank']].mean().values.round(2)

    context = {"category_name": category_name,
                "total_product_count": total_product_count,
               "average_rank": average_rank,
               'altair_category_product_plot': plot_category_product_scatterchart_json
               }

    return render_template('category.html', context=context)


##################################
# 4/5/2021 Add about page by Ivan
##################################
@app.route("/about")
def show_about_page():

    ################################
    # finalize data send to template
    ################################
    page_name = "About"

    context = {"page_name": page_name}

    return render_template('about.html', context=context)
