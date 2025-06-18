import streamlit as st
import pandas as pd

from utils.dashboard_sections import (
    kcal_vs_life_scatter, timeseries_country_plot, world_map_plot, correlation_heatmap, barplot)


# Carrega les dades
@st.cache_data
def load_data():
    life_df = pd.read_csv("data/life-expectancy.csv")
    diet_df = pd.read_csv("data/daily-caloric-supply-derived-from-carbohydrates-protein-and-fat.csv")

    # Canviem el nom de les columnes per fer-les més manejables
    life_df.rename(columns={
        "Entity": "Country",
        "Period life expectancy at birth - Sex: total - Age: 0": "LifeExpectancy"
    }, inplace=True)

    diet_df.rename(columns={
        "Entity": "Country",
        "Daily calorie supply per person that comes from animal protein": "Calories_Animal_Protein",
        "Daily calorie supply per person that comes from vegetal protein": "Calories_Vegetal_Protein",
        "Daily calorie supply per person from fat": "Calories_Fat",
        "Daily calorie supply per person from carbohydrates": "Calories_Carbs"
    }, inplace=True)

    # Fem merge per Country, Code i Year
    merged_df = pd.merge(life_df, diet_df, on=["Country", "Code", "Year"], how="inner")

    # Convertim LifeExpectancy a número
    merged_df["LifeExpectancy"] = pd.to_numeric(merged_df["LifeExpectancy"], errors="coerce")

    # Calories totals
    merged_df["Calories_Total"] = (
        merged_df["Calories_Animal_Protein"] +
        merged_df["Calories_Vegetal_Protein"] +
        merged_df["Calories_Fat"] +
        merged_df["Calories_Carbs"]
    )

    # Calculem els percentatges respecte al total
    merged_df["Perc_Animal_Protein"] = merged_df["Calories_Animal_Protein"] / merged_df["Calories_Total"] * 100
    merged_df["Perc_Vegetal_Protein"] = merged_df["Calories_Vegetal_Protein"] / merged_df["Calories_Total"] * 100
    merged_df["Perc_Fat"] = merged_df["Calories_Fat"] / merged_df["Calories_Total"] * 100
    merged_df["Perc_Carbs"] = merged_df["Calories_Carbs"] / merged_df["Calories_Total"] * 100

    global_means = merged_df.groupby("Year")[[
        "Calories_Animal_Protein",
        "Calories_Vegetal_Protein",
        "Calories_Fat",
        "Calories_Carbs",
        "Perc_Animal_Protein",
        "Perc_Vegetal_Protein",
        "Perc_Fat",
        "Perc_Carbs"
    ]].mean().reset_index()

    # Fem merge per tenir la mitjana global de cada any al costat de cada país
    merged_df = pd.merge(merged_df, global_means, on="Year", suffixes=("", "_GlobalAvg"))

    # Calcular diferències absolutes
    merged_df["Diff_Cal_Animal_Protein"] = merged_df["Calories_Animal_Protein"] - merged_df["Calories_Animal_Protein_GlobalAvg"]
    merged_df["Diff_Cal_Vegetal_Protein"] = merged_df["Calories_Vegetal_Protein"] - merged_df["Calories_Vegetal_Protein_GlobalAvg"]
    merged_df["Diff_Cal_Fat"] = merged_df["Calories_Fat"] - merged_df["Calories_Fat_GlobalAvg"]
    merged_df["Diff_Cal_Carbs"] = merged_df["Calories_Carbs"] - merged_df["Calories_Carbs_GlobalAvg"]

    # Calcular diferències relatives (en %)
    merged_df["Diff_Perc_Animal_Protein"] = merged_df["Perc_Animal_Protein"] - merged_df["Perc_Animal_Protein_GlobalAvg"]
    merged_df["Diff_Perc_Vegetal_Protein"] = merged_df["Perc_Vegetal_Protein"] - merged_df["Perc_Vegetal_Protein_GlobalAvg"]
    merged_df["Diff_Perc_Fat"] = merged_df["Perc_Fat"] - merged_df["Perc_Fat_GlobalAvg"]
    merged_df["Diff_Perc_Carbs"] = merged_df["Perc_Carbs"] - merged_df["Perc_Carbs_GlobalAvg"]
    
    # Eliminem files amb valors nuls
    return merged_df.dropna()

df = load_data()

# Streamlit app setup
st.title("🍽️ Dieta i Esperança de Vida")
st.markdown("""
Aquest dashboard interactiu et permet explorar la relació entre els hàbits alimentaris i l’esperança de vida a escala mundial.
""")
st.sidebar.header("🎛️ Filtres")

# Variables globals
YEARS = df["Year"].sort_values(ascending=False).unique()
COUNTRIES = sorted(df["Country"].unique())
SELECTED_YEAR = st.sidebar.selectbox(
    "Selecciona un any",
    YEARS,
    index=0  # valor inicial
)
VALUE_TYPE = st.sidebar.radio("Mode de visualització", ["Absolut (kcal)", "Relatiu (%)"], horizontal=True)
#selected_range = st.slider("Interval d'anys", min_value=min_year, max_value=max_year, value=int(df["Year"].max()))

kcal_vs_life_scatter(df, SELECTED_YEAR, VALUE_TYPE)

# 📊 LÍNIA: Evolució al país seleccionat
timeseries_country_plot(df, COUNTRIES, VALUE_TYPE)

# 🗺️ MAPA: Esperança de vida mundial
world_map_plot(df, SELECTED_YEAR)

# Heatmap
correlation_heatmap(df, SELECTED_YEAR)

# Gràfic comparatiu nutricional entre països
barplot(df, SELECTED_YEAR, COUNTRIES, VALUE_TYPE)

# 📌 Footer
st.markdown("Dades de [Our World in Data](https://ourworldindata.org/)")
