import base64
import json

from groq import Groq


FOOD_SCHEMA = {
    "type": "object",
    "properties": {
        "meal_name": {
            "type": "string"
        },
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "food_name": {
                        "type": "string"
                    },
                    "estimated_quantity": {
                        "type": "string"
                    },
                    "calories": {
                        "type": "number"
                    },
                    "protein_g": {
                        "type": "number"
                    },
                    "carbs_g": {
                        "type": "number"
                    },
                    "fat_g": {
                        "type": "number"
                    },
                    "confidence": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high"
                        ]
                    },
                    "assumptions": {
                        "type": "string"
                    }
                },
                "required": [
                    "food_name",
                    "estimated_quantity",
                    "calories",
                    "protein_g",
                    "carbs_g",
                    "fat_g",
                    "confidence",
                    "assumptions"
                ],
                "additionalProperties": False
            }
        },
        "total": {
            "type": "object",
            "properties": {
                "calories": {
                    "type": "number"
                },
                "protein_g": {
                    "type": "number"
                },
                "carbs_g": {
                    "type": "number"
                },
                "fat_g": {
                    "type": "number"
                }
            },
            "required": [
                "calories",
                "protein_g",
                "carbs_g",
                "fat_g"
            ],
            "additionalProperties": False
        },
        "overall_confidence": {
            "type": "string",
            "enum": [
                "low",
                "medium",
                "high"
            ]
        },
        "warning": {
            "type": "string"
        }
    },
    "required": [
        "meal_name",
        "items",
        "total",
        "overall_confidence",
        "warning"
    ],
    "additionalProperties": False
}


def analyze_food_image(
    image_bytes,
    mime_type,
    api_key,
    model_name="qwen/qwen3.8-27b",
    user_details=""
):
    if not api_key:
        raise ValueError("Groq API key is missing.")

    client = Groq(api_key=api_key)

    encoded_image = base64.b64encode(
        image_bytes
    ).decode("utf-8")

    image_data_url = (
        f"data:{mime_type};base64,{encoded_image}"
    )

    prompt = f"""
Analyse this food image and provide a rough nutrition estimate.

Additional information provided by the user:
{user_details if user_details else "No extra information provided."}

Instructions:

1. Identify every visible food item.
2. Estimate the visible serving size.
3. Estimate calories, protein, carbohydrates and fat.
4. Consider common Indian foods and cooking methods.
5. Clearly state assumptions about oil, butter, sugar, sauces and portion size.
6. Do not claim that the values are exact.
7. Confidence must be low, medium or high.
8. Return the result using the provided JSON structure.
"""

    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": prompt
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": image_data_url
                        }
                    }
                ]
            }
        ],
        temperature=0.2,
        max_completion_tokens=2000,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "food_nutrition_analysis",
                "strict": True,
                "schema": FOOD_SCHEMA
            }
        }
    )

    response_content = (
        response.choices[0].message.content
    )

    if not response_content:
        raise ValueError(
            "Groq returned an empty response."
        )

    try:
        return json.loads(response_content)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Groq returned invalid JSON."
        ) from error