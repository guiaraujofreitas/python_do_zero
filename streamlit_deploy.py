import pandas as pd
import numpy as np
import streamlit as st

st.set_page_config( layout= 'wide') #ampliar o tamanho dos dados

@st.cache( allow_output_mutation=True ) #tira do disco e joga / mémoria(mais rápido)
def get_data(path):

    data = pd.read_csv( path )
    return data

#get data
path = './kc_house_data.csv'

data = get_data( path )


#add new feature:
#depois voltar aqui para ajustar de pá quadrada para m2.
data['price_m2']= data['price']/data['sqft_lot']


# ======================================= #
# Data Overview
# ====================================== #

st.title('Data Overview')

# attributes = selecionar colunas
# zipocode = selecionar linhas
# attributes + zipcode = selecionar linhas e colunas

f_attributes = st.sidebar.multiselect( 'Enter Columns', data.columns ) #filtro seleção coluna HouseRocket
f_zipcode = st.sidebar.multiselect('Enter Zipcode', data['zipcode'].unique() ) #filtro do endereço americano

if ( f_zipcode != [] ) & (f_attributes != [] ):
    data = data.loc[ data['zipcode'].isin(f_zipcode),f_attributes ]

elif(f_zipcode != [] ) & (f_attributes == []):
    data = data.loc[ data['zipcode'].isin(f_zipcode),:] #aqui o CEO está pedido o zipcode

elif (f_zipcode == []) & (f_attributes != [] ): #aqui o Ceo está pedido as colunas(atributos)
       data = data.loc[:, f_attributes]

else:
    data = data.copy()

df1 = data[['id','zipcode']].groupby('zipcode').count().reset_index()
df2 = data[['zipcode','price']].groupby('zipcode').mean().reset_index()
df3 = data[['zipcode','sqft_living']].groupby('zipcode').mean().reset_index()
df4 = data[['zipcode','price_m2']].groupby('zipcode').mean().reset_index()

st.dataframe( data )

#merge (unir as colunas de estastiticas criadas)

c1,c2 = st.columns((2,1))

m1 = pd.merge( df1, df2, on='zipcode', how = 'inner')
m2 = pd.merge( m1, df3, on='zipcode', how= 'inner')
df= pd.merge(m2, df4, on ='zipcode', how='inner')

df.columns = ['ZIPCODE','TOTAL HOUSES','PRICE','SQFT LIVING','PRICE/M2']

c1.header('Average Values')
c1.dataframe( df, height=600 )

#STASTITICS DESCRITIVES

num_attributes = data.select_dtypes(include= ['int64','float64'] )

media = pd.DataFrame(num_attributes.apply( np.mean ) )
mediana = pd.DataFrame( num_attributes.apply( np.median ) )
std = pd.DataFrame( num_attributes.apply( np.std ) )

max_= pd.DataFrame( num_attributes.apply( np.max ))
min_ =  pd.DataFrame (num_attributes.apply( np.min ) )

df1 = pd.concat([max_,min_,media,mediana,std], axis=1).reset_index()

df1.columns = ['attributes','MAX','MIN','MEDIA','MEDIANA','STD']

st.write( f_attributes )
st.write ( f_zipcode )

c2.header('Desciptive Stastitics')
c2.dataframe(df1, height=600)


