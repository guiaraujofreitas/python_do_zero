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

df['yr_built']= pd.to_datetime(df['yr_built']).dt.strftime('%Y-%m-%d')


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
location = df.head(30).copy(deep=True)

#select columns necessary
location = location[['id','zipcode','price','price_region','price_seasons','condition',
                     'waterfront','lat','long','bedrooms','bathrooms']].copy(deep=True)

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
                       'city','neighbourhood','acquisition','lat','long','bedrooms']].copy(deep=True)

### TABLE DE OF SELL ######


#linha que calculo o preço de venda dos imóveis:
tabela['sell']= tabela.apply(lambda x: (x['price']* 0.30 + x['price']) if x['acquisition']=='buy' 
                                 else (x['price'] *0.10 + x['price']),axis=1)

#linha que calculo a lucratividade dos imóveis
tabela['lucro'] = tabela.apply(lambda x: x['sell'] - x['price'],axis=1)

#criando coluna com as respectivas porcentagens de lucro das vendas dos imóveis
tabela['porcentagem_lucro'] = diferenca(vf=tabela['sell'],vi=tabela['price'])


#st.dataframe(tabela)
#########################################
f_zipcode = st.sidebar.multiselect('Select the ZIPCODE of Houses',tabela['zipcode'].unique())




f_waterfront = st.sidebar.selectbox('Is Waterfront', tabela['waterfront'].unique())


###################################


#f_attributes = st.sidebar.multiselect('Select the columns', df.columns)



#

price_min = int(tabela['price'].min())
price_mean = int(tabela['price'].mean())
price_max = int(tabela['price'].max()) 

price_slider = st.slider('Price of Houses Average', price_min,price_max, price_mean)



is_check = st.checkbox('Display Table and Map')
               
if is_check:
    
    tabela = tabela[tabela['price']< price_slider]

  

    if f_zipcode:
        tabela = tabela.loc[tabela['zipcode'].isin(f_zipcode)]
        
        if f_waterfront:
            tabela = tabela.loc[tabela['waterfront']==1]
    
    num_houses = len(tabela)  
         
    st.write('The Humber of Houses select are:', num_houses)

    st.dataframe(tabela)
    
    st.subheader('MAP OF HOUSES SELECT')
       #========= MAP ================
    fig = px.scatter_mapbox(tabela, 
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
  
# ======================== Plot ==================== #

# Hipotese 1:

f_h1 = df[['waterfront','price_m2_lot']].groupby('waterfront').median().reset_index()

#filtrando as casas c/ vista p/ o mar
a = f_h1.loc[f_h1['waterfront']== 0]

#filtrando as casas s/ vista para o mar
b = f_h1.loc[f_h1['waterfront']!= 0]

#calculando a diferença em % / pegando o primeiro valor de cada característica do imóvel

porcentagem = diferenca(vf=b['price_m2_lot'].iloc[0], vi=a['price_m2_lot'].iloc[0])



#plotando o gráfico

#fig = plt.figure(figsize=(13,8))
fig = px.bar(f_h1, x= 'waterfront', y= 'price_m2_lot')

st.title('H1: Imóveis que possuem vista para água, são 30% mais caros, na média.')
st.write('Falsa: Imóveis com vista para água em média 45,93% mais caros em relação aos que não contém vista para o mar.')
#plot  
st.plotly_chart(fig)     

## H2 ############

st.title('H2: Imóveis com data de construção menor que 1955, são 50% mais baratos, na média')
st.write('Casas construidas antes de 1955 não são 50% mais baratas. Elas são em média 133.3 % mais caras em comparação aos imóveis construídos após esse período')

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

#plots

fig1 = px.scatter(f_h2, x='yr_built', y= 'price_m2_lot') 
st.plotly_chart(fig1)

############### H3 ###############
st.title('H3: Imóveis sem porão possuem sqrt_lot, são 50%¶ maiores do que com porão.')
st.subheader('Falso: Os imóveis sem porão são 3,62% maiores do que as casas com porão')
c1,c2,c3 = st.columns(3)

f_h3 = df[['m2_lot','m2_basement']].groupby('m2_lot').median().reset_index()

#filtrando as casas sem porão
without_basement = f_h3.loc[f_h3['m2_basement']== 0]

#filtrando as casas com porão
with_basement = f_h3.loc[f_h3['m2_basement']!= 0]

#============================================================#

c1.subheader('ALL HOUSES')
#plot1
fig = px.scatter(f_h3, x= 'm2_lot', y= 'm2_basement')
c1.plotly_chart(fig)

c2.subheader('HOUSES WITH BASEMENT')
#plot2
fig2 = px.scatter(with_basement, x='m2_lot', y='m2_basement')
c2.plotly_chart(fig2)

c3.subheader('HOUSES WITHOUT BASEMENT')
#plot3
fig3 = px.scatter(without_basement, x='m2_lot', y='m2_basement')
c3.plotly_chart(fig3)

############## H4 ##########################
st.title('H4: O crescimento do preço dos imóveis YoY ( Year over Year ) é de 10%')
st.subheader('Falso: O Crescimenmto anual dos imóveis são de -51.19 %')

c1, c2 = st.columns(2)

#separando, agrupando e somando os valores dos respectivos anos do DF
by_year = df[['price_m2_lot','year']].groupby('year').sum().reset_index()


# fazendo o calculo % utilizndo função do pandas pct._charge() para calcular a diferença do ano para outro
by_year['pct'] = by_year['price_m2_lot'].pct_change()

#criando coluna para indentificar quais são os anos negativos e positivo
by_year['color'] = by_year['pct'].apply(lambda x: 'negativo' if x<0 else 'positivo')

crescimento = by_year['pct'].loc[1] * 100

# ===== montagem do gráfico ======= #

# selecionado as cores do gráfico
#color = ['Positivo','price_m2_lot'] 

fig = px.bar(by_year, x= 'year', y= 'price_m2_lot', color= 'color', title = 'Price m2 by Year')
c1.plotly_chart(fig)

fig2 = px.bar( by_year, x= 'year', y= 'pct', color = 'color', title = 'Grothwing of Houses by Year')
c2.plotly_chart(fig2)
