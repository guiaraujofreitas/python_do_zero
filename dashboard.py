import pandas as pd
import numpy as np
import streamlit as st
import folium
import geopandas
import plotly.express as px

from datetime import datetime 
from folium.plugins import MarkerCluster
from streamlit_folium import folium_static


st.set_page_config( layout= 'wide') #ampliar o tamanho dos dados

@st.cache( allow_output_mutation=True ) #tira do disco e joga / mémoria(mais rápido)
def get_data(path):

    data = pd.read_csv( path )
    return data

#ler arquivo geopandas
@st.cache( allow_output_mutation=True )
def get_geofile( url ):
    geofile = geopandas.read_file( url )
    
    return geofile


def set_feature( data ):
    #add new feature:
    data['price_m2']= data['price']/data['sqft_lot']
    
    return data

def overview_data(data):

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

    elif ( f_zipcode != [] ) & (f_attributes == []):
        data = data.loc[ data['zipcode'].isin(f_zipcode),:] #aqui o CEO está pedido o zipcode

    elif ( f_zipcode == [] ) & ( f_attributes != [] ): #aqui o Ceo está pedido as colunas(atributos)
        data = data.loc[:, f_attributes]

    else:
        data = data.copy()



    st.dataframe( data )

    df1 = data[['id','zipcode']].groupby('zipcode').count().reset_index()
    df2 = data[['zipcode','price']].groupby('zipcode').mean().reset_index()
    df3 = data[['zipcode','sqft_living']].groupby('zipcode').mean().reset_index()
    df4 = data[['zipcode','price_m2']].groupby('zipcode').mean().reset_index()



    #merge (unir as colunas de estastiticas criadas)

    c1,c2 = st.columns((2,1))

    m1 = pd.merge( df1, df2, on='zipcode', how = 'inner')
    m2 = pd.merge( m1, df3, on='zipcode', how= 'inner')
    df= pd.merge(m2, df4, on ='zipcode', how='inner')

    df.columns = ['ZIPCODE','TOTAL HOUSES','PRICE','SQFT LIVING','PRICE/M2']

    c1.header('Average Values')
    c1.dataframe( df, height=600 )


    ##### STASTITICS DESCRITIVES ################

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
    
    return None

def portifolio_density(data,geofile):
    
     #======================================= #
    # Densidade de Portifólio
    # ====================================== #

    st.title ('Region Overview' )

    c1,c2 = st.columns( ( 1,1 ) )

    c1.header('Portifolio Density')

    df = data.sample(10)

    #Base Map- Folium
    density_map =folium.Map( location=[data['lat'].mean(),data['long'].mean()],default_zoom_start=15 )

    marker_cluster = MarkerCluster().add_to( density_map )

    #marker_cluster = MarkerCluster().add_to( density_map )
    for name, row in df.iterrows():
        folium.Marker( [row['lat'], row['long'] ],
        popup= 'Sold R${0} on: {1}.Features: {2} sqft, {3} bedrooms, {4} bathrooms, year built: {5}'.format(row['price'],
                        row['date'],
                        row['sqft_living'],
                        row['bedrooms'],
                        row['bathrooms'],
                        row['yr_built'] ) ).add_to( marker_cluster )

    with c1:
        folium_static(density_map)

    #Region Price Map
    c2.header ( 'Price Density')

    df = data[['price','zipcode']].groupby('zipcode').mean().reset_index()

    df.columns= [ 'ZIP','PRICE']


    geofile = geofile[geofile['ZIP'].isin( df['ZIP'].tolist() )]

    region_price_map= folium.Map( location=[data['lat'].mean(), data['long'].mean()],
                        default_zomm_start=15)

    #densidade por cor
    region_price_map.choropleth(data=df,
                                geo_data=geofile,
                                columns=['ZIP','PRICE'],
                                key_on='feature.properties.ZIP',
                                fill_color= 'YlOrRd',
                                fill_opacity= 0.7,
                                line_opacity= 0.2,
                                legend_name= 'AVG`PRICE' )
    with c2:
        folium_static( region_price_map )

