from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
from datetime import datetime as dt
import streamlit as st
from PIL import Image

import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Empresa', page_icon = '😀', layout = 'wide')

# -------------------------------------------------------------------------------------

df = pd.read_csv('./dataset/train.csv')

# -------------------------------------------------------------------------------------

# FUNÇÕES

def cleancode(df):
# limpeza no dataframe para tirar os Nan
    df = df[(df['City'] != 'NaN ')]
    df = df[(df['Road_traffic_density'] != 'NaN ')]
    df = df[df['Road_traffic_density'] != 'NaN ']
    df = df[df['Road_traffic_density'] != 'NaN ']
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip(' ')
    return df

def conversao(df):
# conversão
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    return df

def orderByDay(df):
#1. Quantidade de pedidos por dia        
    df1 = df.copy()        
    df1 = df1.loc[:, ['ID','Order_Date']].groupby('Order_Date').count().reset_index()        
    fig = px.bar(df1, x = 'Order_Date', y = 'ID')
    return fig

def orderByTraffic(df):
#2. Distribuição dos pedidos por tipo de tráfego.
    df1 = df.copy()
    df1 = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df1['ID_perc'] = (df1['ID'] * 100) / (df1['ID'].sum())
    fig = px.pie(df1, values = 'ID_perc', names = 'Road_traffic_density')
    return fig    

def volumeByCityByTraffic(df):
#3. Comparação de volume de pedidos por cidade e tráfego  
    df1 = df.copy()
    df1 = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    #fig = px.bar(df1, x = 'City', y = 'ID', color = 'Road_traffic_density', barmode = 'group')                  
    fig = px.scatter(df1, x = 'City', y = 'Road_traffic_density', size = 'ID', color = 'City')
    return fig    

def orderByWeek(df):
#4. Quantidade de Pedido por Semana     
    df1 = df.copy()    
    df1['Week_of_Year'] = df1['Order_Date'].dt.strftime("%U")
    df1 = df1.loc[:, ['ID','Week_of_Year']].groupby('Week_of_Year').count().reset_index()      
    fig = px.line(df1, x = 'Week_of_Year', y = 'ID')
    return fig

def orderByDeliverByWeek(df):
# 5. Quantidade de pedidos por entregador por Semana
# Quantas entregas na semana / Quantos entregadores únicos por semana                
    df1 = df.copy()
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')
    df1['DayWeek'] = df1['Order_Date'].dt.strftime('%U')
    
    cols_entregas = ['DayWeek','ID']
    entregas_groupby = ['DayWeek']
    cols_entregadores = ['DayWeek', 'Delivery_person_ID']
    entregadores_groupby = ['Delivery_person_ID','DayWeek']          
    
    df2 = df1.loc[:, cols_entregas].groupby('DayWeek').count().reset_index()
    df3 = df1.loc[:, cols_entregadores].groupby('DayWeek').nunique().reset_index()
    
    df4 = pd.merge(df2, df3, how = 'inner')
    
    df4['pedidospor'] = df4['ID'] / df4['Delivery_person_ID']
    fig = px.line(df4, x='DayWeek', y='pedidospor')        
    return fig    

def cityLocalByTraffic(df):
# 6. A localização central de cada cidade por tipo de tráfego.    
    df3 = df.copy()

    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Road_traffic_density', 'City']
    cols_groupby = ['City', 'Road_traffic_density']

    df3 = df3.loc[:, cols].groupby(cols_groupby).median().reset_index()

    # Desenhar o mapa
    map_ =  folium.Map()  #(zoom_start = 11)

    for index, location in df3.iterrows():
        folium.Marker([location['Delivery_location_latitude'],
                      location['Delivery_location_longitude']],
                      popup = location[['City', 'Road_traffic_density']]).add_to(map_)
                        
    folium_static(map_, width = 1024, height = 600)
    return 0    
    
# -------------------------------------------------------------------------------------

st.header('Marketplace - Visão Cliente')
image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)
st.sidebar.markdown('Pimenta Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")
st.sidebar.markdown('## Selecione uma data limite')

df =  cleancode(df)
df =  conversao(df)

# -------------------------------------------------------------------------------------

# filtros

slide_min = df['Order_Date'].min().date()
slide_max = df['Order_Date'].max().date()
data_slider = st.sidebar.slider('Até qual valor?',                           
                                 min_value = slide_min,
                                 max_value = slide_max,                        
                                 value = slide_max,                                     
                                 format = 'DD-MM-YYYY')

st.header(data_slider)
st.sidebar.markdown("""___""")

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")

data_slider = pd.to_datetime(data_slider)
linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

st.dataframe(df)

# --------------------------------------------------------------------------------------------------------------------------------------

# main

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    
    with st.container():
        
        st.markdown('# Order by Day') 
        fig = orderByDay(df)
        st.plotly_chart(fig, use_container_width = True)
        
        
    with st.container():
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('# Order by Road Traffic Density')
            fig = orderByTraffic(df)
            st.plotly_chart(fig, use_container_width = True)

        with col2:
            st.markdown('# Compare Volume Delivery by City and by Road Traffic')
            fig = volumeByCityByTraffic(df)        
            st.plotly_chart(fig, use_container_width = True)   

# -----------------------------------------------------------------------------------------------------------------------------------------

with tab2:
    
    with st.container():    
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.header('Order by Week')
            fig = orderByWeek(df)
            st.plotly_chart(fig, use_container_width = True) 
            
            st.markdown('# Order by Deliver and Week')                 
            fig = orderByDeliverByWeek(df)
            st.plotly_chart(fig, use_container_width = True)

# -----------------------------------------------------------------------------------------------------------------------------------------
            
with tab3:
    st.header('# City Local by Road Traffic Density')
    cityLocalByTraffic(df)
