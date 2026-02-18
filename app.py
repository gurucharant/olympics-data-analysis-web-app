import streamlit as st
import pandas as pd
from pathlib import Path
import urllib.request

import preprocessor
import helper

import plotly.express as px
import matplotlib.pyplot as plt
import seaborn as sns


# -----------------------------
# Hugging Face dataset links (your links)
# -----------------------------
ATHLETE_URL = "https://huggingface.co/datasets/urwithgc/olympics-data/resolve/main/athlete_events.csv"
REGION_URL = "https://huggingface.co/datasets/urwithgc/olympics-data/resolve/main/noc_regions.csv"


# -----------------------------
# Robust data download + caching
# -----------------------------
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

ATHLETE_PATH = DATA_DIR / "athlete_events.csv"
REGION_PATH = DATA_DIR / "noc_regions.csv"


def download_if_missing(url: str, path: Path) -> None:
    if not path.exists():
        with st.spinner(f"Downloading {path.name}... (first run only)"):
            urllib.request.urlretrieve(url, path)


@st.cache_data(show_spinner=False)
def load_data() -> pd.DataFrame:
    download_if_missing(ATHLETE_URL, ATHLETE_PATH)
    download_if_missing(REGION_URL, REGION_PATH)

    df_raw = pd.read_csv(ATHLETE_PATH)
    region_df = pd.read_csv(REGION_PATH)

    df = preprocessor.preprocess(df_raw, region_df)
    return df


df = load_data()


# -----------------------------
# Sidebar
# -----------------------------
st.sidebar.title("Olympics Analysis")

# Optional logo if you have it in repo
local_logo_png = BASE_DIR / "Olympic_rings_without_rims.png"
if local_logo_png.exists():
    st.sidebar.image(str(local_logo_png))
else:
    st.sidebar.write("🏅 Olympics Dashboard")

user_menu = st.sidebar.radio(
    "Select an Option",
    ("Medal Tally", "Overall Analysis", "Country-wise Analysis", "Athlete wise Analysis"),
)


# -----------------------------
# Medal Tally
# -----------------------------
if user_menu == "Medal Tally":
    st.sidebar.header("Medal Tally")
    years, country = helper.country_year_list(df)

    selected_year = st.sidebar.selectbox("Select Year", years)
    selected_country = st.sidebar.selectbox("Select Country", country)

    medal_tally = helper.fetch_medal_tally(df, selected_year, selected_country)

    if selected_year == "Overall" and selected_country == "Overall":
        st.title("Overall Tally")
    elif selected_year != "Overall" and selected_country == "Overall":
        st.title(f"Medal Tally in {selected_year} Olympics")
    elif selected_year == "Overall" and selected_country != "Overall":
        st.title(f"{selected_country} overall performance")
    else:
        st.title(f"{selected_country} performance in {selected_year} Olympics")

    st.dataframe(medal_tally, use_container_width=True)


# -----------------------------
# Overall Analysis
# -----------------------------
if user_menu == "Overall Analysis":
    editions = df["Year"].nunique()
    cities = df["City"].nunique()
    sports = df["Sport"].nunique()
    events = df["Event"].nunique()
    athletes = df["Name"].nunique()
    nations = df["region"].nunique()

    st.title("Top Statistics")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Editions")
        st.title(editions)
    with col2:
        st.header("Hosts")
        st.title(cities)
    with col3:
        st.header("Sports")
        st.title(sports)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.header("Events")
        st.title(events)
    with col2:
        st.header("Nations")
        st.title(nations)
    with col3:
        st.header("Athletes")
        st.title(athletes)

    nations_over_time = helper.data_over_time(df, "region")
    st.title("Participating Nations over the years")
    st.plotly_chart(px.line(nations_over_time, x="Edition", y="Count"), use_container_width=True)

    events_over_time = helper.data_over_time(df, "Event")
    st.title("Events over the years")
    st.plotly_chart(px.line(events_over_time, x="Edition", y="Count"), use_container_width=True)

    athlete_over_time = helper.data_over_time(df, "Name")
    st.title("Athletes over the years")
    st.plotly_chart(px.line(athlete_over_time, x="Edition", y="Count"), use_container_width=True)

    st.title("No. of Events over time (Every Sport)")
    fig, ax = plt.subplots(figsize=(20, 20))
    x = df.drop_duplicates(["Year", "Sport", "Event"])
    pt = x.pivot_table(index="Sport", columns="Year", values="Event", aggfunc="count").fillna(0).astype(int)
    sns.heatmap(pt, annot=False, ax=ax)
    st.pyplot(fig)

    st.title("Most successful Athletes")
    sport_list = sorted(df["Sport"].dropna().unique().tolist())
    sport_list.insert(0, "Overall")

    selected_sport = st.selectbox("Select a Sport", sport_list)
    top_athletes = helper.most_successful(df, selected_sport)
    st.dataframe(top_athletes, use_container_width=True)


# -----------------------------
# Country-wise Analysis
# -----------------------------
if user_menu == "Country-wise Analysis":
    st.sidebar.title("Country-wise Analysis")

    country_list = sorted(df["region"].dropna().unique().tolist())
    selected_country = st.sidebar.selectbox("Select a Country", country_list)

    country_df = helper.yearwise_medal_tally(df, selected_country)
    st.title(f"{selected_country} Medal Tally over the years")
    st.plotly_chart(px.line(country_df, x="Year", y="Medal"), use_container_width=True)

    st.title(f"{selected_country} excels in the following sports")
    pt = helper.country_event_heatmap(df, selected_country)
    fig, ax = plt.subplots(figsize=(20, 20))
    sns.heatmap(pt, annot=False, ax=ax)
    st.pyplot(fig)

    st.title(f"Top 10 athletes of {selected_country}")
    top10_df = helper.most_successful_countrywise(df, selected_country)
    st.dataframe(top10_df, use_container_width=True)


# -----------------------------
# Athlete wise Analysis
# -----------------------------
if user_menu == "Athlete wise Analysis":
    athlete_df = df.drop_duplicates(subset=["Name", "region"]).copy()

    # ---- No scipy needed: use plotly express histogram
    st.title("Distribution of Age (Overall vs Medalists)")
    temp = athlete_df.dropna(subset=["Age"]).copy()
    temp["MedalType"] = temp["Medal"].fillna("No Medal")
    temp = temp[temp["MedalType"].isin(["Gold", "Silver", "Bronze", "No Medal"])]

    fig = px.histogram(temp, x="Age", color="MedalType", nbins=30, barmode="overlay")
    st.plotly_chart(fig, use_container_width=True)

    st.title("Height Vs Weight")
    sport_list = sorted(df["Sport"].dropna().unique().tolist())
    sport_list.insert(0, "Overall")
    selected_sport = st.selectbox("Select a Sport", sport_list)

    temp_df = helper.weight_v_height(df, selected_sport)

    fig, ax = plt.subplots()
    sns.scatterplot(
        data=temp_df,
        x="Weight",
        y="Height",
        hue="Medal",
        style="Sex",
        s=60,
        ax=ax
    )
    st.pyplot(fig)

    st.title("Men Vs Women Participation Over the Years")
    final = helper.men_vs_women(df)
    fig = px.line(final, x="Year", y=["Male", "Female"])
    st.plotly_chart(fig, use_container_width=True)
