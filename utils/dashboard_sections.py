import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import numpy as np

from utils.constants import NUTRIENT_OPTIONS, VALUE_TRANSLATIONS

def kcal_vs_life_scatter(df, year, mode):
    st.subheader(f"Relació entre consum de nutrients i esperança de vida ({year})")

    nutrient_name = st.selectbox("Escull el nutrient a analitzar", list(NUTRIENT_OPTIONS.keys()))

    # Determinar columna a usar
    nutrient_column = NUTRIENT_OPTIONS[nutrient_name][0 if "Absolut" in mode else 1]

    # Filtrar dades pel rang d’anys
    scatter_df = df[df["Year"] == year]

    fig_nutrient = px.scatter(
        scatter_df,
        x=nutrient_column,
        y="LifeExpectancy",
        hover_name="Country",
        color='Country',
        trendline="ols",
        size="Calories_Total",
        labels=VALUE_TRANSLATIONS
    )

    st.plotly_chart(fig_nutrient, use_container_width=True)


def timeseries_country_plot(df, countries, mode):
    st.subheader(f"Evolució temporal de la dieta i salut en un país seleccionat")
    selected_country = st.selectbox("País", countries, index=countries.index("Spain") if "Spain" in countries else 0)
    country_df = df[df["Country"] == selected_country]

    nutrient_columns = [op[0 if "Absolut" in mode else 1] for op in NUTRIENT_OPTIONS.values()]

    fig_line_dual = go.Figure()

    # Calories (primer eix Y)
    colors = ["grey", "orange", "green", "red", "blue"]
    for i, nutrient in enumerate(nutrient_columns):
        fig_line_dual.add_trace(go.Scatter(
            x=country_df["Year"],
            y=country_df[nutrient],
            mode="lines+markers",
            name=VALUE_TRANSLATIONS[nutrient],
            yaxis="y1",
            line=dict(color=colors[i] if i < len(colors) else "grey")
        ))


    # Esperança de vida (segon eix Y)
    fig_line_dual.add_trace(go.Scatter(
        x=country_df["Year"],
        y=country_df["LifeExpectancy"],
        mode="lines+markers",
        name=VALUE_TRANSLATIONS["LifeExpectancy"],
        yaxis="y2",
        line=dict(color="black", dash="dot")
    ))

    # Configurar layout amb dos eixos
    fig_line_dual.update_layout(
        yaxis=dict(
            title="Calories (kcal)" if "Absolut" in mode else "Calories (%)",
            tickfont=dict(color="grey")
        ),
        yaxis2=dict(
            title="Esperança de vida (anys)",
            tickfont=dict(color="black"),
            overlaying="y",
            side="right"
        ),
        xaxis=dict(title="Any"),
        legend=dict(orientation="h"),
        margin=dict(l=40, r=40, t=40, b=40)
    )

    st.plotly_chart(fig_line_dual, use_container_width=True)


def world_map_plot(df, year):
    st.subheader(f"Mapa mundial d’esperança de vida ({year})")
    map_df = df[df["Year"] == year]
    fig3 = px.choropleth(
        map_df,
        locations="Code",
        color="LifeExpectancy",
        hover_name="Country",
        color_continuous_scale="Blues",
        labels={"LifeExpectancy": "Esperança de vida"}
    )
    st.plotly_chart(fig3, use_container_width=True)


def correlation_heatmap(df, year):
    st.subheader(f"Mapa de calor de correlacions ({year})")
    corr_df = df[df["Year"] == year]

    # Matriu de correlació
    corr_matrix = corr_df[[
        "LifeExpectancy", 
        "Calories_Animal_Protein", 
        "Calories_Vegetal_Protein", 
        "Calories_Fat", 
        "Calories_Carbs"
    ]].corr()

    fig_corr = ff.create_annotated_heatmap(
        z=np.round(corr_matrix.values, 2),
        x=corr_matrix.columns.tolist(),
        y=corr_matrix.index.tolist(),
        colorscale="RdBu",
        showscale=True,
        reversescale=True
    )

    st.plotly_chart(fig_corr, use_container_width=True)

def barplot(df, year, countries, mode):
    st.subheader(f"Comparativa de calories vs. mitjana mundial ({year})")

    selected_countries = st.multiselect(
        "Selecciona països per comparar",
        sorted(countries),
        default=["Spain", "Japan", "United States"]
    )
    nutrient_columns = [op[2 if "Absolut" in mode else 3] for op in NUTRIENT_OPTIONS.values()]

    # Filtrar dades
    bar_data = df[
        (df["Year"] == year) &
        (df["Country"].isin(selected_countries))
    ]

    # Selecció de columnes i canvi de nom per llegibilitat
    bar_df = bar_data[["Country"] + nutrient_columns].rename(columns={
        col: VALUE_TRANSLATIONS[col] for col in nutrient_columns})

    # Convertir a format llarg
    bar_df = bar_df.melt(id_vars="Country", var_name="Macronutrient", value_name="Desviacio")

    # Gràfic de barres
    fig_bar = px.bar(
        bar_df,
        x="Macronutrient",
        y="Desviacio",
        color="Country",
        barmode="group"
    )

    fig_bar.update_layout(yaxis_title="Diferència", xaxis_title="Macronutrient")

    st.plotly_chart(fig_bar, use_container_width=True)