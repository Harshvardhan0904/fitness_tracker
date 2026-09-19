import streamlit as st
from calculation import calculate_macros
st.set_page_config(
    page_title="Fitness Tracker",
    page_icon="💪",
    layout="wide"
)

st.title("💪 Fitness & Nutrition Tracker")

selected_page = st.segmented_control(
    "Navigation",
    options=[
        "🧮 Calculator",
        "🏋️ Workout Tracker",
        "🍛 Food Tracker",
        "📊 Analytics"
    ],
    default="🧮 Calculator",
    label_visibility="collapsed"
)

if selected_page == "🏋️ Workout Tracker":
    st.switch_page("pages/workout_tracker.py")

elif selected_page == "🍛 Food Tracker":
    st.switch_page("pages/food_tracker.py")

elif selected_page == "📊 Analytics":
    st.switch_page("pages/analytics.py")

# =========================
# CALCULATOR PAGE
# =========================

st.header("Calorie & Macro Calculator")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input(
        "Age",
        min_value=15,
        max_value=100,
        value=21
    )

    gender = st.selectbox(
        "Gender",
        ["Male", "Female"]
    )

    weight = st.number_input(
        "Weight (kg)",
        min_value=30.0,
        value=58.0
    )

with col2:
    height = st.number_input(
        "Height (cm)",
        min_value=100.0,
        value=170.0
    )

    activity_name = st.selectbox(
        "Activity Level",
        [
            "Sedentary",
            "Light",
            "Moderate",
            "Very Active",
            "Extra Active"
        ]
    )

    goal = st.selectbox(
        "Goal",
        ["Bulk", "Maintain", "Cut"]
    )

activity_levels = {
    "Sedentary": 1.2,
    "Light": 1.375,
    "Moderate": 1.55,
    "Very Active": 1.725,
    "Extra Active": 1.9
}

diet_preference = st.selectbox(
    "Diet Preference",
    [
        "Vegetarian",
        "Vegan",
        "Non-Vegetarian"
    ]
)

if st.button("Calculate", type="primary"):
    result = calculate_macros(
        weight,
        height,
        age,
        gender,
        activity_levels[activity_name],
        goal
    )

    st.divider()
    st.subheader("Your Daily Target")

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("🔥 Calories", f"{result['calories']} kcal")
    c2.metric("🥩 Protein", f"{result['protein']} g")
    c3.metric("🍚 Carbs", f"{result['carbs']} g")
    c4.metric("🥑 Fat", f"{result['fat']} g")

    st.write(f"BMR: **{result['bmr']} kcal**")
    st.write(f"Maintenance Calories: **{result['tdee']} kcal**")
    st.write(f"Diet Preference: **{diet_preference}**")