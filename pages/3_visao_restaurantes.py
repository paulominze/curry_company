# libraries
from haversine import haversine
import plotly.express as px
import plotly.graph_objects as go

# bibliotecas necessárias
import pandas as pd
import streamlit as st
from datetime import datetime
from PIL import Image
import folium
from streamlit_folium import folium_static
import numpy as np


# -------------------------
# Funções
# -------------------------
def avg_std_time_on_traffic(df1):
    ##st.markdown('##### Coluna 2')
    cols = ['City', 'Time_taken(min)', 'Road_traffic_density']
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time']))
    return fig

def avg_std_time_graph(df1):
    ## st.markdown('##### Coluna 1')
    df_aux = df1.loc[:, ['City', 'Time_taken(min)']].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']

    df_aux = df_aux.reset_index()

    fig = go.Figure()
    fig.add_trace(go.Bar(name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time'])))

    fig.update_layout(barmode='group')

    return fig

def avg_std_time_delivery(df1, festival, op):
    """
        Esta função calcula tempo médio do desvio padrão no tempo de entrega.
            Parâmetros:
                Input:
                    - df: Dataframe com os dados necessários para o cálculos
                    - op: Tipo de operação que precisa ser calculado
                    - 'avg_time': Calcula o tempo médio
                    - 'std_time': calcula o desvio padrão do tempo
                Output:
                    - df: Dataframe com 2 colunas e 1 linha.
         
    """
    df_aux = df1.loc[:, ['Time_taken(min)', 'Festival']].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux


def distance(df1, fig):
    if fig == False:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        
        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
                
        avg_distance = np.round(df1['distance'].mean(), 2)
        return avg_distance
    else:
        cols = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        
        df1['distance'] = df1.loc[:, cols].apply(lambda x: haversine( (x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)

        avg_distance = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        #avg_distance
        # pull is given as a fraction of the pie radius
        fig = go.Figure(data=[go.Pie(labels=avg_distance['City'], values=avg_distance['distance'], pull=[0, 0.1, 0])])
                
        return fig
    


def clean_code (df1):
    """ Esta função tem a responsabilidade de limpar o dataframe 

        Tipos de limpeza:
        1. Remoção dos dados NaN
        2. Mudança do tipo da coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação da coluna de datas
        5. Limpeza da coluna de tempo ( remoção do texto da variável numérica )

        Input: Dataframe
        Output: Dataframe
    
    """
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    
    linhas_vazias = df1['Road_traffic_density'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    
    linhas_vazias = df1['Time_taken(min)'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    
    linhas_vazias = df1['City'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    
    linhas_vazias = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    
    # Conversão de texto/categoria/string para números inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    
    # Conversão de texto/categoria/string para números decimais
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)
    
    # Conversão de texto para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format='%d-%m-%Y')
    
    # Remove as linhas da coluna multiple_deliveries que tenham o
    # conteúdo igual a 'NaN '
    linhas_selecionadas = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_selecionadas, : ].copy()
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)
    
    # Comando para remover o texto de números
    # df1 = df1.reset_index(drop=True)
    # for i in range(len(df1)):
       #df1.loc[i, 'ID'] = df1.loc[i, 'ID'].strip()
      # df1.loc[i, 'Time_taken(min)'] = re.findall(r'\d+', df1.loc[i, 'Time_taken(min)'])
    
    # Removendo os espaços dentro da string/texto/object
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()
    
    # 7. limpando a coluna de Time Taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

# importa dataset
df = pd.read_csv('dataset/train.csv')

# cleaning dataframe
df1 = clean_code(df)

# esse comando ocupa toda área da tela.
st.set_page_config(page_title="Marketplace - Visão Restaurantes", layout="wide")

# ========================================== #
# Barra Lateral
# ========================================== #
st.markdown('# Marketplace - Visão Restaurantes')

image_path = 'Logo.png'
image = Image.open(image_path)
st.sidebar.image(image, use_container_width=True)

#st.sidebar.markdown('# Curry Company')
#st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")


# Usando datetime para garantir que a data seja do tipo esperado
date_slider = st.sidebar.slider(
    'Até qual valor?',
    value=datetime(2022, 4, 13),  # Data no formato datetime
    min_value=datetime(2022, 2, 11),
    max_value=datetime(2022, 4, 6),
    format='DD-MM-YYYY'
)

st.sidebar.markdown("""---""")


traffic_options = st.sidebar.multiselect(
    'Quais as condições do trânsito?',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam']
)

st.sidebar.markdown("""---""")


weather_conditions_options = st.sidebar.multiselect(
    'Quais as condições climáticas?',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy']
)

st.sidebar.markdown("""---""")
st.sidebar.markdown('### Powered by Comunidade DS')

# Filtro de data
linhas_selecionadas = df1['Order_Date'] < date_slider
df1 = df1.loc[linhas_selecionadas, :]

# filtro de trânsito
linhas_selecionadas = df1['Road_traffic_density'].isin(traffic_options)
df1 = df1.loc[linhas_selecionadas, :]

#st.dataframe(df1)

# ========================================== #
# LAYOUT NO STREAMLIT
# ========================================== #
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.markdown('## Overal Metrics')
        
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            delivery_unique = len(df1.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores Únicos', delivery_unique)

        
        with col2:
            avg_distance = distance(df1, fig=False)    
            col2.metric('Distância Média', avg_distance)
            
            
        with col3:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'avg_time')
            col3.metric('Tempo Médio', df_aux)
                       
        with col4:
            df_aux = avg_std_time_delivery(df1, 'Yes', 'std_time')
            col4.metric('STD Entrega', df_aux)
                        
        with col5:
            df_aux = avg_std_time_delivery(df1, 'No', 'avg_time')
            col5.metric('Tempo Médio', df_aux)
                    
        with col6:
            df_aux = avg_std_time_delivery(df1, 'No', 'std_time')
            col6.metric('STD Entrega', df_aux)
            
    with st.container():
        st.markdown("""___""")
        st.markdown('## Tempo médio de entrega por cidade')        
        col1, col2 = st.columns(2)
        
        with col1:
            fig = avg_std_time_graph(df1)
            st.plotly_chart(fig)
            
        with col2:
            df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Road_traffic_density']].groupby(['City', 'Road_traffic_density']).agg({'Time_taken(min)': ['mean', 'std']})
            
            df_aux.columns = ['avg_time', 'std_time']
            
            df_aux = df_aux.reset_index()
            
            st.dataframe(df_aux)
        
        
    with st.container():
        st.markdown("""___""")
        st.markdown('## Ditribuição do tempo')
        
        col1, col2 = st.columns(2)
        with col1:
            fig = distance(df1, fig=True)
            st.plotly_chart(fig)

        with col2:            
            fig = avg_std_time_on_traffic(df1)
            st.plotly_chart(fig)
        