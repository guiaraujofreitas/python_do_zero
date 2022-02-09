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

# 1ª Hipotese
f_h1 = df[['waterfront','price_m2_lot']].groupby('waterfront').median().reset_index()

#filtrando as casas c/ vista p/ o mar
a = f_h1.loc[f_h1['waterfront']== 0]

#filtrando as casas s/ vista para o mar
b = f_h1.loc[f_h1['waterfront']!= 0]

#calculando a diferença em % / pegando o primeiro valor de cada característica do imóvel

porcentagem = diferenca(vf=b['price_m2_lot'].iloc[0], vi=a['price_m2_lot'].iloc[0])

print('A diferença é de {} %'.format(porcentagem))

#plotando o gráfico

#dimensão do gráfico
#fig = plt.figure(figsize=(13,8))

#sns.barplot(x= 'waterfront', y='price_m2_lot', data = f_h1);

figure= px.bar(f_h1, x= 'waterfront', y='price_m2_lot' )
st.plotly_chart(figure)

############################################################################################

#============= Filtros ===================== #

min_year_built = int(df['yr_built'].min())
max_year_built = int(df['yr_built'].max())


st.sidebar.title ('Commercial Options') #título do filtro
st.title (' Commercial Attributes')

st.sidebar.subheader('Select Max Year Built') #texto em cima do filtro

f_year_built = st.sidebar.slider('Year Built', min_year_built,
                                            max_year_built,
                                            min_year_built )


#agrupando e criando os filtros das casas construidas.
f_h2 = df[['yr_built','price_m2_lot']].groupby('yr_built').median().reset_index()

# filtrando os imóveis antes do ano de 1955
menor = f_h2.loc[f_h2['yr_built'] < '1955']

#filtrando os imóveis construindo desde de 1955
maior = f_h2.loc[f_h2['yr_built'] >= '1955']

#descobriando a mediana de preços dos imóveis mais antigo
antigo = menor.median(numeric_only=True).iloc[0]

#descobrindo a mediana de preços dos imóveis mais novos
novo   = maior.median(numeric_only=True).iloc[0]

## making the plot 

c1, c2, c3 = st.columns(3)

c1.header('Prices M2 Houses by Year of Built')

fig = px.bar(f_h2,x='yr_built', y='price_m2_lot')
c1.plotly_chart(fig, user_container_witdh= True)

fig_teste = px.scatter(f_h2, x='yr_built',y= 'price_m2_lot')
c1.plotly_chart(fig_teste,user_container_witdh= True)

c2.header('Prices M2 of Smalll of Houses Built')

fig1 = px.bar(maior, x='yr_built', y='price_m2_lot')
c2.plotly_chart(fig1,user_container_witdh= True)

fig_teste = px.scatter(menor, x='yr_built',y= 'price_m2_lot')
c2.plotly_chart(fig_teste,user_container_witdh= True)

c3.header('Prices M2 of Beyourd of Houses Built')
fig2 = px.bar(menor, x='yr_built', y='price_m2_lot')
c3.plotly_chart(fig2, user_container_witdh= True)
fig_teste = px.scatter(maior, x='yr_built',y= 'price_m2_lot')
c3.plotly_chart(fig_teste, user_container_witdh= True)


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
location = df1.head(50).copy(deep=True)

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
                       'city','neighbourhood','acquisition']].copy(deep=True)

st.title( 'TABLE OF ACQUISITION OF HOUSES')
st.dataframe(tabela)

######## TABLE SELL OF HOUSES 

st.title( 'TABLE SELL OF HOUSES')

#linha que calculo o preço de venda dos imóveis:
tabela['sell']= tabela.apply(lambda x: (x['price']* 0.30 + x['price']) if x['acquisition']=='buy' 
                                 else (x['price'] *0.10 + x['price']),axis=1)

#linha que calculo a lucratividade dos imóveis
tabela['lucro'] = tabela.apply(lambda x: x['sell'] - x['price'],axis=1)

#criando coluna com as respectivas porcentagens de lucro das vendas dos imóveis
tabela['porcentagem_lucro'] = diferenca(vf=tabela['sell'],vi=tabela['price'])

table_sell = tabela.copy(deep=True)

st.dataframe(table_sell)

#========= MAP ================
houses = df1[['id','price','lat','long']].copy()

houses = px.density_mapbox(df, lat='lat', lon='long',z= 'price_m2_lot',radius=10,zoom=8,
                            mapbox_style="stamen-terrain")

houses.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
st.plotly_chart(houses,user_container_witdh= True)

