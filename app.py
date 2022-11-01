
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
          'Brighton',
          'Durham', ]

codes = {'---------': None, 'London': '5E87490', 'Glasgow': '5E550', 'Liverpool': '5E813', 'Manchester': '5E904',
         'Leeds': '5E787', 'Nottingham': '5E1019', 'Edinburgh': '5E475', 'Brighton': '5E61480', 'Durham': '5E460'}


@st.cache(ttl=24*60*60)
def get_uni_data():
    uni_df = pd.read_csv(
        'https://docs.google.com/spreadsheets/d/1j29ItCU8flgBlNG1U_mGNVikRTAHMJhhsloFnHpEMcU/export?gid=0&format=csv')
    uni_df['City'] = uni_df['City'].fillna(method='ffill')

    uni_df['Students / Active Listing (Avg)'] = uni_df['Students / Active Listing (Avg)'].fillna(
        method='ffill')

    uni_df['Active Listings'] = uni_df['Active Listings'].fillna(
        method='bfill')

    # uni_df['Number of Students'] = uni_df['Number of Students'].str.replace(
    #     ',', '').astype(float)
    return uni_df


uni_df = get_uni_data()


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
uni_df_city = uni_df[uni_df['City'] == city]

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


# student.com gauge
# if df.shape[0] != 0:
#     if 'demand' in df.columns:
#         demand = df['demand'].iloc[0]
#         demand_color = df['demand_color'].iloc[0]
#         fig = go.Figure(go.Indicator(
#             mode="gauge+number",
#             value=demand,
#             domain={'x': [0, 1], 'y': [0, 1]},
#             title={'text': "Demand"},
#             gauge={'bar': {'color': demand_color}, 'axis': {'range': [None, 100]}}))
#         st.plotly_chart(fig)


if df.shape[0] != 0:
    total_students = uni_df_city[uni_df_city['Univeristy Name']
                                 == 'Total:'].iloc[0]['Number of Students']

    total_students = int(total_students.replace(',', ''))
    demand = uni_df_city['Students / Active Listing (Avg)'].iloc[0]
    _, col1, col2, col3 = st.columns((0.07, 0.5, 0.5, 1))
    fig = go.Figure(go.Indicator(
        mode="number", value=total_students,  number={'font_size': 60}))
    fig.update_layout(height=200, width=300, title='Total Students')

    col1.plotly_chart(fig)

    fig = go.Figure(go.Indicator(
        mode="number", value=round(demand, 2),  number={'font_size': 60}))
    fig.update_layout(height=200, width=300,
                      title='Students / Active Listing (Avg)')

    col2.plotly_chart(fig)

    # fig = px.bar(uni_df_city, x="Number of Students",
    #              y="Univeristy Name", title="Number of Students in Universities")
    # fig.update_layout(template='simple_white', width=900)
    # col2.plotly_chart(fig)

    col3.dataframe(
        uni_df_city[['Univeristy Name', 'Number of Students']].reset_index(drop=True).dropna())


row4_1, _, row4_spacer2 = st.columns((1, 0.1, 1))
with row4_1:
    if df.shape[0] != 0:
        count = df['bed'].value_counts().reset_index().sort_values('index')
        count.columns = ['Rooms', 'Size']

        studio = None
        if 'studio' in count['Rooms'].values:
            studio = count[count['Rooms'] == 'studio']['Size'].iloc[0]

        count = count[~(count['Rooms'].isin(['studio', 'nan']))]
        count['Rooms'] = count['Rooms'].astype(int)
        count = count.sort_values('Rooms').reset_index(drop=True)
        if studio != None:
            count.loc[len(count.index)] = ['studio', studio]
        count['Rooms'] = count['Rooms'].astype('str')
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
    see_data3 = st.expander('You can click here to see the Listings MAP 👉')
    with see_data3:
        st.map(df.dropna(subset=['lat']), zoom=9)
