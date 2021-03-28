from altair import Chart, X, Y, Axis, Data, DataFormat
import pandas as pd
import numpy as np
from flask import render_template, url_for, flash, redirect, request, make_response, jsonify, abort
from web import app
from web.utils import utils
import json
import altair as alt


alt.data_transformers.disable_max_rows()

@app.route("/")
@app.route("/allcategory")
def plot_all_category_global():
    # Loading raw data and clean it
    df = utils.load_data()
    df = utils.clean_data(df)


    #########################################
    # ploting - AMZN Product Data ScatterPlot
    #########################################

    brush = alt.selection_interval()

    input_dropdown = alt.binding_select(options=["Arts, Crafts & Sewing", "Automotive", "Baby", "Beauty & Personal Care",  "Clothing, Shoes & Jewelry", "Health & Household", "Home & Kitchen", "Kitchen & Dining", "Musical Instruments", "Patio, Lawn & Garden", "Pet Supplies", "Sports & Outdoors", "Tools & Home Improvement", "Toys & Games", "Video Games"], name="Select a category..." )

    selection = alt.selection_single(fields=['Category'], bind=input_dropdown, clear=alt.EventStream(type='dblclick'))

    points = alt.Chart(df).mark_circle().encode(
        x='Est_Monthly_Sales:Q',
        y='Est_Monthly_Revenue:Q',
        color = alt.condition(selection,
                                alt.Color('Category:N', legend=None),
                                alt.value('lightgray')),
        tooltip=['Sellers', 'LQS', 'Reviews', 'Rank', 'Fees', 'Net', 'Est_Monthly_Sales','Est_Monthly_Revenue', 'Category', 'Product_Name']
    ).properties(width=1000, height=500).add_selection(
        brush
    ).add_selection(
        selection
    ).transform_filter(
        selection)

    bars = alt.Chart(df).mark_bar().encode(
        y='Category:N',
        color='Category:N',
        x='count(Category):Q'
    ).properties(width=1000, height=200).transform_filter(
        brush
    )

    plot_product_scatterchart =  points & bars

    plot_product_scatterchart_json = plot_product_scatterchart.to_json()


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

    ################################
    # finalize data send to template
    ################################
    total_category_count = "23"
    total_product_count = df.shape[0]
    average_rank = "5"


    context = {"total_category_count": total_category_count,
               "total_product_count": total_product_count,
               "average_rank": average_rank,
               "plot_scatterchart_product": plot_product_scatterchart_json,
               "plot_bar_product": plot_product_bar_json,
               "plot_line_product": plot_product_line_json,
               "plot_bar_year_product": plot_product_bar_year_json,
               "plot_bar_yearqtrmonth_product": plot_product_bar_yearqtrmonth_json
               }

    return render_template('all_category.html', context=context )



