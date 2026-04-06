from django.db import models
from django.contrib.auth.models import User

class AudioRecord(models.Model):
    CATEGORY_CHOICES = [
        ('concentration', 'Для концентрации (Lo-Fi, Классика)'),
        ('pro', 'Профессиональный контент (Вебинары, Акты)'),
        ('relax', 'Психологическая разгрузка (Природа, Медитация)'),
        ('meeting', 'Совещание / Протокол'),
        ('other', 'Прочее'),
    ]

    # ДОБАВЛЯЕМ СВЯЗЬ С ПОЛЬЗОВАТЕЛЕМ (АВТОРОМ)
    # null=True и blank=True нужны для миграции, если в базе уже есть записи
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='audio_records',
        verbose_name="Автор",
        null=True, 
        blank=True
    )
    
    title = models.CharField("Название", max_length=255)
    description = models.TextField("Описание", blank=True, null=True)
    file = models.FileField("Файл", upload_to='audio_records/')
    category = models.CharField("Категория", max_length=20, choices=CATEGORY_CHOICES, default='other')
    created_at = models.DateTimeField("Дата добавления", auto_now_add=True)
    is_private = models.BooleanField(default=False)
    tags = models.CharField("Теги", max_length=255, blank=True, help_text="Введите теги через запятую")


    class Meta:
        verbose_name = "Аудиозапись"
        verbose_name_plural = "Аудиозаписи"
        ordering = ['-created_at'] # Свежие записи будут сверху

    def __str__(self):
        # Добавляем имя автора в отображение для админки
        author_name = self.author.username if self.author else "Система"
        return f"{self.title} ({author_name})"
    
class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    track = models.ForeignKey(AudioRecord, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'track')
        verbose_name = "Избранное"
        verbose_name_plural = "Избранное"


class Comment(models.Model):
    record = models.ForeignKey(
        AudioRecord,
        on_delete=models.CASCADE,
        related_name='comments',
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.FloatField()  # Время в секундах (например, 135.5 для 02:15)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']


class UserProfile(models.Model):
    # Вместо on_express_related_name используем related_name
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE, 
        related_name='profile'
    )
    
    # Убираем font_weight (это для CSS) и меняем label на verbose_name
    department = models.CharField(
        max_length=100, 
        verbose_name="Отдел", 
        default="Общий отдел"
    )

    # Если у тебя есть роли, добавь их через choices
    ROLE_CHOICES = [
        ('employee', 'Сотрудник'),
        ('moderator', 'Модератор'),
        ('admin', 'Администратор'),
    ]
    role = models.CharField(
        max_length=20, 
        choices=ROLE_CHOICES, 
        default='employee'
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"