import pandas as pd
import numpy as np
import streamlit as st
import seaborn as sns

from matplotlib import pyplot as plt


st.set_page_config( layout= 'wide') 

#help functions
def diferenca(vf,vi):
    porcentagem = np.round((( vf-vi) / vi) *100,(2))
    
    return porcentagem

path = './kc_house_data.csv'

df = pd.read_csv(path)

df['date'] = pd.to_datetime(df['date'])

#df['yr_built'].pd.to_datetime(df['yr_built']).dt.strftime('%Y-%m-%d')
df['yr_built']= pd.to_datetime(df['yr_built'],format= '%Y')

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
fig = plt.figure(figsize=(13,8))

sns.barplot(x= 'waterfront', y='price_m2_lot', data = f_h1);
