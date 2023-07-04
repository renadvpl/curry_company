# ========== BIBLIOTECAS ========================================================================
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import streamlit as st
import folium
from haversine import haversine
from PIL import Image
from streamlit_folium import folium_static


# ========== FUNCOES ===============================================================================

def clean_code( df1 ):
# Esta funcao tem a responsabilidade de limpar o dataframe train
# Tipos de Limpeza:
#    1. Remocao dos dados missing (NaN);
#    2. Conversao do tipo de dado da coluna;
#    3. Remocao dos espacos das variaveis de texto;
#    4. Formatacao da coluna de datas;
#    5. Limpeza da coluna de tempo (remocao de caracter de tempo)

    # Exclusoes dos registros com valores missing (NaN)
    df1 = df1.loc[ df1['Delivery_person_Age'] != 'NaN ' , :].copy()
    df1 = df1.loc[ df1['Road_traffic_density'] != 'NaN ', :].copy()
    df1 = df1.loc[ df1['Festival'] != 'NaN ', : ].copy()
    df1 = df1.loc[ df1['Time_Orderd'] != 'NaN ' , : ].copy()
    df1 = df1.loc[ df1['City'] != 'NaN ', : ].copy()
    df1 = df1.loc[ df1['multiple_deliveries'] != 'NaN ', : ].copy()

    # Conversoes do tipo de dado das colunas
    df1['Delivery_person_Age']     = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries']     = df1['multiple_deliveries'].astype(int)
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'] , format='%d-%m-%Y')

    # Renumerar os indices das linhas
    df1 = df1.reset_index( drop=True )

    # Remocao dos espacos
    df1.loc[:,'ID'] = df1.loc[:,'ID'].str.strip()
    df1.loc[:,'Road_traffic_density'] = df1.loc[:,'Road_traffic_density'].str.strip()
    df1.loc[:,'Type_of_order'] = df1.loc[:,'Type_of_order'].str.strip()
    df1.loc[:,'Type_of_vehicle'] = df1.loc[:,'Type_of_vehicle'].str.strip()
    df1.loc[:,'City'] = df1.loc[:,'City'].str.strip()

    # Remover o texto (min) e converter em numeros da coluna Time_taken(min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min)')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return ( df1 )

def order_metric( df1 ):
    df1_aux = df1.loc[:,['ID','Order_Date']].groupby('Order_Date').count().reset_index()
    df1_aux.columns = ['Order_Date','Quantily_of_deliveries']
    fig = px.bar(df1_aux,x='Order_Date',y='Quantily_of_deliveries')
    
    return fig

def traffic_order_share( df1 ):
    df1_aux = ( df1.loc[:,['ID','Road_traffic_density']]
                   .groupby('Road_traffic_density')
                   .count().reset_index() )
    df1_aux['Perc_of_devileries'] = df1_aux['ID'] / df1_aux['ID'].sum()
    fig = px.pie(df1_aux,values='Perc_of_devileries',names='Road_traffic_density')
    
    return fig

def traffic_order_city( df1 ):
    df1_aux = ( df1.loc[:,['ID','City','Road_traffic_density']]
                     .groupby(['City','Road_traffic_density'])
                     .count().reset_index() )
    fig = px.scatter(df1_aux,x='City',y='Road_traffic_density',size='ID', color='City')
    
    return fig

def order_of_week( df1 ):
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime( "%U" )
    df1_aux = df1.loc[:, ['ID','Week_of_year']].groupby('Week_of_year').count().reset_index()
    fig = px.line(df1_aux,x='Week_of_year',y='ID')
    
    return fig

def order_share_by_week( df1 ):
    df1_aux1 = df1.loc[:,['ID','Week_of_year']].groupby('Week_of_year').count().reset_index()
    df1_aux2 = ( df1.loc[:,['Delivery_person_ID','Week_of_year']]
                    .groupby('Week_of_year')
                    .nunique().reset_index() )
    df1_aux = pd.merge(df1_aux1,df1_aux2,how='inner')
    df1_aux['Deliveries_by_person/week'] = df1_aux['ID'] / df1_aux['Delivery_person_ID']
    fig = px.line(df1_aux,x='Week_of_year',y='Deliveries_by_person/week')
    
    return fig

def country_maps( df1 ):
    columns = ['City','Road_traffic_density','Delivery_location_latitude','Delivery_location_longitude']
    data_plot = df1.loc[:, columns].groupby( ['City', 'Road_traffic_density'] ).median().reset_index()

    map = folium.Map()

    for index, location_info in data_plot.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
        location_info['Delivery_location_longitude']],
        popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

    folium_static( map , width=1024 , height=600 )

# ========== INICIO DA ESTRUTURA LOGICA ============================================================

# ================= Importacao do Dataframe ========================================================
#df = pd.read_csv( 'Documents/Jupyter_Labs/repos/dataset/train.csv' )
df = pd.read_csv( 'dataset/train.csv' )

# ================= Limpeza do Dataframe ===========================================================
df1 = clean_code( df )


# ========== VISAO DA EMPRESA ============================================================================

# ================ Barra Lateral da Pagina (Side Bar) ====================================================

st.header('Marketplace - Visão Cliente')

#image_path = 'Documents/Jupyter_Labs/repos/dashboards/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image( image, width=120 )

st.sidebar.title('Curry Company')
st.sidebar.markdown('### Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('### Selecione uma data-limite')
data_slider = st.sidebar.slider('Até que valor?',
                                value=pd.datetime(2022, 3, 20),
                                min_value=pd.datetime(2022, 2, 11),
                                max_value=pd.datetime(2022, 4, 6),
                                format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Selecione as condições do trânsito')
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
                          ['Low','Medium','High','Jam'],
                          default=['Low','Medium','High','Jam'])
st.sidebar.markdown("""---""")
st.sidebar.markdown('#### Powered by Renato Silva')


# ================ Barra Central da Pagina ==============================================================

# Filtro da Data
linhas_selec = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selec, : ]

# Filtro da Transito
linhas_selec = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selec, : ]

st.dataframe(df1)


tab1, tab2, tab3 = st.tabs( ['Visão Gerencial','Visão Tática','Visão Geográfica'] )

with tab1:
    with st.container():
        st.markdown('## Order by Day')
        fig01 = order_metric(df1)
        st.plotly_chart( fig01 , use_container_width=True )

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            st.header('Traffic Order Share')
            fig02 = traffic_order_share(df1)
            st.plotly_chart( fig02 , use_container_width=True )
            
        with col2:
            st.header('Traffic Order City')
            fig03 = traffic_order_city(df1)
            st.plotly_chart( fig03 , use_container_width=True )

with tab2:
    with st.container():
        st.header('Order by Week')
        fig04 = order_of_week(df1)
        st.plotly_chart( fig04, use_container_width=True )
        
    with st.container():
        st.header('Order Share by Week')
        fig05 = order_share_by_week(df1)
        st.plotly_chart( fig05, use_container_width=True )
    
with tab3:
    st.header('Country Maps')
    fig06 = country_maps(df1)