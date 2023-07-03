import streamlit as st
from PIL import Image

st.set_page_config(
    page_title="Home",
    page_icon="🈳"
)
image_path = 'C:/Users/renat/Documents/Jupyter_Labs/repos/dashboards/'
image = Image.open( image_path + 'logo.jpg' )
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write( '# Curry Company Growth Dashboard' )

st.markdown(
    """
    Growth Dashboard foi construido para acompanhar as metricas de crescimento dos
    entregadores e restaurantes.
    ### Como utilizar esse Growth Dashboard?
    - Visao da Empresa:
      - Visao Gerencial: Metricas gerais de comportamento;
      - Visao Tatica: Indicadores semanais de crescimento;
      - Visao Geografica: Insights de geolocalizacao.
    - Visao dos Entregadores:
      - Acompanhamento dos indicadores semanais de crescimento.
    - Visao dos Restaurantes:
      - Indicadores semanais de crescimento dos restaurantes.
    ### Ask for Help
      - Time de Data Science no Discord
    """ )

