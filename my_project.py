import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns
import plotly.express as px
import matplotlib.pyplot as plt

from matplotlib import pyplot as plt
from datetime import datetime

st.set_page_config( layout= 'wide') 

#help functions
def diferenca(vf,vi):
    porcentagem = np.round((( vf-vi) / vi) *100,(2))
    
    return porcentagem

path = './kc_house_data.csv'

df = pd.read_csv(path)

df['date'] = pd.to_datetime(df['date'])

#df['yr_built']= pd.to_datetime(df['yr_built']).dt.strftime('%Y-%m-%d')

#df['yr_built']= pd.to_datetime(df['yr_built'],format= '%Y')

#df['yr_built']= pd.to_datetime( df['yr_built'] ).dt.strftime( '%Y )

#criando coluna do mês
df['month'] = df['date'].dt.month

#criando coluna dos anos
df['year'] = df['date'].dt.year

#criando coluna para transformar pé quadrado em área quadrado
df['m2_lot'] = df['sqft_lot'].apply(lambda x: np.round(x * 0.092903,2) )

#criando coluna de preços por M2
df['price_m2_lot'] = np.round(df['price'] / df['m2_lot'],2)

# transformando pé quadrados das salas em M2
df['m2_living'] = np.round(df['sqft_living']* 0.092903,2) 

df['m2_basement'] = np.round(df['sqft_basement'] * 0.092903,2)
# ================================================================ #

df = df.copy()

#criando coluna das estações
df['seasons'] = df['month'].apply(lambda x: 'spring'  if (x>=3 and x<=5) else 'summer' if (x>=6 and x<=8) else 
                                  'fall' if (x>=9 and x<=11) else 'winter')

#criando coluna de referencia numerica das estações
df['numeric_seasons'] = df['seasons'].apply(lambda x: 1 if x == 'summer' else 2 if x== 'spring' 
                                              else 3 if x== 'fall' else 4)

#fazendo a mediana de preços dos endereços(zipcode) por preço por M2 construídos
price_region = df[['zipcode','price_m2_lot']].groupby('zipcode').median().reset_index()

#renomenado as colunas para futura mescla
price_region.columns= ['zipcode','price_region']

#fazenddo as medianas de zipcode e numeric_seasons 
seasons_median = df[['numeric_seasons','zipcode','price_m2_lot']].groupby(['zipcode','numeric_seasons']).median().reset_index()

seasons_median.columns = ['zipcode','numeric_seasons','price_seasons']

#unificando os preços medianos das regioões com o DF original
df = pd.merge(df,price_region, on='zipcode',how='inner')

#unificando a mediana de preços por estações do ano
df = pd.merge(df,seasons_median, on= ['zipcode','numeric_seasons'], how='inner')

#=============================================================================

### TABLE ACQUISITON OF HOUSES 
#loading date
location = df.head(50).copy(deep=True)

#select columns necessary
location = location[['id','zipcode','price','price_region','price_seasons','condition',
                     'waterfront','lat','long']].copy(deep=True)

#library of maps
from geopy.geocoders import Nominatim

#initialize Nominatim APi

geolocator = Nominatim(user_agent ='geoapiExercises') #porteiro

#guardando a latitude e longitude para acessar o endereço no mapa
#response=geolocator.reverse ('47.4977,-122.226')

for i in range(len(location)):
    
    #descobrindo a localização dos imóveis
    query = str(location.loc[i,'lat']) + ',' + str(location.loc[i,'long'])
    
    response = geolocator.reverse(query,timeout=1000)
    
    if 'city' in response.raw['address']:
        location.loc[i,'city'] = response.raw['address']['city']
    
        if 'state' in response.raw['address']:
            location.loc[i,'state']= response.raw['address']['state']
    
            if 'neighbourhood'in response.raw['address']:
                location.loc[i,'neighbourhood']= response.raw['address']['neighbourhood']
    
        #linha de condição de compra de acordo com os perfis dos imóveis 
    location['acquisition'] = location.apply(lambda x: 'buy' if (x['price_seasons']< x['price_region']) 
                                                 & (x['waterfront']==1) & (x['condition']>=3) else 'no_buy', axis=1)
       
    tabela = location[['id','zipcode','price','price_region','condition','waterfront','state',
                       'city','neighbourhood','acquisition','lat','long']].copy(deep=True)

### TABLE DE OF SELL ######


#linha que calculo o preço de venda dos imóveis:
tabela['sell']= tabela.apply(lambda x: (x['price']* 0.30 + x['price']) if x['acquisition']=='buy' 
                                 else (x['price'] *0.10 + x['price']),axis=1)

#linha que calculo a lucratividade dos imóveis
tabela['lucro'] = tabela.apply(lambda x: x['sell'] - x['price'],axis=1)

#criando coluna com as respectivas porcentagens de lucro das vendas dos imóveis
tabela['porcentagem_lucro'] = diferenca(vf=tabela['sell'],vi=tabela['price'])

st.dataframe(tabela)
#########################################


#f_attributes = st.sidebar.multiselect('Select the columns', df.columns)

f_zipcode = st.sidebar.multiselect('Select the ZIPCODE of Houses',tabela['zipcode'].unique())

f_condition = st.sidebar.multiselect('Select kind condition of Houses',tabela['condition'].unique())


f_waterfront = st.sidebar.selectbox('Is Waterfront', tabela['waterfront'].unique())

f_attributes = tabela.columns
is_check = st.checkbox('Display Table and Map')

#

price_min = int(tabela['price'].min())
price_mean = int(tabela['price'].mean())
price_max = int(tabela['price'].max()) 

price_slider = st.slider('Price of Houses Average', price_min,price_max, price_mean)

if is_check:
    
    houses = tabela[tabela['price']< price_slider],f_attributes 
    

    houses = tabela[tabela['waterfront']==f_waterfront]
    
    if f_condition:
        houses = tabela[tabela['condition'].isin(f_condition)]
    
    if  f_zipcode :
        houses = tabela[tabela['zipcode'].isin(f_zipcode)]
        
            

   
    #========= MAP ================

    fig = px.scatter_mapbox( houses, 
                        lat = 'lat',
                        lon = 'long', 
                        size ='price',
                        color_continuous_scale=px.colors.cyclical.IceFire,
                        size_max = 15,
                        zoom =10 )
    #atribuindo o modelo de mapa 
    fig.update_layout(mapbox_style = 'open-street-map')
    #colocando as margens do mapa 
    fig.update_layout(height=600, margin= {'r':0, 't':0, 'l':0, 'b': 0} )

    #fig.show()
    st.plotly_chart(fig,user_container_witdh= True)
    
        
    

    st.dataframe(houses)



