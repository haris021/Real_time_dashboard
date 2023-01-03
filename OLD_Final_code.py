
import json
import folium
from folium import features
import vincent
import shapefile
from json import dumps
import random
import pandas as pd
import geojson
import plotly.express as px
import pandas as pd
import numpy as np
from plotly import graph_objects as go
from plotly.subplots import make_subplots
import folium
import branca
from folium.plugins import BeautifyIcon


m1 = folium.Map(location=(32, 67), #location sets the longitude and latitude of the map
              zoom_start=4, tiles='Stamen Terrain')





#m1





# converting shapefile to json insert location of your shapefile here

reader = shapefile.Reader('UIB_30m_New.shp')
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature",     geometry=geom, properties=atr)) 


#writing the GEOJson file
geojson = open("pyshp-demo.json", "w") #this file is saved in the current working directory
geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
geojson.close()




json1='pyshp-demo.json'
style = {'fillColor': '#1F51FF'}    
polygon = folium.GeoJson(json1, style_function = lambda x: style).add_to(m1)
#m1


df = pd.read_csv('indus_at_tarbela.csv')


df['snapshot_month'] = pd.to_datetime(df['Date'])



df["Indus River at Tarbela (m3/s)"] = pd.to_numeric(df["Indus River at Tarbela (m3/s)"], downcast="float")




df=df.sort_values("snapshot_month")




fig=make_subplots(specs=[[{"secondary_y":True}]])



