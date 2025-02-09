import json

PAID_USERS_FILE = "paid_users.json"

def load_paid_users():
    """Загружает список оплативших пользователей из JSON-файла."""
    try:
        with open(PAID_USERS_FILE, "r") as file:
            return set(json.load(file))  # Преобразуем в set для быстрого поиска
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_paid_users(paid_users):
    """Сохраняет список оплативших пользователей в JSON-файл."""
    with open(PAID_USERS_FILE, "w") as file:
        json.dump(list(paid_users), file)

# Загружаем пользователей в память
paid_users = load_paid_users()

def is_user_paid(user_id):
    """Проверяет, есть ли пользователь в списке оплативших"""
    return user_id in paid_users

def add_user(user_id):
    """Добавляет пользователя в список оплативших и сохраняет в файл"""
    paid_users.add(user_id)
    save_paid_users(paid_users)

def remove_user(user_id):
    """Удаляет пользователя из списка оплативших и обновляет файл"""
    paid_users.discard(user_id)
    save_paid_users(paid_users)