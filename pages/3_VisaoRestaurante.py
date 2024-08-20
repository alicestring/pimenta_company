from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

import pandas as pd
import numpy as np
import streamlit as st
from PIL import Image

import folium
from streamlit_folium import folium_static

st.set_page_config(page_title = 'Visão Restaurante', page_icon = '🍜', layout = 'wide')

df = pd.read_csv('./dataset/train.csv')

# LIMPEZA no dataframe para tirar os Nan ------------------------------------------------

def clean_code(df):
    
    df = df[(df['City'] != 'NaN ')]
    df = df[(df['Road_traffic_density'] != 'NaN ')]
    df = df[df['Road_traffic_density'] != 'NaN ']
    df = df[df['Road_traffic_density'] != 'NaN ']
    df = df[df['Festival'] != 'NaN ']
    df['Road_traffic_density'] = df['Road_traffic_density'].str.strip(' ')
    df['Festival'] = df['Festival'].str.strip(' ')
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
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( float )
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

st.header('Marketplace - Visão Restaurante')
st.markdown("""___""")

with st.container(): 

# ----------------------------------------------------------------------------------------------------------------------- 
    # FUNÇÕES

    def distancia_media_total(df):
        pontos = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude',
                  'Delivery_location_longitude']
    
        df['km_media'] = df.loc[:, pontos].apply(lambda x: haversine(
                                  (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                  (x['Delivery_location_latitude'], x['Delivery_location_longitude']))
                                   , axis = 1)
        distancia_media_total_ = df['km_media'].mean()                               
        distancia_media_total_ = np.round(distancia_media_total_ , 2)
        
        return distancia_media_total_

    
    def calculo_entrega_por_festival(df, operacao, festival):     

        df1 = (df.loc[:, ['Time_taken(min)', 'Festival']]
                                                        .groupby('Festival')
                                                        .agg({'Time_taken(min)': 
                                                              ['mean', 'std']})
             )        
        df1.columns = ['avg_time', 'std_time']
        df1 = df1.reset_index()  
        if operacao == 'media':
            calculo = df1.loc[(df1['Festival'] == festival), 'avg_time']
        elif operacao == 'desviopadrao':
            calculo = df1.loc[(df1['Festival'] == festival), 'std_time']
        else:
            calculo = 0
            
        calculo = np.round(calculo, 2)

        return calculo

    
    def distribuicao_media_distancia_por_cidade(df):
        cols = ['Restaurant_latitude', 'Restaurant_longitude',
            'Delivery_location_latitude', 'Delivery_location_longitude']

        df1 = df.copy()

        df1['distancia'] = df1.loc[:, cols].apply(lambda x :                                                    
                                                           haversine(
                                                            (x['Restaurant_latitude'],x['Restaurant_longitude']),
                                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude']))
                                                            , axis = 1)
        df1 = df1.loc[:, ['distancia', 'City']].groupby('City').mean().reset_index()

        fig = go.Figure(data = [
                                 go.Pie(labels = df1['City'], values = df1['distancia'], pull = [0, 0.1, 0])
        ])
        return fig


    def calculo_tempo_por(df, campos, campos_group, figura):        
        df1 = df.copy()
        df1 = df1.loc[:, campos].groupby(campos_group).agg({'Time_taken(min)': ['mean', 'std']})
        df1.columns = ['media', 'desvio']
        df1 = df1.reset_index()

        if figura == 'barra':
            fig = go.Figure()
            fig.add_trace(go.Bar(name = 'Control',
                                 x = df1[campos_group[0]],
                                 y = df1['media'],
                                 error_y = dict(type = 'data', array = df1['desvio'])
                                )
                         )
        elif figura == 'sunburst':
            fig = px.sunburst(
                                df1, path = campos_group, values = 'desvio',
                                color = 'desvio', color_continuous_scale = 'RdBu',
                                color_continuous_midpoint = np.average(df1['desvio'])
                             )        
            
        return fig

    
    def tempo_medio_std_por(df):
        df1 = df.copy()
        cols = ['Time_taken(min)', 'City', 'Type_of_order']
        df1 = df1.loc[:, cols].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)': ['mean', 'std']})
        return df1
        
# ---------------------------------------------------------------------------------------------------------------------

    st.title('Overall Metrics')

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        x = len(df.loc[:, 'Delivery_person_ID'].unique())
        st.markdown('Entregadores Únicos')
        col1.metric('Entregadores Únicos', x)
        st.markdown("""___""")        

    with col2:        
        st.markdown('Distância Média')
        col2.metric('Distancia Media', distancia_media_total(df))
        st.markdown("""___""")
        
    with col3:
        st.markdown('Tempo médio de entrega durante os festivais')
        col3.metric('Tempo médio', calculo_entrega_por_festival(df, 'media', 'Yes'))
        st.markdown("""___""")

    with col4:    
        st.markdown('Desvio Padrão de entrega durante os festivais')
        col4.metric('Tempo Entrega', calculo_entrega_por_festival(df, 'desviopadrao', 'Yes'))
        st.markdown("""___""")

        
    with col5:        
        st.markdown('Tempo médio de entrega durante os dias sem festivais')
        col5.metric('Tempo Medio', calculo_entrega_por_festival(df, 'media', 'No'))
        st.markdown("""___""")        
                     
    with col6:
        st.markdown('Desvio Padrão de entrega durante os dias sem festivais')
        col6.metric('Desvio Tempo', calculo_entrega_por_festival(df, 'desviopadrao', 'No'))    
        st.markdown("""___""")

with st.container():      
    st.title('Distribuição Média da Distância por Cidade')
    fig = distribuicao_media_distancia_por_cidade(df)
    st.plotly_chart(fig)   
    st.markdown("""___""")

with st.container():
    st.title('Distribuição do tempo')
    col1, col2 = st.columns(2, gap = 'large')

    with col1:
        st.markdown('O tempo médio de entrega por cidade')
        cols = ['Time_taken(min)', 'City']
        cols_group = ['City']
        fig = calculo_tempo_por(df, cols, cols_group, 'barra')
        fig.update_layout(barmode = 'group')
        st.plotly_chart(fig)

    with col2:
        st.markdown('O tempo médio de entrega por cidade e tipo de tráfego')
        cols = ['Time_taken(min)', 'City', 'Road_traffic_density']
        cols_group = ['City', 'Road_traffic_density']
        fig = calculo_tempo_por(df, cols, cols_group, 'sunburst')       
        st.plotly_chart(fig)    
        st.markdown("""___""")

with st.container():
    st.title('Tempo Médio e Desvio Padrão por Cidade e Tipo de Pedido')    
    st.dataframe(tempo_medio_std_por(df))  
    st.markdown("""___""")