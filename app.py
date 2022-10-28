
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(layout="wide")

cities = ['---------', 'Glasgow',
          'Liverpool',
          'Manchester',
          'Leeds',
          'Nottingham',
          'London',
          'Edinburgh',
          'Bristol',
          'Durham', ]

codes = {'---------': None, 'London': '5E87490', 'Glasgow': '5E550', 'Liverpool': '5E813', 'Manchester': '5E904',
         'Leeds': '5E787', 'Nottingham': '5E1019', 'Edinburgh': '5E475', 'Bristol': '5E219', 'Durham': '5E460'}


@st.cache(ttl=24*60*60)
def get_data(city, city_name):
    if city == None:
        return pd.DataFrame(), None

    df = pd.read_csv('data/'+city_name+'.csv')
    nres = df['nres'].astype(int).iloc[0]
    df['bed'] = df['bed'].astype(str)
    symbols = ['>', '<', '"', "'", ',', '(', ')']

    for symbol in symbols:
        try:
            df['sq_ft'] = df['sq_ft'].str.replace(symbol, '')
        except:
            pass

    df['sq_ft'] = pd.to_numeric(df['sq_ft'], errors='coerce')
    return df, nres


st.header('Student Rental Analysis')

styl = """
<style>
.plot-container{
  box-shadow: 4px 4px 8px 4px rgba(0,0,0,0.2);
  transition: 0.3s;

}
</styl>
"""
st.markdown(styl, unsafe_allow_html=True)
city = st.selectbox(
    "Please select City", cities, key='city', index=0)
df, nres = get_data(codes[city], city)


if df.shape[0] != 0:
    _, col1, col2, col3, col4 = st.columns((0.1, 1, 1, 1, 1))

    # col1.metric(label="Average Weekly Rate", value='£ ' + str(
    #     round(df['price_weekly'].mean(), 2)))

    fig = go.Figure(go.Indicator(
        mode="number", value=nres,  number={'font_size': 60}))
    fig.update_layout(height=200, width=300, title='Total Listings')

    col1.plotly_chart(fig)

    fig = go.Figure(go.Indicator(
        mode="number", value=round(df['price_weekly'].mean(), 2),  number={'prefix': "£", 'font_size': 60}))
    fig.update_layout(height=200, width=300, title='Average Weekly Rate')

    col2.plotly_chart(fig)

    fig = go.Figure(go.Indicator(
        mode="number", value=round(df['price'].mean() * 12, 2),  number={'prefix': "£", 'font_size': 60}))
    fig.update_layout(height=200, width=300, title='Average Annual Revenue')

    col3.plotly_chart(fig)

    sq = df[~(df['sq_ft'].isna())]
    rent_per_sq = (sq['price'] / sq['sq_ft']).mean()

    if str(rent_per_sq).lower() == 'nan' or str(rent_per_sq).lower() == 0:
        pass
    else:
        fig = go.Figure(go.Indicator(mode="number", value=round(
            rent_per_sq, 2),  number={'prefix': "£", 'font_size': 60}))
        fig.update_layout(height=200, width=300, title='Rent per Sq ft.')

        col4.plotly_chart(fig)

    # col2.metric(label="Average Annual Revenue", value='£ ' + str(
    #     round(df['price'].mean() * 12, 2)))

row4_1, _, row4_spacer2 = st.columns((1, 0.1, 1))
with row4_1:
    if df.shape[0] != 0:
        count = df['bed'].value_counts().reset_index().sort_values('index')
        count.columns = ['Rooms', 'Size']
        fig = px.bar(count, y="Rooms", x="Size",
                     color="Rooms", title="Rental Size")
        fig.update_layout(template='simple_white')
        row4_1.plotly_chart(fig)
        count = df['type'].value_counts().reset_index()
        count.columns = ['type', 'count']
        fig = px.pie(count, values='count', names='type',
                     title='Rental Type')
        fig.update_layout(template='simple_white')
        row4_spacer2.plotly_chart(fig, use_container_width=True)


if df.shape[0] != 0:
    see_data3 = st.expander('You can click here to see the MAP 👉')
    with see_data3:
        st.map(df.dropna(subset=['lat']), zoom=9)
