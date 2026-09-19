import streamlit as st
import pandas as pd

from database import get_connection


st.set_page_config(
    page_title="Workout Analytics",
    page_icon="📊",
    layout="wide",
)

st.title("📊 Workout Analytics")

REQUIRED_COLUMNS = {"date", "exercise", "sets", "reps", "weight"}
COLUMN_ALIASES = {
    "workout_date": "date",
    "exercise_name": "exercise",
    "set": "sets",
    "repetition": "reps",
    "repetitions": "reps",
    "weight_kg": "weight",
    "weight_(kg)": "weight",
}


@st.cache_data(ttl=30)
def load_sqlite_data():
    connection = get_connection()
    try:
        return pd.read_sql_query("SELECT * FROM workouts ORDER BY date", connection)
    finally:
        connection.close()


def load_uploaded_data(uploaded_file):
    filename = uploaded_file.name.lower()

    if filename.endswith(".csv"):
        return pd.read_csv(uploaded_file)

    if filename.endswith((".xlsx", ".xls")):
        return pd.read_excel(uploaded_file, sheet_name=0)

    raise ValueError("Only CSV, XLSX and XLS files are supported.")


def prepare_data(dataframe):
    df = dataframe.copy()

    df.columns = (
        df.columns.astype(str)
        .str.strip()
        .str.lower()
        .str.replace(" ", "_", regex=False)
    )
    df = df.rename(columns=COLUMN_ALIASES)

    missing_columns = REQUIRED_COLUMNS.difference(df.columns)
    if missing_columns:
        missing_text = ", ".join(sorted(missing_columns))
        raise ValueError(f"Missing required columns: {missing_text}")

    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df["exercise"] = df["exercise"].astype(str).str.strip()

    for column in ["sets", "reps", "weight"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")

    df = df.dropna(
        subset=["date", "exercise", "sets", "reps", "weight"]
    )

    df = df[
        (df["sets"] > 0)
        & (df["reps"] > 0)
        & (df["weight"] >= 0)
    ].copy()

    df["total_reps"] = df["sets"] * df["reps"]
    df["volume"] = df["sets"] * df["reps"] * df["weight"]

    return df.sort_values("date")


source = st.radio(
    "Data Source",
    options=["SQLite Database", "Upload Excel / CSV"],
    horizontal=True,
)

raw_df = None

if source == "SQLite Database":
    try:
        raw_df = load_sqlite_data()
        st.caption("Showing workouts stored in the application database.")
    except Exception as error:
        st.error(f"SQLite data could not be loaded: {error}")
        st.stop()

else:
    uploaded_file = st.file_uploader(
        "Upload workout data",
        type=["xlsx", "xls", "csv"],
        help="Required columns: date, exercise, sets, reps and weight",
    )

    if uploaded_file is None:
        st.info("Upload an Excel or CSV file to open its analytics.")
        st.stop()

    try:
        raw_df = load_uploaded_data(uploaded_file)
        st.success(f"Loaded {uploaded_file.name}")
    except Exception as error:
        st.error(f"The uploaded file could not be read: {error}")
        st.stop()


try:
    workout_df = prepare_data(raw_df)
except ValueError as error:
    st.error(str(error))
    st.code("date, exercise, sets, reps, weight")
    st.stop()

if workout_df.empty:
    st.warning("No valid workout rows were found.")
    st.stop()


st.divider()

filter_col1, filter_col2, filter_col3 = st.columns([1, 1.5, 2])

with filter_col1:
    time_view = st.segmented_control(
        "Group results by",
        options=["Day", "Week", "Month"],
        default="Week",
    )

with filter_col2:
    exercise_options = sorted(workout_df["exercise"].unique().tolist())
    selected_exercise = st.selectbox(
        "Exercise",
        options=["All Exercises"] + exercise_options,
    )

with filter_col3:
    minimum_date = workout_df["date"].min().date()
    maximum_date = workout_df["date"].max().date()
    date_range = st.date_input(
        "Date range",
        value=(minimum_date, maximum_date),
        min_value=minimum_date,
        max_value=maximum_date,
    )


filtered_df = workout_df.copy()

if selected_exercise != "All Exercises":
    filtered_df = filtered_df[
        filtered_df["exercise"] == selected_exercise
    ]

if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
    start_date = pd.Timestamp(date_range[0])
    end_date = pd.Timestamp(date_range[1]) + pd.Timedelta(days=1)
    filtered_df = filtered_df[
        (filtered_df["date"] >= start_date)
        & (filtered_df["date"] < end_date)
    ]

if filtered_df.empty:
    st.warning("No workout data matches the selected filters.")
    st.stop()


if time_view == "Day":
    filtered_df["period"] = filtered_df["date"].dt.normalize()
elif time_view == "Week":
    filtered_df["period"] = (
        filtered_df["date"].dt.to_period("W").dt.start_time
    )
else:
    filtered_df["period"] = (
        filtered_df["date"].dt.to_period("M").dt.start_time
    )


summary_df = (
    filtered_df.groupby("period", as_index=False)
    .agg(
        total_sets=("sets", "sum"),
        total_reps=("total_reps", "sum"),
        average_weight=("weight", "mean"),
        maximum_weight=("weight", "max"),
        total_volume=("volume", "sum"),
        workout_entries=("exercise", "count"),
    )
    .sort_values("period")
)


st.subheader("Performance Summary")

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("🏋️ Total Sets", f"{filtered_df['sets'].sum():,.0f}")
m2.metric("🔁 Total Reps", f"{filtered_df['total_reps'].sum():,.0f}")
m3.metric("⚖️ Average Weight", f"{filtered_df['weight'].mean():,.1f} kg")
m4.metric("🏆 Best Weight", f"{filtered_df['weight'].max():,.1f} kg")
m5.metric("📦 Total Volume", f"{filtered_df['volume'].sum():,.0f} kg")


st.divider()
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    st.subheader("Weight Trend")
    st.line_chart(
        summary_df.set_index("period")[["average_weight", "maximum_weight"]],
        x_label=time_view,
        y_label="Weight (kg)",
    )

with chart_col2:
    st.subheader("Repetition Trend")
    st.line_chart(
        summary_df.set_index("period")[["total_reps"]],
        x_label=time_view,
        y_label="Total repetitions",
    )


chart_col3, chart_col4 = st.columns(2)

with chart_col3:
    st.subheader("Sets Trend")
    st.bar_chart(
        summary_df.set_index("period")[["total_sets"]],
        x_label=time_view,
        y_label="Total sets",
    )

with chart_col4:
    st.subheader("Training Volume Trend")
    st.line_chart(
        summary_df.set_index("period")[["total_volume"]],
        x_label=time_view,
        y_label="Volume (kg)",
    )


st.divider()
st.subheader("Exercise Comparison")

exercise_summary = (
    filtered_df.groupby("exercise", as_index=False)
    .agg(
        total_sets=("sets", "sum"),
        total_reps=("total_reps", "sum"),
        average_weight=("weight", "mean"),
        best_weight=("weight", "max"),
        total_volume=("volume", "sum"),
    )
    .sort_values("total_volume", ascending=False)
)

comparison_metric = st.selectbox(
    "Comparison metric",
    options=[
        "total_volume",
        "total_reps",
        "total_sets",
        "best_weight",
        "average_weight",
    ],
    format_func=lambda value: value.replace("_", " ").title(),
)

st.bar_chart(
    exercise_summary.set_index("exercise")[[comparison_metric]]
)


with st.expander("View cleaned workout data"):
    st.dataframe(
        filtered_df.drop(columns=["period"], errors="ignore"),
        use_container_width=True,
        hide_index=True,
    )

st.caption(
    "Training volume is calculated as sets × reps × weight. "
    "Uploaded files are analyzed in memory and are not automatically saved to SQLite."
)
