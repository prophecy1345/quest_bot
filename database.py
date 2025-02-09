# database.py

# Список пользователей, оплативших доступ
paid_users = {}  # Добавляй ID пользователей сюда вручную или через бота

def is_user_paid(user_id):
    """Проверяет, есть ли пользователь в списке оплативших"""
    return user_id in paid_users

def add_user(user_id):
    """Добавляет пользователя в список оплативших"""
    paid_users.add(user_id)

def remove_user(user_id):
    """Удаляет пользователя из списка оплативших"""
    paid_users.discard(user_id)