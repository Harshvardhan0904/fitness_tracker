import os

import pandas as pd
import streamlit as st
from dotenv import load_dotenv

from food_analyzer import analyze_food_image
from database import add_food, get_connection
from database import (
    create_tables,
    add_food,
    get_connection
)
from database import (
    create_tables,
    add_food,
    get_connection
)

load_dotenv()

api_key = os.getenv("API_KEY")

model_name = "qwen/qwen3.8-27b"

create_tables()

# Streamlit Cloud fallback
if not api_key:
    api_key = st.secrets.get("GROQ_API_KEY")

model_name = os.getenv("GROQ_MODEL")

if not model_name:
    model_name = st.secrets.get(
        "GROQ_MODEL",
        "qwen/qwen3.8-27b"
    )

if not api_key:
    st.error("Groq API key is not configured.")
    st.stop()

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

st.header("📷 AI Food Photo Analysis")

uploaded_image = st.file_uploader(
    "Upload your food photo",
    type=["jpg", "jpeg", "png", "webp"]
)

meal_details = st.text_area(
    "Optional details",
    placeholder=(
        "Example: 2 rotis, homemade dal, approximately "
        "1 tablespoon oil used, one medium bowl."
    )
)

if uploaded_image is not None:

    st.image(
        uploaded_image,
        caption="Uploaded meal",
        width=450
    )

    if st.button(
        "✨ Analyse Food",
        type="primary"
    ):

        if not api_key:
            st.error(
                "API_KEY was not found in the .env file."
            )
            st.stop()

        try:
            with st.spinner(
                "Groq AI meal analyse कर रहा है..."
            ):

                result = analyze_food_image(
                    image_bytes=uploaded_image.getvalue(),
                    mime_type=uploaded_image.type,
                    api_key=api_key,
                    model_name=model_name,
                    user_details=meal_details
                )

                st.session_state["food_ai_result"] = result

            st.success("Food analysis completed!")

        except Exception as error:
            st.error(
                f"Food analysis failed: {error}"
            )


# =========================
# DISPLAY AI RESULT
# =========================

if "food_ai_result" in st.session_state:

    result = st.session_state["food_ai_result"]
    total = result["total"]

    st.subheader(result["meal_name"])

    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "🔥 Calories",
        f"{total['calories']:.0f} kcal"
    )

    c2.metric(
        "🥩 Protein",
        f"{total['protein_g']:.1f} g"
    )

    c3.metric(
        "🍚 Carbs",
        f"{total['carbs_g']:.1f} g"
    )

    c4.metric(
        "🥑 Fat",
        f"{total['fat_g']:.1f} g"
    )

    st.write(
        f"AI confidence: **{result['overall_confidence']}**"
    )

    items_df = pd.DataFrame(result["items"])

    edited_items = st.data_editor(
        items_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "food_name": st.column_config.TextColumn(
                "Food"
            ),
            "estimated_quantity": st.column_config.TextColumn(
                "Estimated Quantity"
            ),
            "calories": st.column_config.NumberColumn(
                "Calories",
                min_value=0.0
            ),
            "protein_g": st.column_config.NumberColumn(
                "Protein (g)",
                min_value=0.0
            ),
            "carbs_g": st.column_config.NumberColumn(
                "Carbs (g)",
                min_value=0.0
            ),
            "fat_g": st.column_config.NumberColumn(
                "Fat (g)",
                min_value=0.0
            )
        }
    )

    # Recalculate after user corrections
    corrected_calories = edited_items["calories"].sum()
    corrected_protein = edited_items["protein_g"].sum()
    corrected_carbs = edited_items["carbs_g"].sum()
    corrected_fat = edited_items["fat_g"].sum()

    st.subheader("Corrected Total")

    r1, r2, r3, r4 = st.columns(4)

    r1.metric(
        "Calories",
        f"{corrected_calories:.0f} kcal"
    )

    r2.metric(
        "Protein",
        f"{corrected_protein:.1f} g"
    )

    r3.metric(
        "Carbs",
        f"{corrected_carbs:.1f} g"
    )

    r4.metric(
        "Fat",
        f"{corrected_fat:.1f} g"
    )

    with st.expander("AI assumptions"):
        for item in result["items"]:
            st.write(
                f"**{item['food_name']}:** "
                f"{item['assumptions']}"
            )

    st.warning(
        "This is only a visual estimate. Hidden oil, sugar, "
        "butter and exact serving weight can cause a large difference."
    )