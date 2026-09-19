def calculate_bmr(weight, height, age, gender):
    if gender == "Male":
        return 10 * weight + 6.25 * height - 5 * age + 5

    return 10 * weight + 6.25 * height - 5 * age - 161


def calculate_macros(weight, height, age, gender, activity, goal):
    bmr = calculate_bmr(weight, height, age, gender)

    tdee = bmr * activity

    if goal == "Bulk":
        target_calories = tdee + 300
    elif goal == "Cut":
        target_calories = tdee - 300
    else:
        target_calories = tdee

    protein = weight * 2
    fat = weight * 0.8

    protein_calories = protein * 4
    fat_calories = fat * 9

    carb_calories = target_calories - protein_calories - fat_calories
    carbs = max(carb_calories / 4, 0)

    return {
        "bmr": round(bmr),
        "tdee": round(tdee),
        "calories": round(target_calories),
        "protein": round(protein),
        "fat": round(fat),
        "carbs": round(carbs),
    }