#%%
import os
from datetime import timedelta
from turtle import width

import altair as alt
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st
from dotenv import load_dotenv
from sqlalchemy import create_engine

#%%
load_dotenv()

POSTGRES_CONNECTION_STRING = os.environ["POSTGRES_CONNECTION_STRING"]
engine = create_engine(POSTGRES_CONNECTION_STRING)
#%% number of reviews per day over Amsterdam, Rotterdam and Groningen


# @st.cache
def get_data_review(connection):
    engine = create_engine(connection)
    df = pd.read_sql_query(
        """
        select date(rev.datetime) as datum, rest.location_city as stadsnaam, count(rest.location_city) as aantal_reviews from reviews rev
        inner join restaurants rest
        on rev.restaurant_id =rest.restaurant_id
        where datetime between '2021-12-31' and '2022-12-31'
        and rest.location_city in ('Amsterdam', 'Rotterdam', 'Groningen')
        group by date(rev.datetime), rest.location_city
        """,
        con=engine,
    )
    return df


df = get_data_review(POSTGRES_CONNECTION_STRING)


#%%
# @st.cache
def get_covid_date(connection):
    engine = create_engine(connection)
    dfcovid = pd.read_sql_query(
        """
        select date(mtd.date_of_publication) as datum, mtd.municipality_name as stadsnaam, count(mtd.municipality_name), mtd.total_reported as covid_infecties
        from covid.municipality_totals_daily mtd
        where date(mtd.date_of_publication) between '2022-01-01' and '2022-12-31'
        and mtd.municipality_name in ('Amsterdam', 'Rotterdam', 'Groningen')
        group by date(mtd.date_of_publication), mtd.municipality_name, mtd.total_reported
        """,
        con=engine,
    )
    return dfcovid


dfcovid = get_covid_date(POSTGRES_CONNECTION_STRING)
# %%
st.title("Review gegevens over grote steden in Nederland")
st.write("### Het aantal reviews per stad gedurende het jaar 2022")
# %%
revs = alt.Chart(df).mark_line().encode(x="datum", y="aantal_reviews", color="stadsnaam")
st.altair_chart(revs, use_container_width=True)
# %%
from datetime import datetime

dfcovid["datum"] = pd.to_datetime(dfcovid["datum"])
st.write("### Het aantal covid-19 infecties per stad gedurende het jaar 2022")
dmin = dfcovid["datum"].dt.date.min()
dmax = dfcovid["datum"].dt.date.max()
# %%
dates = st.slider("Pick data", dmin, dmax, value=[dmin, dmax])
k = dfcovid.loc[((df["datum"] >= dates[0]) & (df["datum"] <= dates[-1]))]

# %%
fig = px.line(
    k,
    x="datum",
    y="covid_infecties",
    color="stadsnaam",
)
# covinf = plt.Chart(k).mark_line().encode(x="datum", y="covid_infecties", color="stadsnaam")

st.plotly_chart(fig, use_container_width=True)
# %%
