#libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go
#bibliotecas necessarias
import pandas as pd
from PIL import Image
import streamlit as st
from streamlit_folium import folium_static
import folium
import numpy as np
st.set_page_config(page_title='Visão Restaurantes')

#--------------------------------------------------------------
#---------------------------Funções----------------------------
#--------------------------------------------------------------
def tempo_trafego_cidade(df1):
    df_aux = (df1.loc[:,['Time_taken(min)','City','Road_traffic_density'] ].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)':
              ['mean','std']}))
    df_aux.columns =  ['Delivery_mean','Delivery_std']
    df_aux = df_aux.reset_index()
    fig = (px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Delivery_mean', color='Delivery_std', 
            color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['Delivery_std'])))
    return fig
def tempo_pedido_cidade(df1):
    df_aux = df1.loc[:,['Time_taken(min)','City','Type_of_order'] ].groupby(['City','Type_of_order']).agg({'Time_taken(min)':['mean','std']})
    df_aux.columns =  ['Delivery_mean','Delivery_std']
    df_aux = df_aux.reset_index()
    return df_aux

def distancia_cidade(df1):
    """
    explicacao sobre a funcao
    """
    cols = ['Delivery_location_latitude', 'Delivery_location_longitude', 'Restaurant_latitude', 'Restaurant_longitude']
    df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                 (x['Delivery_location_latitude'],     x['Delivery_location_longitude']) ), axis=1)
    avg_distance= df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    fig = go.Figure( data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0,0.1,0])])
    return fig
     
def tempo_cidade(df1):
    """
    explicacao sobre a funcao
    """
    df_aux = df1.loc[:,['Time_taken(min)','City'] ].groupby('City').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns =  ['Delivery_mean','Delivery_std']
    df_aux = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name= 'Control', x=df_aux['City'], y=df_aux['Delivery_mean'], error_y=dict( type='data', array=df_aux['Delivery_std'])))
    fig.update_layout(barmode='group')
    return fig

def media_festival(df1, festival):
    """
    explicacao sobre a funcao
    """
    df_aux = df1.loc[:,['Time_taken(min)','Festival']].groupby('Festival').agg({'Time_taken(min)':['mean','std']})
    df_aux.columns =  ['Delivery_mean','Delivery_std']
    df_aux = df_aux.reset_index()
    if festival == 'Yes':
        media = np.round(df_aux.loc[2,'Delivery_mean'],2)
        desvio_padrao = np.round(df_aux.loc[2,'Delivery_std'], 2)
    elif festival == 'No':
        media = np.round(df_aux.loc[1,'Delivery_mean'],2)
        desvio_padrao = np.round(df_aux.loc[1,'Delivery_std'],2)
    return media, desvio_padrao
     
