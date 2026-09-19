import sqlite3
from config.config import DB_NAME



def get_connection():
    return sqlite3.connect(DB_NAME)


def create_tables():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            exercise TEXT,
            sets INTEGER,
            reps INTEGER,
            weight REAL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS foods (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            food TEXT,
            quantity REAL,
            calories REAL,
            protein REAL,
            carbs REAL,
            fat REAL
        )
    """)

    conn.commit()
    conn.close()


def add_workout(date, exercise, sets, reps, weight):

    conn = get_connection()

    conn.execute("""
        INSERT INTO workouts
        (date, exercise, sets, reps, weight)

        VALUES (?, ?, ?, ?, ?)
    """, (date, exercise, sets, reps, weight))

    conn.commit()
    conn.close()


def add_food(
    date,
    food,
    quantity,
    calories,
    protein,
    carbs,
    fat
):

    conn = get_connection()

    conn.execute("""
        INSERT INTO foods
        (date, food, quantity, calories, protein, carbs, fat)

        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        date,
        food,
        quantity,
        calories,
        protein,
        carbs,
        fat
    ))

    conn.commit()
    conn.close()