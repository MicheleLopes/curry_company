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

st.set_page_config(page_title='Visão Empresa')

#--------------------------------------------------------------
#---------------------------Funções----------------------------
#--------------------------------------------------------------
def mapa_loc_central(df1):
    df_aux = df1.loc[:, ['Delivery_location_latitude', 'City','Road_traffic_density','Delivery_location_longitude']].groupby(
        ['City','Road_traffic_density']).median().reset_index()
    map = folium.Map()
    for index, location in df_aux.iterrows():
        folium.Marker([location['Delivery_location_latitude'], 
                       location['Delivery_location_longitude']],    popup=location[
                      ['City','Road_traffic_density']]).add_to(map)
    folium_static(map, width=800, height=600)
    return None
def pedidos_entregador_semana(df1):
    entregas = df1.loc[:, ['ID', 'week_of_year']].groupby(['week_of_year']).count().reset_index()
    entregadores = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby(['week_of_year']).nunique().reset_index()
    df_aux = pd.merge(entregas, entregadores, how='inner')
    df_aux['order_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']
    grafico = px.line(df_aux, x='week_of_year', y='order_deliver')
    return grafico
    
def pedidos_semana(df1):
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    grafico = px.line(df_aux, x= 'week_of_year', y= 'ID')
    return grafico
    
def pedidos_trafego(df1):
    """
    escrever sobre essa funcao aqui
    """
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby('Road_traffic_density').count().reset_index()
    df_aux = df_aux.loc[(df_aux['Road_traffic_density'] != 'NaN'), :]
    df_aux['percentual'] = df_aux['ID'] / df_aux['ID'].sum()
    grafico = px.pie(df_aux, values = 'percentual', names = 'Road_traffic_density')
    return grafico
    
def pedidos_dia(df1):
    """ 
    escrever sobre essa funcao aqui
    """
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby('Order_Date').count().reset_index()
    grafico = px.bar(df_aux, x='Order_Date', y='ID')
    return grafico

def pedidos_trafego_cidade(df1):
    """
    escrever sobre essa funcao aqui
    """
    df_aux = df1.loc[:, ['ID', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).count().reset_index()
    df_aux = df_aux.loc[(df_aux['Road_traffic_density'] != 'NaN'), :]
    df_aux = df_aux.loc[(df_aux['City'] != 'NaN'), :]
    grafico = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color = 'City')
    return grafico


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

st.header( 'Crescimento Empresa')
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
tab1, tab2, tab3 = st.tabs(['Visão Planejamento','Visão Estratégica', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.markdown('## Quantidade pedidos por dia')
        grafico = pedidos_dia(df1)
        st.plotly_chart(grafico, use_container_width=True)
        
    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('## Pedidos por tipo de tráfego')
            grafico = pedidos_trafego(df1)
            st.plotly_chart(grafico, use_container_width=True)
            
        with col2:
            st.markdown('## Pedidos por tipo de tráfego e cidade')
            grafico = pedidos_trafego_cidade(df1)
            st.plotly_chart(grafico, use_container_width=True)
            
with tab2:
    with st.container():
        st.markdown('## Quantidade pedidos por semana')
        grafico = pedidos_semana(df1)
        st.plotly_chart(grafico, use_container_width=True)
        
    with st.container():
        st.markdown('## Quantidade de pedidos por entregador por semana')
        grafico = pedidos_entregador_semana(df1)
        st.plotly_chart(grafico, use_container_width=True)
with tab3:
    with st.container():
        st.markdown('## Mapa da localização central de cada cidade por tipo de tráfego')
        mapa_loc_central(df1)
        
