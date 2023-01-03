from bs4 import BeautifulSoup
import requests
import pandas as pd
import openpyxl
from openpyxl import Workbook
import folium
from folium import features
import shapefile
from json import dumps
import pandas as pd
import geojson
import plotly.express as px
import pandas as pd
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import folium
from folium.plugins import BeautifyIcon
import streamlit as st 
from streamlit_folium import st_folium, folium_static
import altair as alt 
import json

month_to_number = {"Jan": 1, "Feb":2 , "Mar":3 , "Apr":4, "May": 5, "Jun":6, "Jul":7, "Aug":8, "Sep":9, "Oct":10, "Nov":11, "Dec":12}

# directory = 'C:/Users/User-PC/Desktop/Haris/Haris 28'


plotting_data = {
    "Indus": {
        "location": "Tarbela", 
        "coords": [34.088961, 72.697154], 
        "shapefile": 'UIB/UIB_30m_New.shp', 
        "fillColor" : '#1F51FF', 
        "border_color" : '#1F51FF'
        }, 
    "Kabul":{
        "location": "Nowshera", 
        "coords": [34.0105, 71.9876], 
        "shapefile": 'Kabul/krbshape.shp', 
        "fillColor": '#7f00ff', 
        "border_color" : '#7f00ff'
        }, 
    "Jhelum": {
        "location": "Mangla", 
        "coords": [33.0947, 73.6418], 
        "shapefile": 'mangla/newmangla.shp', 
        "fillColor": 'yellow', 
        "border_color" : 'yellow'
        },
    "Chenab":{
        "location": "Marala", 
        "coords":[32.6724, 74.4644], 
        "shapefile": 'chenab/newchenab.shp', 
        "fillColor": 'red', 
        "border_color" : 'firebrick'
        }, 

}
def generate_json():
    for river in plotting_data.keys():
        shpfile = plotting_data[river]["shapefile"]
        reader = shapefile.Reader(shpfile)
        fields = reader.fields[1:]
        field_names = [field[0] for field in fields]
        buffer = []
        for sr in reader.shapeRecords():
            atr = dict(zip(field_names, sr.record))
            geom = sr.shape.__geo_interface__
            buffer.append(dict(type="Feature",     geometry=geom, properties=atr)) 

        json_name = "{}.json".format(river)
        #writing the GEOJson file
        geojson = open(json_name.format(river), "w") #this file is saved in the current working directory
        geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
        geojson.close()


def get_html_table(url):
	html_content = requests.get(url).text
	soup = BeautifulSoup(html_content, "html.parser")
	table = soup.find_all("table", class_="table table-bordered table-hover cc_cursor")
	return table
    
def table_to_df(table_data, headings):
	data = []
	for row in table_data:
		row_data = row.find_all('td')
		sub_data =[]
		for cell in row_data:
			entry = cell.text
			sub_data.append(entry)
		data.append(sub_data)

	df = pd.DataFrame(data, columns=headings)
	
	return df

def get_river_flow_data():
	url="http://www.wapda.gov.pk/index.php/river-flow-data"
	table = get_html_table(url)
	
	table_data = table[0].find_all('tr')
	table_data = table_data[4:]
	Headings = ['Date', 'Indus_levels','Indus at Tarbela (m3/s)','Indus_Outflow','Kabul at Nowshera (m3/s)',
	'Jhelum_levels','Jhelum at Mangla (m3/s)','Jhelum_Outflow', 'Chenab at Marala (m3/s)','System_Inflow_now',
	'System_Inflow_past','System_Inflow_avg']
	df = table_to_df(table_data,headings = Headings)
	df.drop(['Indus_levels', 'Indus_Outflow', 'Jhelum_levels', 'Jhelum_Outflow', 'System_Inflow_now', 'System_Inflow_past', 'System_Inflow_avg'], axis = 1, inplace = True)
	return df, table[0]

# Retrieving, organizing, and cleaning the data fetched
def retrieve_data():

    master_df, table = get_river_flow_data()
    row = list(table.find_all('tr')[1])
    row.remove('\n')
    period= row[0]
    period = period.text
    starting_period, ending_period = period[::-1][0:7][::-1].split('-')[0],"20" + period[::-1][0:7][::-1].split('-')[1]
    timeperiod = (starting_period, ending_period)

    master_df['Date'] = master_df['Date'].apply(lambda date: date.replace('-', ' ')).apply(lambda date: date.replace('/', ' ')).apply(lambda date: date[:len(date)-1])
    master_df = master_df[::-1].reset_index(drop = True, inplace = False)
    master_df[['Day','Month']] = master_df['Date'].str.split(' ',expand=True)
    master_df['Month'] = master_df['Month'].apply(lambda month: 'Nov' if (month == 'No') else ("Aug" if month == 'Au' else month))
    years_list = []
    curr = starting_period 
    months = master_df['Month']
    # print(list(set(months)))
    prev = "init"
    for month in months: 
        if prev == "Dec" and month == "Jan": 
            curr = ending_period 
        years_list.append(curr)
        prev = month

    master_df["Year"] = years_list




    master_df["Month"] = master_df["Month"].apply(lambda month: month_to_number[month])
    master_df["Date"] = pd.to_datetime(master_df[["Year", "Month", "Day"]])
    master_df = master_df[['Date', 'Indus at Tarbela (m3/s)','Kabul at Nowshera (m3/s)','Jhelum at Mangla (m3/s)','Chenab at Marala (m3/s)']]

    for data_col in list(master_df.columns)[1:]:
        master_df[data_col] = master_df[data_col].apply(lambda data: data.strip())
    
    return master_df, timeperiod

