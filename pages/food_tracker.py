# =========================
# FOOD TRACKER
# =========================
import streamlit as st
import pandas as pd

from calculation import calculate_macros
from database import (
    create_tables,
    add_workout,
    add_food,
    get_connection
)

st.header("🍛 Food Tracker")

food_date = st.date_input(
    "Food Date"
)

food = st.text_input(
    "Food Name"
)

quantity = st.number_input(
    "Quantity (g/ml)",
    min_value=0.0
)

col1, col2 = st.columns(2)

with col1:

    calories = st.number_input(
        "Calories",
        min_value=0.0
    )

    protein = st.number_input(
        "Protein (g)",
        min_value=0.0
    )

with col2:

    carbs = st.number_input(
        "Carbs (g)",
        min_value=0.0
    )

    fat = st.number_input(
        "Fat (g)",
        min_value=0.0
    )

if st.button("Add Food"):

    add_food(
        str(food_date),
        food,
        quantity,
        calories,
        protein,
        carbs,
        fat
    )

    st.success("Food added!")

conn = get_connection()

foods = pd.read_sql(
    "SELECT * FROM foods ORDER BY date DESC",
    conn
)

conn.close()

if not foods.empty:

    st.subheader("Food History")

    st.dataframe(
        foods,
        use_container_width=True
    )

    st.subheader("Total Nutrition")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Calories",
        f"{foods['calories'].sum():.0f}"
    )

    c2.metric(
        "Protein",
        f"{foods['protein'].sum():.1f} g"
    )

    c3.metric(
        "Carbs",
        f"{foods['carbs'].sum():.1f} g"
    )

    c4.metric(
        "Fat",
        f"{foods['fat'].sum():.1f} g"
    )