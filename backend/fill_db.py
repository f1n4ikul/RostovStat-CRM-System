import os
import django
import io
from django.core.files.base import ContentFile

# Настройка окружения Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings') # Замени 'backend' на имя папки с settings.py
django.setup()

from django.contrib.auth.models import User
from api.models import AudioRecord, UserProfile

def fill_data():
    print("Начинаю наполнение базы...")
    
    # 1. Находим или создаем пользователя
    user, created = User.objects.get_or_create(username='admin_test')
    if created:
        user.set_password('password123')
        user.is_staff = True
        user.is_superuser = True
        user.save()
    
    # Обновляем профиль
    profile, _ = UserProfile.objects.get_or_create(user=user)
    profile.role = 'admin'
    profile.save()

    # 2. Создаем 50 записей
    for i in range(71, 92):
        title = f"test{i}"
        
        # Если такой трек уже есть, пропускаем, чтобы не дублировать
        if AudioRecord.objects.filter(title=title).exists():
            continue

        # Создаем "пустой" файл-заглушку
        fake_file = ContentFile(b"fake audio data", name=f"test_audio_{i}.mp3")

        AudioRecord.objects.create(
            title=title,
            description=f"Это тестовая аудиозапись №{i}",
            category="meet",
            author=user,
            file=fake_file,
            is_private=False,
            tags="тест, автозаполнение"
        )
        if i % 10 == 0:
            print(f"Добавлено {i} записей...")

    print(f"Готово! Теперь в базе {AudioRecord.objects.count()} записей.")

if __name__ == '__main__':
    fill_data()