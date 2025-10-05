# content.py

from datetime import datetime

# Тематические курсы
COURSES = {
    "general": {
        "name": "Общий курс",
        "lessons": [
            {
                "palabra": {"es": "hola", "ru": "привет", "example": "¡Hola! ¿Cómo estás?"},
                "frase": {"es": "¿Cómo te llamas?", "ru": "Как тебя зовут?", "context": "При знакомстве"},
                "quiz": {"question": "Как переводится 'gracias'?", "options": ["спасибо", "пожалуйста", "извините", "до свидания"], "correct": 0}
            },
            {
                "palabra": {"es": "adiós", "ru": "до свидания", "example": "¡Adiós! ¡Hasta luego!"},
                "frase": {"es": "¿De dónde eres?", "ru": "Откуда ты?", "context": "При знакомстве"},
                "quiz": {"question": "Как сказать 'пожалуйста'?", "options": ["gracias", "por favor", "lo siento", "hola"], "correct": 1}
            }
        ]
    },
    "viajes": {
        "name": "Испанский для путешествий",
        "lessons": [
            {
                "palabra": {"es": "pasaporte", "ru": "паспорт", "example": "¿Dónde está mi pasaporte?"},
                "frase": {"es": "¿Dónde está la estación?", "ru": "Где находится вокзал?", "context": "В городе"},
                "quiz": {"question": "Что означает 'hotel'?", "options": ["ресторан", "отель", "аэропорт", "музей"], "correct": 1}
            },
            {
                "palabra": {"es": "billete", "ru": "билет", "example": "Necesito un billete de tren."},
                "frase": {"es": "¿Cuánto cuesta?", "ru": "Сколько стоит?", "context": "В магазине"},
                "quiz": {"question": "Как сказать 'аэропорт'?", "options": ["estación", "aeropuerto", "hotel", "playa"], "correct": 1}
            }
        ]
    },
    "negocios": {
        "name": "Деловой испанский",
        "lessons": [
            {
                "palabra": {"es": "reunión", "ru": "встреча", "example": "Tenemos una reunión a las 10."},
                "frase": {"es": "¿Podemos programar una llamada?", "ru": "Можем ли мы назначить звонок?", "context": "По работе"},
                "quiz": {"question": "Что означает 'contrato'?", "options": ["договор", "счёт", "проект", "отчёт"], "correct": 0}
            }
        ]
    }
}

def get_daily_content(curso: str = "general"):
    if curso not in COURSES:
        curso = "general"
    lessons = COURSES[curso]["lessons"]
    day_of_year = datetime.now().timetuple().tm_yday
    index = (day_of_year - 1) % len(lessons)
    return lessons[index]