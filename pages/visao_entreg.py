# ========== LIBRARIES ========================================================================
import plotly.express as px
import pandas as pd
import streamlit as st
from PIL import Image

# ========== FUNÇÕES ==========================================================================
def top_delivery( df1, order_list ):
    df_aux = ( df1.loc[:,['Delivery_person_ID','City','Time_taken(min)']]
               .groupby(['City','Delivery_person_ID'])
               .mean()
               .sort_values(['City','Time_taken(min)'],ascending=order_list).reset_index() )

    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian',:].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Urban',:].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Semi-Urban',:].head(10)

    df1_aux = pd.concat([df_aux01, df_aux02, df_aux03])
    df1_aux = df1_aux.reset_index(drop=True)
    
    return df1_aux


def clean_code( df1 ):
    ####################################################################
    # Esta funcao tem a responsabilidade de limpar o dataframe train   #
    # Tipos de Limpeza:                                                #
    #    1. Remocao dos dados missing (NaN);                           #
    #    2. Conversao do tipo de dado da coluna;                       #
    #    3. Remocao dos espacos das variaveis de texto;                #
    #    4. Formatacao da coluna de datas;                             #
    #    5. Limpeza da coluna de tempo (remocao de caracter de tempo)  #
    ####################################################################

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

                        
# ========== IMPORTACAO DO DATASET =================================================================
#df = pd.read_csv( 'Documents/Jupyter_Labs/repos/dataset/train.csv' )
df = pd.read_csv( '/dataset/train.csv' )


# ================= Limpeza do Dataframe ===========================================================
df1 = clean_code( df )

                        
# ========== VISAO DA EMPREGADORES =============================================================

st.header('Marketplace - Visão dos Entregadores')

#image_path = 'Documents/Jupyter_Labs/repos/dashboards/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data-limite')
data_slider = st.sidebar.slider('# Até que valor?',
                                value=pd.datetime(2022, 3, 1),
                                min_value=pd.datetime(2022, 2, 11),
                                max_value=pd.datetime(2022, 4, 6),
                                format='DD-MM-YYYY' )

st.sidebar.markdown("""---""")
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
                          ['Low','Medium','High','Jam'],
                          default=['Low','Medium','High','Jam'])
weather_options = st.sidebar.multiselect('Quais as condições climáticas',
                          ['conditions Cloudy','conditions Fog','conditions Sandstorms',
                           'conditions Stormy','conditions Sunny','conditions Windy'],
                          default=['conditions Cloudy','conditions Fog','conditions Sandstorms',
                                   'conditions Stormy','conditions Sunny','conditions Windy'])
st.sidebar.markdown("""---""")
st.sidebar.markdown('##### Powered by Renato Silva')

# Filtro da Data
linhas_selec = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selec, : ]

# Filtro do Transito
linhas_selec = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selec, : ]

# Filtro da Condicao Climatica
linhas_selec = df1['Weatherconditions'].isin(weather_options)
df1 = df1.loc[linhas_selec, : ]


# ================ Barra Central da Pagina ====================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial',' ',' '] )

with tab1:
    with st.container():
        st.markdown('### Métricas')
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            maior_idade = df1.loc[:,'Delivery_person_Age'].max()
            col1.metric('Maior Idade',maior_idade)
            
        with col2:
            menor_idade = df1.loc[:,'Delivery_person_Age'].min()
            col2.metric('Menor Idade',menor_idade)
            
        with col3:
            melhor_veic = df1.loc[:,'Vehicle_condition'].max()
            col3.metric('Melhor Veiculo',melhor_veic)
            
        with col4:
            pior_veic = df1.loc[:,'Vehicle_condition'].min()
            col4.metric('Pior Veiculo', pior_veic)
            
    st.markdown("""---""")
    
    with st.container():
        st.markdown('### Avaliações')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df1_med_entreg = ( df1.loc[:,['Delivery_person_ID','Delivery_person_Ratings']]
                                  .groupby('Delivery_person_ID')
                                  .mean().reset_index() )
            st.dataframe( df1_med_entreg )
            
        with col2:
            st.markdown('##### Avaliação média por tráfego')
            df1_med_trafego = ( df1.loc[:,['Delivery_person_Ratings','Road_traffic_density']]
                                   .groupby('Road_traffic_density')
                                   .agg({'Delivery_person_Ratings':['mean','std']}) )
            df1_med_trafego.columns = ['Delivery_Mean','Delivery_St_Dev']
            df1_med_trafego.reset_index()
            st.dataframe( df1_med_trafego )
                
            st.markdown('##### Avaliação média por condição climática')
            df1_med_clim = ( df1.loc[:,['Delivery_person_Ratings','Weatherconditions']]
                                .groupby('Weatherconditions')
                                .agg({'Delivery_person_Ratings':['mean','std']}) )
            df1_med_clim.columns = ['Weather_Mean','Weather_St_Dev']
            df1_med_clim.reset_index()
            st.dataframe( df1_med_clim )

    st.markdown("""---""")

    with st.container():
        st.markdown('### Velocidade das Entregas')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('##### Top 10 entregadores mais rápidos')
            df6 = top_delivery( df1, order_list=True )
            st.dataframe( df6 )
            
        with col2:
            st.markdown('##### Top 10 entregadores mais lentos')
            df7 = top_delivery( df1, order_list=False )
            st.dataframe( df7 )