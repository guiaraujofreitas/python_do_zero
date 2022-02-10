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

st.title(" Overview")

st.dataframe(df)

#
############################################################################################




# ===================================================================== #


##### TABLE OF ACQUISTION ######
df1 = df.copy()
#criando coluna das estações
df1['seasons'] = df['month'].apply(lambda x: 'spring'  if (x>=3 and x<=5) else 'summer' if (x>=6 and x<=8) else 
                                  'fall' if (x>=9 and x<=11) else 'winter')

#criando coluna de referencia numerica das estações
df1['numeric_seasons'] = df1['seasons'].apply(lambda x: 1 if x == 'summer' else 2 if x== 'spring' 
                                              else 3 if x== 'fall' else 4)

#fazendo a mediana de preços dos endereços(zipcode) por preço por M2 construídos
price_region = df1[['zipcode','price_m2_lot']].groupby('zipcode').median().reset_index()

#renomenado as colunas para futura mescla
price_region.columns= ['zipcode','price_region']

#fazenddo as medianas de zipcode e numeric_seasons 
seasons_median = df1[['numeric_seasons','zipcode','price_m2_lot']].groupby(['zipcode','numeric_seasons']).median().reset_index()

seasons_median.columns = ['zipcode','numeric_seasons','price_seasons']

#unificando os preços medianos das regioões com o DF original
df1 = pd.merge(df1,price_region, on='zipcode',how='inner')

#unificando a mediana de preços por estações do ano
df1 = pd.merge(df1,seasons_median, on= ['zipcode','numeric_seasons'], how='inner')

#TABLE ACQUISITION OF HOUSES

#loading date
location = df1.head(320).copy(deep=True)

#select columns necessary
location = location[['id','zipcode','price','price_region','price_seasons','condition',
                     'waterfront','lat','long']].copy(deep=True)
##============ MAPS ====================== #

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

st.title( 'TABLE OF ACQUISITION OF HOUSES')
st.dataframe(tabela)


### Filtro map #######


##========= MAP ================
houses = tabela[['id','price','lat','long']].copy(deep=True)

houses = px.density_mapbox(tabela, lat='lat', lon='long',z= 'price',radius=10,zoom=8,
                            mapbox_style="stamen-terrain")

houses.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(houses,user_container_witdh= True)


######## TABLE SELL OF HOUSES #################



