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
    data.copy()

st.write( f_attributes )
st.write ( f_zipcode )
st.write( data )

#st.write ( data.head() )
