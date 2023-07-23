from selenium import webdriver 
from webdriver_manager.chrome import ChromeDriverManager 
from selenium.webdriver.common.by import By 
import folium 
from folium.plugins import BeautifyIcon
import pandas as pd 
import streamlit as st 
import altair as alt
import json


def reconstruct_map():

    # Scrapping the data

    driver = webdriver.Chrome(ChromeDriverManager().install())
    driver.get("https://wapda.gov.pk/river-flow")
    driver.implicitly_wait(15)


    table_html = driver.find_element(By.TAG_NAME, "table").get_attribute("innerHTML")

    table_html_modified = f'<table> {table_html} </table>'

    df_retrieved = pd.read_html(table_html_modified)[0]

    driver.close()

    # Process downloaded data

    # Processing the data downloaded from Wapda

    df = df_retrieved.copy()
    df["Date"] = df["Date"] + " 2023"
    df["Date"] = pd.to_datetime(df["Date"])


    # Keeping only the required columns 

    df = df[["Date","Inflow", "Kabul Inflow at Nowshera", "Chenab Inflow at Marala", "Inflow.1"]]

    df = df.rename(mapper = {"Inflow": "Indus at Tarbela",
                            "Kabul Inflow at Nowshera" : "Kabul at Nowshera",
                            "Chenab Inflow at Marala" : "Chenab at Marala",
                            "Inflow.1": "Jhelum at Mangla"},
                            axis = 1)

    df = df.sort_values(by = "Date").reset_index(drop = True)



    def cusec_to_m3sec(cusec):
        conversion_factor = 0.0283168466 * 1000
        m3sec = cusec * conversion_factor 
        return m3sec

    for column in list(df.columns)[1:]: 
        df[str(column)] = df[str(column)].apply(lambda value: cusec_to_m3sec(value))

    wapda_data = df.copy() 
    del(df)

    # Processing the historical data

    historical_file_paths = {"Chenab at Marala": "Historical/chenab_at_marala.csv",
                            "Jhelum at Mangla": "Historical/jhelum_at_mangla.csv", 
                            "Kabul at Nowshera": "Historical/kabul_at_nowshera.csv", 
                            "Indus at Tarbela": "Historical/indus_at_tarbela.csv"}

    plotting_dfs = dict() 


    for column in list(wapda_data.columns)[1:]: 
        # Reading the historical data
        historical_data = pd.read_csv(historical_file_paths[column])
        historical_data.reset_index() 
        historical_data["Date"] = pd.to_datetime(historical_data["Date"])
        historical_data = historical_data.set_index("Date")
        # Processing the data to obtain historical trends
        df_percentiles = historical_data.groupby([historical_data.index.month, historical_data.index.day]).quantile([0.05, 0.1, 0.25, 0.75, 0.9, 0.95])
        df_percentiles.index = df_percentiles.index.set_names(['month', 'day', 'quantile'])
        df_percentiles = pd.pivot(df_percentiles.reset_index(), index = ['day', 'month'], columns = 'quantile', values = list(df_percentiles.columns)[0]).reset_index().sort_values(by = [ 'month', 'day']).reset_index(drop = True)
        df_percentiles.set_index(["day", "month"])

        df_min = historical_data.groupby([historical_data.index.month, historical_data.index.day]).min()
        df_min.index.set_names(['month', 'day'], inplace=True)
        df_min = df_min.rename(mapper = {list(historical_data.columns)[0]:'min'}, axis = 1)
        df_min = df_min.reset_index().set_index(['day', 'month'])

        df_max = historical_data.groupby([historical_data.index.month, historical_data.index.day]).max()
        df_max.index.set_names(['month', 'day'], inplace=True)
        df_max = df_max.rename(mapper = {list(historical_data.columns)[0]: 'max'}, axis = 1)
        df_max = df_max.reset_index().set_index(['day', 'month'])

        final_trends = df_min.reset_index().merge(df_max.reset_index(), on = ["day", "month"]).merge(df_percentiles.reset_index(), on = ["day", "month"]).set_index(['day', 'month'])[['min', 0.05, 0.1, 0.25, 0.75, 0.9, 0.95, 'max']]




        river_df = wapda_data[["Date", column]] 
        river_df["day"] = river_df["Date"].dt.day 
        river_df["month"] = river_df["Date"].dt.month

        river_plotting_df = pd.merge(river_df, final_trends, on = ["day", "month"], how = "left").drop(["day", "month"], axis = 1) 

        river_plotting_df = river_plotting_df.set_index("Date")

        river_plotting_df.columns = [column,'min', '5p', '10p', '25p', '75p','90p', '95p', 'max']

        plotting_dfs[column] = river_plotting_df
        
    map_data = {
    "Indus at Tarbela": {
        "location": "Tarbela", 
        "coords": [34.088961, 72.697154], 
        "shapefile": 'UIB/UIB_30m_New.shp', 
        "fillColor" : '#1F51FF', 
        "border_color" : '#1F51FF', 
        "json": "Indus.json"
        }, 
    "Kabul at Nowshera":{
        "location": "Nowshera", 
        "coords": [34.0105, 71.9876], 
        "shapefile": 'Kabul/krbshape.shp', 
        "fillColor": '#7f00ff', 
        "border_color" : '#7f00ff',
        "json":"Kabul.json"
        }, 
    "Jhelum at Mangla": {
        "location": "Mangla", 
        "coords": [33.0947, 73.6418], 
        "shapefile": 'mangla/newmangla.shp', 
        "fillColor": 'yellow', 
        "border_color" : 'yellow', 
        "json":"Jhelum.json"
        },
    "Chenab at Marala":{
        "location": "Marala", 
        "coords":[32.6724, 74.4644], 
        "shapefile": 'chenab/Chenab_30m_New.shp', 
        "fillColor": 'red', 
        "border_color" : 'firebrick',
        "json":"Chenab.json"
        }, 
}

    map = folium.Map(location=(33, 73), zoom_start=7, tiles='Stamen Terrain')

    for river in map_data.keys():


        # Overlaying the polygon

        style = {'fillColor': map_data[river]["fillColor"]}    
        polygon = folium.GeoJson(map_data[river]["json"], style_function = lambda x: style).add_to(map)

        # Preparing the plot
        df = plotting_dfs[river].reset_index()


        ch1 = alt.Chart(df).mark_area(opacity=0.5, color = "#b44200").encode(
            alt.X("Date:T"),
            alt.Y("min:Q"),
            alt.Y2("10p:Q"),
        ).properties(width=600, height=300)

        ch2 = alt.Chart(df).mark_area(opacity=0.5, color = "#f0e04d").encode(
            alt.X("Date:T"),
            alt.Y("10p:Q"),
            alt.Y2("25p:Q"),
        ).properties(width=600, height=300)

        ch3 = alt.Chart(df).mark_area(opacity=0.5, color = "#28fa76").encode(
            alt.X("Date:T"),
            alt.Y("25p:Q"),
            alt.Y2("75p:Q"),
        ).properties(width=600, height=300)

        ch4 = alt.Chart(df).mark_area(opacity=0.5, color = "#29f2fa").encode(
            alt.X("Date:T"),
            alt.Y("75p:Q"),
            alt.Y2("90p:Q"),
        ).properties(width=600, height=300)

        ch5 = alt.Chart(df).mark_area(opacity=0.5, color = "#293efa").encode(
            alt.X("Date:T"),
            alt.Y("90p:Q"),
            alt.Y2("max:Q"),
        ).properties(width=600, height=300)

        line_char = alt.Chart(df).mark_line(opacity=1, color = "Black").encode(
            alt.X("Date:T"),
            alt.Y(river),
        ).properties(width=600, height=300)

        final_chart = (ch1 + ch2 + ch3 + ch4 +ch5 + line_char).encode(
            x=alt.X(title = "Date"),
            y=alt.Y(title = "Inflow (meter cube per second)"),
        ).properties(title = river)

        chart_json = json.loads(final_chart.to_json())


        # Preparing the popup
        popup = folium.Popup(min_width = 700, max_width=600)
        folium.features.VegaLite(chart_json, height=250, width=600).add_to(popup)

        
        icon_circle = BeautifyIcon(
            icon_shape='circle-dot', 
            border_color=map_data[river]["border_color"], 
            border_width=6,
        )
        

        folium.Marker(location=map_data[river]["coords"],tooltip=map_data[river]["location"], icon=icon_circle,popup=popup).add_to(map)




    map.save("Final_map.html")

    return wapda_data

processed_data = reconstruct_map()

pd.options.mode.chained_assignment = None  # default='warn'

st.header("Real Time River Inflows Dashboard") 
# st.subheader("{} - {}".format(processed_data["Date"].head(0), processed_data["Date"].tail(1))) 

html = open("Final_map.html", 'r', encoding ='utf-8').read()
st.components.v1.html(html, height = 600, width = 1000)

st.download_button(
   "Download Data",
   processed_data.to_csv(index=False).encode('utf-8'),
   "River Inflow Data.csv",
   "text/csv",
   key='download-csv'
)
