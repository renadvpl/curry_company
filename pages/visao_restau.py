# ========== LIBRARIES ========================================================================
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np
import streamlit as st
from haversine import haversine
from PIL import Image

# ========== FUNCOES ==========================================================================
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


def tempo_med( df1 , festival ):
    df_tmed = ( df1.loc[:,['Time_taken(min)','Festival']]
               .groupby(['Festival'])
               .mean().reset_index() )
    tmed = df_tmed.loc[ df_tmed['Festival'] == festival , : ].iloc[0,1]
    return tmed


def desv_padr( df1, festival ):
    df_dpad = ( df1.loc[:,['Time_taken(min)','Festival']]
               .groupby(['Festival'])
               .std().reset_index() )
    dpad = df_dpad.loc[ df_dpad['Festival'] == festival, : ].iloc[0,1]
    return dpad


# ========== IMPORTACAO DO DATASET ===========================+++++++++++++++++================
#df = pd.read_csv( 'Documents/Jupyter_Labs/repos/dataset/train.csv' )
df = pd.read_csv( 'dataset/train.csv' )

# ========== PREPARACAO DO DATASET ===========================+++++++++++++++++================
df1 = clean_code( df )


# ========== VISAO DA EMPRESA ================================+++++++++++++++++================

# ================ Barra Lateral da Pagina ====================================================

st.header('Marketplace - Visão dos Restaurantes')

#image_path = 'Documents/Jupyter_Labs/repos/dashboards/logo.jpg'
image = Image.open('logo.jpg')
st.sidebar.image( image, width=120 )

st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")
st.sidebar.markdown('## Selecione uma data-limite')
data_slider = st.sidebar.slider('# Até que valor?',
                                value=pd.datetime(2022, 3, 10),
                                min_value=pd.datetime(2022, 2, 11),
                                max_value=pd.datetime(2022, 4, 6),
                                format='DD-MM-YYYY' )

#st.metric(label='Date',value=data_slider)
st.sidebar.markdown("""---""")
traffic_options = st.sidebar.multiselect('Quais as condições do trânsito',
                          ['Low','Medium','High','Jam'],
                          default=['Low','Medium','High','Jam'])
st.sidebar.markdown("""---""")
st.sidebar.markdown('Powered by Renato Silva')

# Filtro da Data
linhas_selec = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selec, : ]

# Filtro da Transito
linhas_selec = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selec, : ]

# ================ Barra Central da Pagina ====================================================

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial',' ',' '] )

with tab1:
    with st.container():
        st.markdown('### Métricas')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            col1.metric( 'Entregadores', len(df1.loc[:,'Delivery_person_ID'].unique()) )
            
        with col2:
            colunas = ['Restaurant_latitude','Restaurant_longitude',
                       'Delivery_location_latitude','Delivery_location_longitude']
            df1['Distance'] = df1.loc[:,colunas].apply(lambda x:
                                 haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1 )
            col2.metric( 'Distância Média', round(df1['Distance'].mean(),2) )

        with col3:
            tmed_fest = tempo_med( df1 , festival='Yes ' )
            col3.metric('Tempo Méd. com Festivais', round(tmed_fest,2) )
            
        with col4:
            dpad_fest = desv_padr( df1 , festival='Yes ' )
            col4.metric('D.Padrão com Festivais', round(dpad_fest,2) )
            
        with col5:
            tmed_fest = tempo_med( df1 , festival='No ' )
            col5.metric('Tempo Méd. sem Festivais', round(tmed_fest,2) )

        with col6:
            dpad_fest = desv_padr( df1 , festival='No ' )
            col6.metric('D.Padrão sem Festivais', round(dpad_fest,2) )
    
    st.markdown("""---""")
    
    with st.container():
        st.markdown('### Distribuição da Distância')
        colunas = ['Restaurant_latitude','Restaurant_longitude',
                   'Delivery_location_latitude','Delivery_location_longitude']
        df1['Distance'] = ( df1.loc[:,colunas].apply(lambda x:
                                 haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']),
                                            (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1) )
        avg_dist = df1.loc[:,['City','Distance']].groupby('City').mean().reset_index()
        pizza = go.Figure( data=[ go.Pie(labels=avg_dist['City'], values=avg_dist['Distance'], pull=[0,0.1,0]) ] )
        st.plotly_chart(pizza)
        
    
    st.markdown("""---""")
    
    with st.container():
        st.markdown('### Distribuição do Tempo')
        col1,col2 = st.columns(2)
        
        with col1:
            df3 = ( df1.loc[:,['City','Time_taken(min)']]
                     .groupby('City')
                     .agg( {'Time_taken(min)':['mean','std']} ) )
            df3.columns = ['avg_time','std_time']
            df3 = df3.reset_index()
            fig = go.Figure()
            fig.add_trace( go.Bar( name='Control', x=df3['City'] , y=df3['avg_time'],
                                 error_y=dict( type='data' , array=df3['std_time'] )) )
            fig.update_layout(barmode='group')
            st.plotly_chart(fig)
            
        with col2:
            df5 = ( df1.loc[:,['City','Time_taken(min)','Road_traffic_density']]
                       .groupby(['City','Road_traffic_density'])
                       .agg( {'Time_taken(min)':['mean','std']} ) )
            df5.columns = ['avg_time','std_time']
            df5 = df5.reset_index()
            fig = px.sunburst( df5, path=['City','Road_traffic_density'], values='avg_time',
                              color='std_time', color_continuous_scale='rdbu',
                              color_continuous_midpoint=np.average(df5['std_time']) )
            st.plotly_chart(fig)
    
    st.markdown("""---""")
    
    with st.container():
        st.markdown('### Tempo médio de Entrega por Cidade e Tipo de Pedido')
        df4 = ( df1.loc[:,['City','Time_taken(min)','Type_of_order']]
                 .groupby(['City','Type_of_order'])
                 .agg( {'Time_taken(min)':['mean','std']}) )
        df4.columns = ['avg_time','std_time']
        df4 = df4.reset_index()
        st.dataframe(df4)