def distancia_media(df1):
    """
    explicacao sobre essa funcao
    """
    colunas = ['Restaurant_latitude', 'Restaurant_longitude','Delivery_location_latitude',
               'Delivery_location_longitude']
    df1['Distance'] = (df1.loc[:,colunas].apply(lambda x: haversine( 
        (x['Restaurant_latitude'], x['Restaurant_longitude']),   
        (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), 
        axis=1 ))            
    df_aux2 = np.round(df1.loc[:,'Distance'].mean(), 2)
    return df_aux2


def clean_code(df1):
    """ Esta função tem a responsabilidade de limpar o dataframe
    Tipo de limpeza:
    1. Remoção dos dados NaN
    2. Mudança do tipo da coluna de dados
    3. Formatação da coluna de datas
    4. Remoção dos espaços das variáveis de texto
    5. Limpeza da coluna de tempo (remoção do texto da variável numérica)

    Input: Dataframe
    Output: Dataframe
    """
    # Limapndo o dataset
    #1- Removi os NaN's da coluna delivery person age e converti para inteiro
    selecao = (df1['Delivery_person_Age'] != 'NaN ')
    df1=df1.loc[selecao, :]
    selecao = (df1['Road_traffic_density'] != 'NaN ')
    df1=df1.loc[selecao, :]
    selecao = (df1['City'] != 'NaN ')
    df1=df1.loc[selecao, :]
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    #2- Converti a coluna ratings para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    #3- Converti a coluna order date para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format = '%d-%m-%Y')
    #2- Removi os NaN's da colina multiple deliveries e converti para inteiro
    df1 = df1.loc[(df1['multiple_deliveries'] != 'NaN '),:].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    #Como tirei linhas, ele remove o index também, então resetei os valores do index
    df1 = df1.reset_index(drop=True)
    
    #4- Limpar os espaços em branco do dataset
    
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Delivery_person_ID'] = df1.loc[:, 'Delivery_person_ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    
    #5- Limpando a coluna time taken(deixando só os números e transformando em inteiro 
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1
    
# --------------- Inicio da estrutura lógica do código ---------------
#---------------------------------------------------------------------
    
# import dataset
df = pd.read_csv('train_ftc.csv')
# Limpando o código
df1 = clean_code(df)

##### --------------------------------------------------#####
##### Barra Lateral
##### --------------------------------------------------#####

st.header( 'Overal Metrics')
col1, col2 = st.sidebar.columns(2)
with col1:
    image = Image.open('image.png')
    st.image(image, width=120)
with col2:
    st.markdown('# Cury Company')
    
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

date_slider = st.sidebar.slider('Até qual dia?', value=pd.to_datetime('2022-4-13').date(), min_value=pd.to_datetime('2022-2-11').date(), max_value=pd.to_datetime('2022-4-6').date(), format='DD-MM-YYYY')
#convertendo a variavel para o formato 'datetime64' (que é o formato de data do nosso dataset)
data = pd.to_datetime(date_slider, format='datetime64')
st.sidebar.markdown("""---""")
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito?', ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")
weather_options = st.sidebar.multiselect('Quais as condições de clima?', ['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'], default=['conditions Sunny', 'conditions Stormy', 'conditions Sandstorms','conditions Cloudy', 'conditions Fog', 'conditions Windy'])

st.sidebar.markdown( """---""" )
st.sidebar.markdown( '### Powered by Comunidade DS' )

# Para aplicar o filtro de data no dashboard
linhas_selecionadas = df1['Order_Date'] < data
df1 = df1.loc[linhas_selecionadas, :]

# Para aplicar o filtro de transio no dashboard
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

# Para aplicar o filtro de cond climatica no dashboard
linhas_selecionadas = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selecionadas, :]

# =======================================
# Layout no Streamlit
# =======================================

#Criando as 3 abas
tab1, tab2, tab3 = st.tabs(['Visão Gerencial','-', '-'])

with tab1:
    with st.container():
        col1, col2, col3 = st.columns(3)
        with col1:
            df_aux = df1.loc[:,'Delivery_person_ID'].unique().shape[0]
            df_aux2 = distancia_media(df1)

            st.markdown('######  - ')
            col1.metric('Entregadores únicos', df_aux)
            col1.metric('Distância média', f'{df_aux2} Km',)
            
        with col2:
            media, desvio_padrao = media_festival(df1, festival='Yes')
            st.markdown('###### Com festival')
            col2.metric('Tempo médio entrega', f'{media} min')
            col2.metric('Desvio padrão', desvio_padrao)
            
        with col3:
            media, desvio_padrao = media_festival(df1, festival='No')
            st.markdown('###### Sem festival')
            col3.metric('Tempo médio entrega', f'{media} min')
            col3.metric('Desvio padrão', desvio_padrao)
            
    with st.container():
        st.markdown('###### Tempo médio e desvio padrão de entrega por cidade')
        fig = tempo_cidade(df1)
        st.plotly_chart(fig, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Distância média dos locais de entrega por cidade')
            fig = distancia_cidade(df1)
            st.plotly_chart(fig, use_container_width=True)
            
        with col2:
            st.markdown('###### Tempo médio por tipo de pedido e cidade')
            df_aux = tempo_pedido_cidade(df1)
            st.dataframe(df_aux)
            
    with st.container():
        st.markdown('###### Tempo médio por cidade e tipo de tráfego')
        fig = tempo_trafego_cidade(df1)
        st.plotly_chart(fig, use_container_width=True)