fig.add_trace(                           
    go.Scatter(
    x=df['snapshot_month'],
    y=df['Indus River at Tarbela (m3/s)'],
    
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
             yaxis_title='Indus River at Tarbela (m3/s)',
            )



fig.write_html('indus.html')
html_list=[]
html_list.append('indus.html')
df2=pd.DataFrame(html_list,columns =['html_file'])
#df2


icon_circle = BeautifyIcon(
    icon_shape='circle-dot', 
    border_color='#1F51FF', 
    border_width=6,
)

for i in range(0,len(html_list)):
    html="""
    <iframe src=\"""" + df2['html_file'][i] + """\" width="600" height="300"  frameborder="0">    
    """
    popup = folium.Popup(folium.Html(html, script=True))
    folium.Marker( location=[34.088961, 72.697154],tooltip='Tarbela', icon=icon_circle,
                  popup=popup,).add_to(m1)


m1.save('indus_plot.html')


# Kabul

# converting shapefile to json insert location of your shapefile here

reader = shapefile.Reader('krbshape.shp')
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature",     geometry=geom, properties=atr)) 


#writing the GEOJson file
geojson = open("kabul.json", "w") #this file is saved in the current working directory
geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
geojson.close()





json2='kabul.json'
style2 = {'fillColor': '#7f00ff'}    
polygon = folium.GeoJson(json2, style_function = lambda x: style2).add_to(m1)
m1


df2 = pd.read_csv('kabul_at_nowshera.csv')





df2['snapshot_month'] = pd.to_datetime(df2['Date'])





df2["Kabul at Nowshera (m3/s)"] = pd.to_numeric(df2["Kabul at Nowshera (m3/s)"], downcast="float")





df2=df2.sort_values("snapshot_month")



fig1=make_subplots(specs=[[{"secondary_y":True}]])


fig1.add_trace(                           
    go.Scatter(
    x=df2['snapshot_month'],
    y=df2['Kabul at Nowshera (m3/s)'],
    
    mode='lines',                  
    line = dict(color='firebrick', width=3)
     )
)


fig1.update_layout(hoverlabel_bgcolor='#DAEEED',  #Change the background color of the tooltip to light gray
             #title_text="Housing Market Trends: Atlanta, GA", #Add a chart title
             title_font_family="Times New Roman",
             title_font_size = 20,
             title_font_color="darkblue", #Specify font color of the title
             title_x=0.5, #Specify the title position
             xaxis_title='Date'     ,
             yaxis_title='Kabul at Nowshera (m3/s)',
            )


fig1.write_html('kabul.html')
html_list1=[]
html_list1.append('kabul.html')
df22=pd.DataFrame(html_list1,columns =['html_file'])
#df22


# m1 = folium.Map(location=[34.088961, 72.697154], zoom_start=15)

icon_circle = BeautifyIcon(
    icon_shape='circle-dot', 
    border_color='#7f00ff', 
    border_width=6,
)

for i in range(0,len(html_list)):
    html1="""
    <iframe src=\"""" + df22['html_file'][i] + """\" width="600" height="300"  frameborder="0">    
    """
    popup1 = folium.Popup(folium.Html(html1, script=True))
    folium.Marker( location=[34.0105, 71.9876],tooltip='Nowshera', icon=icon_circle,
                  popup=popup1,).add_to(m1)





m1.save('kabul_plot.html')

reader = shapefile.Reader('newmangla.shp')
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature",     geometry=geom, properties=atr)) 



#writing the GEOJson file
geojson = open("jhelum.json", "w") #this file is saved in the current working directory
geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
geojson.close()


json3='jhelum.json'
style3 = {'fillColor': 'yellow'}    
polygon = folium.GeoJson(json3, style_function = lambda x: style3).add_to(m1)
#m1



df = pd.read_csv('jhelum_at_mangla.csv')




df['snapshot_month'] = pd.to_datetime(df['Date'])





df["Jhelum at Mangla (m3/s)"] = pd.to_numeric(df["Jhelum at Mangla (m3/s)"], downcast="float")





df=df.sort_values("snapshot_month")




fig=make_subplots(specs=[[{"secondary_y":True}]])




fig.add_trace(                           
    go.Scatter(
    x=df['snapshot_month'],
    y=df['Jhelum at Mangla (m3/s)'],
    
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
             yaxis_title='Jhelum at Mangla (m3/s)',
            )



fig.write_html('mangla.html')
html_list4=[]
html_list4.append('mangla.html')
df4=pd.DataFrame(html_list4,columns =['html_file4'])
#df4

icon_circle = BeautifyIcon(
    icon_shape='circle-dot', 
    border_color='yellow', 
    border_width=6,
)

for i in range(0,len(html_list4)):
    html4="""
    <iframe src=\"""" + df4['html_file4'][i] + """\" width="600" height="300"  frameborder="0">    
    """
    popup4 = folium.Popup(folium.Html(html4, script=True))
    folium.Marker( location=[33.0947, 73.6418], tooltip='Mangla', icon=icon_circle,
                  popup=popup4,).add_to(m1)




m1.save('mangla_plot.html')



# converting shapefile to json insert location of your shapefile here

reader = shapefile.Reader('newchenab.shp')
fields = reader.fields[1:]
field_names = [field[0] for field in fields]
buffer = []
for sr in reader.shapeRecords():
    atr = dict(zip(field_names, sr.record))
    geom = sr.shape.__geo_interface__
    buffer.append(dict(type="Feature",     geometry=geom, properties=atr)) 


#writing the GEOJson file
geojson = open("chenab.json", "w") #this file is saved in the current working directory
geojson.write(dumps({"type": "FeatureCollection","features": buffer}, indent=2) + "\n")
geojson.close()


json6='chenab.json'
style6 = {'fillColor': 'red'}    
polygon = folium.GeoJson(json6, style_function = lambda x: style6).add_to(m1)
#m1



df = pd.read_csv('chenab_at_marala.csv')




df['snapshot_month'] = pd.to_datetime(df['Date'])



df["Chenab at Marala (m3/s)"] = pd.to_numeric(df["Chenab at Marala (m3/s)"], downcast="float")



df=df.sort_values("snapshot_month")




fig=make_subplots(specs=[[{"secondary_y":True}]])




fig.add_trace(                           
    go.Scatter(
    x=df['snapshot_month'],
    y=df['Chenab at Marala (m3/s)'],
    
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
             yaxis_title='Chenab at Marala (m3/s)',
            )



fig.write_html('chenab.html')
html_list6=[]
html_list6.append('chenab.html')
df26=pd.DataFrame(html_list6,columns =['html_file6'])
#df26


icon_circle = BeautifyIcon(
    icon_shape='circle-dot', 
    border_color='firebrick', 
    border_width=6,
)

for i in range(0,len(html_list)):
    html6="""
    <iframe src=\"""" + df26['html_file6'][i] + """\" width="600" height="300"  frameborder="0">    
    """
    popup6 = folium.Popup(folium.Html(html6, script=True))
    folium.Marker( location=[32.6724, 74.4644],tooltip='Marala', icon=icon_circle,
                  popup=popup6,).add_to(m1)



m1.save('chenab_plot.html')

