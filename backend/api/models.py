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
    file_format = models.CharField("Формат", max_length=10, default="MP3")
    bitrate = models.CharField("Битрейт", max_length=20, default="128 kbps")
    file_size = models.CharField("Размер", max_length=20, default="0 MB")

    is_verified = models.BooleanField("Проверено архивом", default=False)
    security_level = models.CharField(
        "Уровень доступа", 
        max_length=50, 
        default="Только для внутреннего пользования"
    )

    tags = models.CharField("Теги", max_length=255, blank=True, default="Аналитика, Голос")


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



class PostComment(models.Model):
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

class Post(models.Model):
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='posts',
        verbose_name="Автор"
    )
    text = models.TextField("Текст поста")
    image = models.ImageField("Изображение", upload_to='post_images/', blank=True, null=True)
    created_at = models.DateTimeField("Дата публикации", auto_now_add=True)
    
    # Можно добавить лайки
    likes = models.ManyToManyField(User, related_name='liked_posts', blank=True)

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ['-created_at']

    def __str__(self):
        return f"Пост от {self.author.username} ({self.created_at.strftime('%d.%m %H:%M')})"
    
class FeedComment(models.Model):
    post = models.ForeignKey(
        Post, 
        on_delete=models.CASCADE, 
        related_name='comments',
        verbose_name="Пост"
    )
    author = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        verbose_name="Автор"
    )
    text = models.TextField("Текст комментария")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Комментарий к посту"
        verbose_name_plural = "Комментарии к постам"
        ordering = ['-created_at'] # Новые сверху

    def __str__(self):
        return f"Коммент от {self.author.username} к посту {self.post.id}"
    

class PortalNews(models.Model):
    title = models.CharField("Заголовок", max_length=255)
    content = models.TextField("Текст новости")
    is_important = models.BooleanField("Закрепить на главной", default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Новость портала"
        verbose_name_plural = "Новости портала"
        ordering = ['-is_important', '-created_at']

    def __str__(self):
        return self.title

class RegionalStat(models.Model):
    label = models.CharField("Название показателя", max_length=100) # Инфляция
    value = models.CharField("Значение", max_length=50) # +0.4%
    trend = models.CharField("Тренд", max_length=10, choices=[('up', 'Вверх'), ('down', 'Вниз'), ('stable', 'Стабильно')])
    
    class Meta:
        verbose_name = "Статистический показатель"
        verbose_name_plural = "Статистические показатели"

    def __str__(self):
        return f"{self.label}: {self.value}"


class AdditionalDocument(models.Model):
    # Связь "многие файлы к одной аудиозаписи"
    # Если нужно "многие к многим", можно сменить на ManyToManyField
    audio_record = models.ForeignKey(
        'AudioRecord', 
        on_delete=models.CASCADE, 
        related_name='documents',
        verbose_name="Основная запись"
    )
    file = models.FileField("Документ", upload_to='audio_docs/')
    file_name = models.CharField("Имя файла", max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Дополнительный документ"
        verbose_name_plural = "Дополнительные документы"

    def __str__(self):
        return self.file_name