def regenerate_plots(master_df):
    
    for river in plotting_data.keys(): 

        col_name = "{} at {} (m3/s)".format(river, plotting_data[river]["location"])
        shpfile = plotting_data[river]["shapefile"]

        df = master_df[["Date", col_name]]
        df[col_name] = pd.to_numeric(df[col_name], downcast="float")
        fig=make_subplots(specs=[[{"secondary_y":True}]])
        fig.add_trace(                           
            go.Scatter(
            x=df['Date'],
            y=df[col_name],
            mode='lines',                  
            line = dict(color='firebrick', width=3)
            )
        )
        fig.update_layout(hoverlabel_bgcolor='#DAEEED',  #Change the background color of the tooltip to light gray
                    #title_text="Housing Market Trends: Atlanta, GA", #Add a chart title
                    title_font_family="Times New Roman",
                    title_font_size = 20,
                    title_font_color="darkblue", #Specify font color of the title
                    title_x=0.5, #Specify the title position
                    xaxis_title='Date'     ,
                    yaxis_title=col_name,
                    )
        plot_name = "Timeseries Plots/{}.html".format(river)
        fig.write_html(plot_name)

def generate_map(master_df):
    
    # regenerate_plots(master_df)
    m1 = folium.Map(location=(33, 67), zoom_start=4, tiles='Stamen Terrain')

    for river in plotting_data.keys(): 

        icon_circle = BeautifyIcon(
            icon_shape='circle-dot', 
            border_color=plotting_data[river]["border_color"], 
            border_width=6,
        )


        col_name = "{} at {} (m3/s)".format(river, plotting_data[river]["location"])
        df = master_df[["Date", col_name]]
        df[col_name] = pd.to_numeric(df[col_name], downcast="float")
        chart = alt.Chart(df).mark_line().encode(x='Date', y=col_name).properties(width=540,height=250)
        chart_2 = json.loads(chart.to_json())

        popup = folium.Popup(min_width = 600, max_width=600)
        folium.features.VegaLite(chart_2, height=250, width=600).add_to(popup)
        folium.Marker(location=plotting_data[river]["coords"],tooltip=plotting_data[river]["location"], icon=icon_circle,
                    popup=popup).add_to(m1)




        # html="""<iframe src=\"""" + "Timeseries plots/{}.html".format(river) + """\" width="600" height="300"  frameborder="0">    """
        # popup = folium.Popup(folium.Html(html, script=True))
        # folium.Marker( location=plotting_data[river]["coords"],tooltip=plotting_data[river]["location"], icon=icon_circle,
        #           popup=popup,).add_to(m1)

        # html=open("Timeseries plots/{}.html".format(river), "r", encoding = 'utf-8').read() 
        # # print(html)
        # iframe = folium.IFrame(html).render()
        # # iframe = folium.branca.element.IFrame(html)
        # popup = folium.Popup(iframe, parse_html=False)
        # popup = folium.Popup(folium.Html('aa<br>'+folium.IFrame(html, width='410px', height='410px').render(), script=True), max_width=2650)
        # folium.Marker( location=plotting_data[river]["coords"],tooltip=plotting_data[river]["location"], icon=icon_circle,
        #           popup=popup,).add_to(m1)


        

        json_name = "{}.json".format(river)
        style = {'fillColor': plotting_data[river]["fillColor"]}    
        print(plotting_data[river]["fillColor"])
        polygon = folium.GeoJson(json_name, style_function = lambda x: style).add_to(m1)
       


    # master_df.to_csv("River inflows data.csv")
    m1.save("Final_map.html")

pd.options.mode.chained_assignment = None  # default='warn'
master_df, timeperiod = retrieve_data()
generate_map(master_df)

st.header("River Inflows Data") 
st.subheader("{} - {}".format(timeperiod[0], timeperiod[1])) 

html = open("Final_map.html", 'r', encoding ='utf-8').read()
st.components.v1.html(html, height = 600, width = 1000)

st.download_button(
   "Download Data",
   master_df.to_csv(index=False).encode('utf-8'),
   "File Name.csv",
   "text/csv",
   key='download-csv'
)

