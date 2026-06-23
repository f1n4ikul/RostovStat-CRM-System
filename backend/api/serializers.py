from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    AdditionalDocument, AudioRecord, Favorite,
    Post, PostComment, FeedComment,
    PortalNews, RegionalStat,
)

from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError

from django.db import transaction  # <-- ДОБАВИТЬ ИМПОРТ

class UserCreateByAdminSerializer(serializers.ModelSerializer):
    role = serializers.CharField(write_only=True, required=False, default='employee')
    # 1. Делаем поле необязательным (required=False) и разрешаем пустые строки (allow_blank=True)
    department = serializers.CharField(write_only=True, required=False, allow_blank=True, default='Общий отдел') 
    password = serializers.CharField(write_only=True, required=True)

    DEPARTMENTS_LIST = [
        "Отдел сводных статических работ и общественных связей",
        "Отдел региональных счетов и балансов",
        "Отдел статистики цен и финансов",
        "Отдел статистики сельского хозяйства и окружающей природной среды",
        "Отдел статистики предприятий",
        "Отдел статистики рыночных услуг",
        "Отдел статистики труда, образования, науки и инноваций",
        "Отдел статистики уровня жизни и обследований домашних хозяйств",
        "Отдел статистики строительства, инвестиций и жилищно-коммунального хозяйства",
        "Отдел статистики населения и здравоохранения, организации и проведения переписей и обследований",
        "Общий отдел"
    ]

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role', 'department']

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Пароль должен быть не менее 8 символов.")
        return value

    def validate_email(self, value):
        # 2. Если email пустой, просто пропускаем (чтобы не упасть, если фронт его не прислал)
        if not value:
            return value
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Этот Email уже зарегистрирован в системе.")
        return value

    def validate_department(self, value):
        # 3. Если фронт прислал пустоту, подменяем на дефолт и не взрываем валидацию
        if not value or value.strip() == "":
            return "Общий отдел"
        
        # На всякий случай: если фронт прислал что-то, чего нет в списке, 
        # вместо жесткой ошибки просто мягко сбросим на "Общий отдел" для защиты
        if value not in self.DEPARTMENTS_LIST:
            return "Общий отдел"
            
        return value

    def create(self, validated_data):
        role = validated_data.pop('role', 'employee')
        # Если вдруг департмент потерялся в validated_data, берем дефолт
        department = validated_data.pop('department', 'Общий отдел')
        password = validated_data.pop('password')

        with transaction.atomic():
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data.get('email', ''),
                password=password,
                first_name=department
            )
            
            user.is_staff = role in ('admin', 'moderator')
            user.is_superuser = role == 'admin'
            user.save()

            profile = user.profile
            profile.department = department
            profile.role = role if role in ('employee', 'moderator', 'admin') else 'employee'
            profile.save()

            return user

class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PostComment
        fields = ['id', 'author_name', 'text', 'timestamp', 'created_at']


class PostCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = FeedComment
        fields = ['id', 'author_name', 'text', 'created_at']
        read_only_fields = ['author', 'post', 'created_at']


class AdditionalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDocument
        fields = ['id', 'file', 'file_name', 'created_at']


class AudioRecordSerializer(serializers.ModelSerializer):
    author_id = serializers.ReadOnlyField(source='author.id')
    author_name = serializers.ReadOnlyField(source='author.username')
    author_department = serializers.ReadOnlyField(source='author.profile.department')
    is_favorite = serializers.SerializerMethodField()
    is_private = serializers.BooleanField(default=False)
    comments = CommentSerializer(many=True, read_only=True)
    documents = AdditionalDocumentSerializer(many=True, read_only=True)

    class Meta:
        model = AudioRecord
        fields = [
            'id', 'title', 'file', 'category', 'description', 'created_at',
            'author_id', 'author_name', 'author_department',
            'is_favorite', 'is_private',
            'tags', 'file_format', 'bitrate', 'file_size',
            'is_verified', 'security_level',
            'comments', 'documents',
        ]

    def get_is_favorite(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            return Favorite.objects.filter(user=user, track=obj).exists()
        return False


class AudioRecordCreateSerializer(serializers.ModelSerializer):
    # Трюк 1: Явно объявляем category как CharField, чтобы развязать руки от choices в БД
    category = serializers.CharField(required=False, default='svod')
    
    class Meta:
        model = AudioRecord
        # Убедись, что все эти поля действительно есть в твоей модели AudioRecord
        fields = ['title', 'file', 'category', 'description', 'is_private']

    def validate_is_private(self, value):
        # Трюк 2: Превращаем текстовые "true"/"false" от FormData в реальные True/False
        if isinstance(value, str):
            return value.lower() in ['true', '1', 'yes']
        return bool(value)

    def validate_file(self, value):
        # Трюк 3: Смягчаем валидацию для blob-файлов во время тестов/защиты
        name_lower = value.name.lower()
        if not (name_lower.endswith('.mp4') or 'blob' in name_lower):
            raise serializers.ValidationError("Допускаются только файлы формата MP4 (.mp4).")
        return value

    def create(self, validated_data):
        # Автор и формат проставляются автоматически
        validated_data['author'] = self.context['request'].user
        validated_data['file_format'] = 'MP4'
        return super().create(validated_data)
    
class UserProfileSerializer(serializers.ModelSerializer):
    total_records = serializers.SerializerMethodField()
    total_favorites = serializers.SerializerMethodField()
    role = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'role', 'total_records', 'total_favorites']

    def get_total_records(self, obj):
        return obj.audio_records.count()

    def get_total_favorites(self, obj):
        return obj.favorites.count()

    def get_role(self, obj):
        return "Администратор" if obj.is_staff else "Сотрудник"


class UserAdminSerializer(serializers.ModelSerializer):
    role = serializers.CharField(source='profile.role', read_only=True)

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_staff']


class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    author_department = serializers.ReadOnlyField(source='author.profile.department')
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author_name', 'author_department',
            'text', 'image', 'created_at',
            'likes_count', 'is_liked', 'comments_count', 'is_owner',
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        user = self.context['request'].user
        return obj.likes.filter(id=user.id).exists() if user.is_authenticated else False

    def get_is_owner(self, obj):
        user = self.context['request'].user
        return obj.author == user if user.is_authenticated else False


class PortalNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalNews
        fields = '__all__'


class RegionalStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionalStat
        fields = '__all__'