def commercial(data):
    
    #======================================= #
    # Distribuição dos imóveis por categorias comerciais
    # ====================================== #

    #====== Average Price Yr Built by Year ============

    # ==== filtros ====== #

    #barra de seleção
    min_year_built = int(data['yr_built'].min() )
    max_year_built = int(data['yr_built'].max() )


    st.sidebar.title ('Commercial Options') #título do filtro
    st.title (' Commercial Attributes')

    st.sidebar.subheader('Select Max Year Built') #texto em cima do filtro
    f_year_built = st.sidebar.slider('Year Built', min_year_built,
                                            max_year_built,
                                            min_year_built )
    #filtro por Year
    df = data.loc[data['yr_built'] < f_year_built]

    df = df[['yr_built','price']].groupby('yr_built').mean().reset_index()

    #plot
    fig = px.line( df, x= 'yr_built', y = 'price')

    st.plotly_chart( fig, use_container_width= True ) #para deixar o gráfico correspondende c/ a tela


    # ====== Average Price YR Built by Day =========

    st.header('Average Price per Day')
    st.sidebar.subheader('Select The Day Built')

    #filtro por day
    #barra seleção dia:
    data['date'] = data['date'] = pd.to_datetime( data['date'] ).dt.strftime( '%Y-%m-%d' )

    min_date = datetime.strptime(data['date'].min(),'%Y-%m-%d')

    max_date = datetime.strptime(data['date'].max(),'%Y-%m-%d')

    f_date = st.sidebar.slider('Select Day', min_date, max_date, min_date)
      

    data['date'] = pd.to_datetime(data['date'])
    df = data.loc[data['date']< f_date] #date filtering
    df= data[['date','price']].groupby('date').mean().reset_index()


    #plot date

    fig2= px.line(df, x= 'date',y= 'price')

    st.plotly_chart( fig2, use_container_witdh=True ) #tamanho total do espaço

    ## ========== Histograma ==================

    #filters 
    st.title('Distribuição dos Atributos dos imóveis')
    st.subheader('Plot Histograma')

    min_price = int(data['price'].min())
    max_price = int(data['price'].max())
    avg_price = int(data['price'].mean())


    f_price = st.sidebar.slider('Select The Price', min_price,max_price, avg_price,min_price)

    #Filters Bedrooms

    df = data[data['price']< f_price]

    fig = px.histogram(df, x ='price',nbins = 50)

    st.plotly_chart(fig, user_container_witdh= True)

    return None

def attributes_distribuition(data):
    
    #####======= Atributos =========

    #filtros dos atributos:

    f_bathrooms = st.sidebar.selectbox('Number de Bathrooms', sorted(data['bathrooms'].unique( ) ) )

    f_bedrooms = st.sidebar.selectbox('Number Bedrooms', sorted(data['bedrooms'].unique( ) ) )

    f_floor = st.sidebar.selectbox('Number Floors', sorted(data['floors'].unique() ) )

    f_waterfront = st.sidebar.selectbox('Select Water Is Front', data['waterfront'].unique( ) )


    c1, c2 = st.columns(2)

    #Title Bedrooms and Bathrooms
    c1.subheader('Histrogram Bedrooms')
    c2.subheader('Histrogram Bathrooms')
    #filter bedrooms:

    df= data[data['bedrooms']<= f_bedrooms]

    fig = px.histogram(df, x='bedrooms', nbins=20)
    c1.plotly_chart(fig, user_container_witdh= True)


    ###======= Barthrooms ==========


    df = data[data['bathrooms'] <= f_bathrooms]

    fig =px.histogram(df, x= 'bathrooms', nbins=20)
    c2.plotly_chart(fig, user_container_witdh= True)


    #===================================== ##

    cf,cw = st.columns(2)

    cf.subheader('Histrogram Houses per Floor') 
    cw.subheader('Histrogram Water Front')

    ### ======= Floors =========

    df = data[data['floors']<= f_floor]

    fig = px.histogram(df, x='floors', nbins=20)
    cf.plotly_chart(fig, user_container_witdh= True)

    ## ====== WaterFront =============

    if f_waterfront:
        df = data[data['waterfront'] == 1]

    else:
        data.copy()

    fig = px.histogram(df, x='waterfront', nbins=10)
    cw.plotly_chart(fig, user_container_witdh= True)
    
    return None


if __name__ == "__main__":
    #ETL
    #data extraction
    #get data
    path = './kc_house_data.csv'
    data = get_data( path )

    #get geofile
    url= 'https://opendata.arcgis.com/datasets/83fc2e72903343aabff6de8cb445b81c_2.geojson'

    geofile = get_geofile(url)
    
    #transformation
    data = set_feature( data )

    overview_data( data )

    portifolio_density( data,geofile )
    
    commercial( data )

    attributes_distribuition(data)




