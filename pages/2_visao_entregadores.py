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

st.set_page_config(page_title='Visão Entregadores')

#--------------------------------------------------------------
#---------------------------Funções----------------------------
#--------------------------------------------------------------

def top_entregadores(df1, ascending):
    """
    Explicar sobre a função
    """
    df_aux = (df1.loc[:,['Delivery_person_ID','City','Time_taken(min)' ] ].groupby
              (['City','Delivery_person_ID']).mean().sort_values(['City','Time_taken(min)'], ascending=ascending).reset_index())
    dfmetro = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    dfurban = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)
    dfsemi = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df3 = pd.concat([dfmetro, dfurban, dfsemi]).reset_index(drop=True)
    return df3

def avaliacoes_clima(df1):
    """
    Explicar sobre a função
    """
    df_aux = df1.loc[:,['Weatherconditions','Delivery_person_Ratings'] ].groupby('Weatherconditions').agg(
        {'Delivery_person_Ratings':['mean','std']})
    df_aux.columns =  ['Delivery_mean','Delivery_std']
    df_aux = df_aux.reset_index()
    return df_aux
    
def avaliacoes_transito(df1):
    """
    Explicar sobre a função
    """
    df_aux = df1.loc[:,['Road_traffic_density','Delivery_person_Ratings'] ].groupby('Road_traffic_density').agg(
        {'Delivery_person_Ratings':['mean','std']})
    df_aux.columns =  ['Delivery_mean','Delivery_std']
    df_aux = df_aux.reset_index()
    return df_aux

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

st.header( 'Marketplace - Visão Entregadores')
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
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            menor = df1.loc[:,'Delivery_person_Age'].min()
            col1.metric( 'Entregador mais jovem', menor )           
        with col2:
            maior = df1.loc[:,'Delivery_person_Age'].max()
            col2.metric('Entregador mais velho', maior)
        with col3:
            menor = df1.loc[:,'Vehicle_condition'].min()
            col3.metric('Melhor condição de veículo', menor)
        with col4:
            maior = df1.loc[:,'Vehicle_condition'].max()
            col4.metric('Pior condição de veículo', maior)
            
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### Avaliações média por entregador')
            tabela = (df1.loc[:,[ 'Delivery_person_ID','Delivery_person_Ratings']].groupby(
                'Delivery_person_ID').mean().reset_index())
            st.dataframe(tabela)
            
        with col2:
            st.markdown('###### Avaliações média por trânsito')
            df_aux = avaliacoes_transito(df1)
            st.dataframe(df_aux)
            
            st.markdown('###### Avaliações média por condição climática')
            df_aux = avaliacoes_clima(df1)
            st.dataframe(df_aux)
            
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('###### 10 Entregadores mais rápidos')
            df3 = top_entregadores(df1, ascending=True)
            st.dataframe(df3)
            
        with col2:
            st.markdown('###### 10 Entregadores mais lentos')
            df3 = top_entregadores(df1, ascending=False)
            st.dataframe(df3)
