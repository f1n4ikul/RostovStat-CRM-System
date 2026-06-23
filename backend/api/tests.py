import io
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIClient
from rest_framework import status
from .models import AudioRecord

class AudioMassCreateTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        # 1. Создаем пользователя
        self.user = User.objects.create_user(
            username='admin_test', 
            password='password123',
            email='test@rostovstat.ru'
        )
        self.user.is_staff = True
        self.user.save()
        
        # Создаем профиль с ролью admin
        from .models import UserProfile
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.role = 'admin'
        profile.department = 'IT'
        profile.save()
        # Авторизуемся
        self.client.force_authenticate(user=self.user)

    def test_create_50_tracks(self):
        """Тест создает 50 аудиозаписей и проверяет их наличие в базе"""
        print("\nНачинаю создание 50 тестовых записей...")
        
        for i in range(90, 120):
            # Создаем фейковый файл в памяти
            fake_file = io.BytesIO(b"fake audio content")
            fake_file.name = f'test_audio_{i}.mp3'
            
            data = {
                'title': f'test{i}',
                'description': f'Автоматически сгенерированное описание для теста №{i}',
                'category': 'concentration',
                'file': fake_file,
                'is_private': False
            }
            
            response = self.client.post('/api/upload/', data, format='multipart')
            
            # Проверяем, что каждая запись создается успешно
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            
            if i % 10 == 0:
                print(f"Создано {i} записей...")

        # Итоговая проверка в базе данных
        self.assertEqual(AudioRecord.objects.count(), 50)
        print("Успех: В базе данных ровно 50 записей.")

    def test_search_and_filter(self):
        """Проверка, что поиск находит созданные записи"""
        # Сначала создаем одну запись для теста поиска
        AudioRecord.objects.create(
            title="test999", 
            author=self.user, 
            category="pro",
            file="test.mp3"
        )
        
        response = self.client.get('/api/records/', {'search': 'test999'})
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], 'test999')