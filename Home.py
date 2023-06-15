import streamlit as st
from PIL import Image

st.set_page_config(page_title="Home")

col1, col2 = st.sidebar.columns(2)
with col1:
    image = Image.open('image.png')
    st.image(image, width=120)
with col2:    
    st.markdown('# Cury Company')
    
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write("# Curry Company Growth Dashboard")

st.markdown("""
	Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
### Como utilizar esse Growth Dashboard?
- Visão Empresa:
	- Visão Gerencial: Métricas gerais de comportamento.
	- Visão Tática: Indicadores semanais de crescimento.
- Visão Entregadores:
	- Acompanhamento dos indicadores semanais de crescimento.
- Visão Restaurante:
	- Indicadores semanais de crescimento dos restaurantes.
### Ask for Help
Email: miichele.lopesf@gmail.com
""")