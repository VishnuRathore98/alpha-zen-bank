from enum import Enum
from sqlmodel import SQLModel, Field
from pydantic import EmailStr, field_validator
from fastapi import HTTPException, status


class SecurityQuestionsSchema(str, Enum):
    MOTHER_MAIDEN_NAME = "mother_maiden_name"
    CHILDHOOD_FRIEND = "childhood_friend"
    FAVORITE_COLOR = "favorite_color"
    BIRTH_CITY = "birth_city"

    @classmethod
    def get_description(cls, value: "SecurityQuestionsSchema") -> str:
        descriptions = {
            cls.MOTHER_MAIDEN_NAME: "What is the name of your mother?",
            cls.CHILDHOOD_FRIEND: "What is the name of your childhood friend?",
            cls.FAVORITE_COLOR: "What is your favorite color?",
            cls.BIRTH_CITY: "What is the name of the city you were born in?",
        }

        return descriptions.get(value, "Unknown security question")
