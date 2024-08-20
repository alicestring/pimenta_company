from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Entregador', page_icon = '🚚', layout = 'wide')

df = pd.read_csv('dataset/train.csv')

# LIMPEZA no dataframe para tirar os Nan ------------------------------------------------

def clean_code(df):
    
    df = df[(df['City'] != 'NaN ')]
    df = df[(df['Road_traffic_density'] != 'NaN ')]
    df = df[df['Road_traffic_density'] != 'NaN ']
    df = df[df['Road_traffic_density'] != 'NaN ']
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip(' ')
    df.loc[:, 'Delivery_person_ID'] = df.loc[:, 'Delivery_person_ID'].str.strip()
    df = df.loc[df['Delivery_person_Age'] != 'NaN ', :]
    df['Time_taken(min)'] = df['Time_taken(min)'].replace(np.nan, '')
    df = df[df['Time_taken(min)'] != '']
    return df


# CONVERSÃO -----------------------------------------------------------------------------

def conversao(df):

    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format = '%d-%m-%Y')
    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( 'Int64' )
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float)
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.strip( '(min) '))
    return df

# CABEÇALHO BARRA LATERAL --------------------------------------------------------------------------------

df = clean_code(df)
df = conversao(df)

image_path = 'logo.png'
image = Image.open(image_path)
st.sidebar.image(image, width = 120)

st.sidebar.markdown('Pimenta Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""___""")

# FILTROS --------------------------------------------------------------------------------

data_slider = st.sidebar.slider('Até qual data?',
                               value = pd.datetime(2022, 4, 13),
                               min_value = pd.datetime(2022, 2, 11),
                               max_value = pd.datetime(2022, 4, 6),
                               format = 'DD-MM-YYYY')

traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito ?',
    ['Low', 'Medium', 'High', 'Jam'],
    default = ['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""___""")

linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas, :]

linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

# MAIN ------------------------------------------------------------------------------------

st.header('Marketplace - Visão Entregador')
st.markdown("""___""")

with st.container():

    col1, col2, col3, col4 = st.columns(4, gap = 'large')
    
    
    with col1:          
        col1.metric('Maior Idade', df['Delivery_person_Age'].max())
        
    with col2:            
        col2.metric('Menor Idade', df['Delivery_person_Age'].min())            

    with col3:
        col3.metric('Melhor Veículo', df['Vehicle_condition'].max())
        
    with col4:
        col4.metric('Pior Veículo', df['Vehicle_condition'].min())    
        
st.markdown("""___""")

with st.container():

    def calcula_media(df, coluna_media, coluna_agrupamento):
        df1 = df.loc[:, [coluna_media, coluna_agrupamento]].groupby(coluna_agrupamento).mean().reset_index()
        return df1

    col1, col2 = st.columns(2, gap = 'large')      

    with col1:
        st.markdown('Média das Avaliações Por Entregador')         
        st.dataframe(calcula_media(df, 'Delivery_person_Ratings', 'Delivery_person_ID'))
                    
    with col2:            
        with st.container():
            st.markdown('Média das Avaliações Por Trânsito')            
            st.dataframe(calcula_media(df, 'Delivery_person_Ratings', 'Road_traffic_density'))  
            
        with st.container():
            st.markdown('Média das Avaliações Por Condições Climáticas')            
            st.dataframe(calcula_media(df, 'Delivery_person_Ratings', 'Weatherconditions'))        
    
    st.markdown("""___""")

with st.container():

    def top_entregadores(df, ordem_crescente_True_False):
        df1 = df.loc[:, ['Delivery_person_ID', 'Time_taken(min)']].sort_values('Time_taken(min)', ascending = ordem_crescente_True_False).head(1)
        return df1

    col1, col2 = st.columns(2, gap = 'large')
    
    with col1:                        
        st.markdown('Top Entregadores Mais Rápidos')        
        st.dataframe(top_entregadores(df, True))
        
    with col2:
        st.markdown('Top Entregadores Mais Lentos')
        st.dataframe(top_entregadores(df, False))
        
    st.markdown("""___""")