@app.route("/rong1")
def rong1():
    # Loading raw data and clean it
    df = utils.load_data()
    df = utils.clean_data(df)


    ## to drop off outliers, choose data that has 'Est_Monthly_Sales' <1500 & 'Reviews' <200)
    source = df.loc[(df['Est_Monthly_Sales'] <1500) & (df['Reviews'] <200)]

    brush = alt.selection(type='interval', resolve='global')

    height=300
    width=300

    ## chart1-High Demand and Low Competition
    chart1 = alt.Chart(source,title="High Demand and Low Competition").transform_calculate(
        url='https://www.amazon.com/dp/' + alt.datum.ASIN
    ).mark_circle(size=60).encode(
        x='Reviews',
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'ASIN:O', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','url:N','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## chart2 - High Demand and Bad Marketing
    chart2 = alt.Chart(source,title="High Demand and Bad Marketing").mark_circle(size=60).encode(
        x='LQS',
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'ASIN:O', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','ASIN','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## chart3 - Good Return on Investment  
    chart3 = alt.Chart(source,title="Good Return on Investment").mark_circle(size=60).encode(
        x='Price',
        y='Net',
        color=alt.condition(brush, 'ASIN:O', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','ASIN','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## chart4 - Good Demand & Poor Quality

    chart4 = alt.Chart(source,title="Good Demand & Poor Quality").mark_circle(size=60).encode(
        x='Rating',
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'ASIN:O', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','ASIN','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## line1 Est_Monthly_Sales >= 200
    line1 = alt.Chart(pd.DataFrame({'y': [200]})).mark_rule(color='red').encode(y='y')
    ## line2 Reviews <=50
    line2 = alt.Chart(pd.DataFrame({'x': [50]})).mark_rule(color='red').encode(x='x')
    ## line3 LQS <6
    line3 = alt.Chart(pd.DataFrame({'x': [6]})).mark_rule(color='red').encode(x='x')
    ## line4 Price>20
    line4 = alt.Chart(pd.DataFrame({'x': [20]})).mark_rule(color='red').encode(x='x')
    ## line5 Net>15
    line5 = alt.Chart(pd.DataFrame({'y': [15]})).mark_rule(color='red').encode(y='y')
    ## line6 Rating<3.7
    line6 = alt.Chart(pd.DataFrame({'x': [3.7]})).mark_rule(color='red').encode(x='x')
    
    plot_product_scatterchart =  chart1 + line1 + line2|chart2 + line1 + line3|chart3 + line5 +line4|chart4 + line1 + line6
    
    plot_product_scatterchart_json = plot_product_scatterchart.to_json()


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

    ################################
    # finalize data send to template
    ################################
    total_category_count = "23"
    total_product_count = df.shape[0]
    average_rank = "5"


    context = {"total_category_count": total_category_count,
               "total_product_count": total_product_count,
               "average_rank": average_rank,
               "plot_scatterchart_product": plot_product_scatterchart_json,
               "plot_bar_product": plot_product_bar_json,
               "plot_line_product": plot_product_line_json,
               "plot_bar_year_product": plot_product_bar_year_json,
               "plot_bar_yearqtrmonth_product": plot_product_bar_yearqtrmonth_json
               }

    return render_template('all_category.html', context=context )


@app.route("/max1")
def max1():
    # Loading raw data and clean it
    df = utils.load_data()
    df = utils.clean_data(df)

    ## to drop off outliers, choose data that has 'Est_Monthly_Sales' <1500 & 'Reviews' <200)
    source = df.loc[(df['Est_Monthly_Sales'] <1500) & (df['Reviews'] <40)]

    brush = alt.selection(type='interval', resolve='global')

    height=300
    width=300

    ## chart1-High Demand and Low Competition
    chart1 = alt.Chart(source,title="High Demand and Low Competition").transform_calculate(
        url='https://www.amazon.com/dp/' + alt.datum.ASIN
    ).mark_circle(size=60).encode(
        x = alt.X('Reviews', scale=alt.Scale(domain=[0, 40])),
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'Category:N', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','url:N','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## chart2 - High Demand and Bad Marketing
    chart2 = alt.Chart(source,title="High Demand and Bad Marketing").mark_circle(size=60).encode(
        x='LQS',
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'Category:N', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','ASIN','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## chart3 - Good Return on Investment  
    chart3 = alt.Chart(source,title="Good Return on Investment").mark_circle(size=60).encode(
        x='Net',
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'Category:N', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','ASIN','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## chart4 - Good Demand & Poor Quality

    chart4 = alt.Chart(source,title="Good Demand & Poor Quality").mark_circle(size=60).encode(
        x='Rating',
        y = alt.Y('Est_Monthly_Sales', scale=alt.Scale(domain=[0, 1600])),
        color=alt.condition(brush, 'Category:N', alt.ColorValue('whitesmoke'), legend=None),
        tooltip=['Product_Name','ASIN','Est_Monthly_Sales','Category','Reviews', 'LQS', 'Net','Price',]
    ).add_selection(
        brush).properties(
        height=height,
        width=width)

    ## line1 Est_Monthly_Sales >= 200
    line1 = alt.Chart(pd.DataFrame({'y': [200]})).mark_rule(color='red').encode(y='y')
    ## line2 Reviews <=50
    line2 = alt.Chart(pd.DataFrame({'x': [50]})).mark_rule(color='red').encode(x='x')
    ## line3 LQS <6
    line3 = alt.Chart(pd.DataFrame({'x': [6]})).mark_rule(color='red').encode(x='x')
    ## line4 Price>20
    line4 = alt.Chart(pd.DataFrame({'x': [20]})).mark_rule(color='red').encode(x='x')
    ## line5 Net>15
    line5 = alt.Chart(pd.DataFrame({'y': [15]})).mark_rule(color='red').encode(y='y')
    ## line6 Rating<3.7
    line6 = alt.Chart(pd.DataFrame({'x': [3.7]})).mark_rule(color='red').encode(x='x')
    
    plot_product_scatterchart =  chart1 + line1 + line2|chart2 + line1 + line3|chart3 + line5 +line4|chart4 + line1 + line6
    
    plot_product_scatterchart_json = plot_product_scatterchart.to_json()


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

    ################################
    # finalize data send to template
    ################################
    total_category_count = "23"
    total_product_count = df.shape[0]
    average_rank = "5"


    context = {"total_category_count": total_category_count,
               "total_product_count": total_product_count,
               "average_rank": average_rank,
               "plot_scatterchart_product": plot_product_scatterchart_json,
               "plot_bar_product": plot_product_bar_json,
               "plot_line_product": plot_product_line_json,
               "plot_bar_year_product": plot_product_bar_year_json,
               "plot_bar_yearqtrmonth_product": plot_product_bar_yearqtrmonth_json
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
