import streamlit as st
import pandas as pd

from calculation import calculate_macros
from database import (
    create_tables,
    add_workout,
    add_food,
    get_connection
)
# =========================
# WORKOUT TRACKER
# =========================


st.header("🏋️ Workout Tracker")

workout_date = st.date_input(
    "Workout Date"
)

exercise = st.text_input(
    "Exercise"
)

col1, col2, col3 = st.columns(3)

with col1:

    sets = st.number_input(
        "Sets",
        min_value=1,
        value=3
    )

with col2:

    reps = st.number_input(
        "Reps",
        min_value=1,
        value=10
    )

with col3:

    workout_weight = st.number_input(
        "Weight (kg)",
        min_value=0.0,
        value=10.0
    )

if st.button("Add Workout"):

    add_workout(
        str(workout_date),
        exercise,
        sets,
        reps,
        workout_weight
    )

    st.success("Workout added!")

conn = get_connection()

workouts = pd.read_sql(
    "SELECT * FROM workouts ORDER BY date DESC",
    conn
)

conn.close()

if not workouts.empty:

    workouts["Volume"] = (
        workouts["sets"]
        * workouts["reps"]
        * workouts["weight"]
    )

    st.subheader("Workout History")

    st.dataframe(
        workouts,
        use_container_width=True
    )