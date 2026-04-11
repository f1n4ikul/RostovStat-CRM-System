from rest_framework import serializers
from .models import AdditionalDocument, PortalNews, RegionalStat, AudioRecord, Favorite, Post, PostComment, FeedComment
from django.contrib.auth.models import User



class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = PostComment
        fields = ['id', 'author_name', 'text', 'timestamp', 'created_at']


class PostCommentSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = FeedComment
        # Мы просто перечисляем поля, которые хотим отправить на фронтенд
        fields = ['id', 'author_name', 'text', 'timestamp', 'created_at']


class AdditionalDocumentSerializer(serializers.ModelSerializer):
    class Meta:
        model = AdditionalDocument
        fields = ['id', 'file', 'file_name', 'created_at']

class AudioRecordSerializer(serializers.ModelSerializer):
    # Добавляем ID автора, чтобы фронтенд мог сравнивать его с ID текущего юзера
    author_id = serializers.ReadOnlyField(source='author.id')
    is_favorite = serializers.SerializerMethodField()
    author_department = serializers.ReadOnlyField(source='author.profile.department')
    comments = CommentSerializer(many=True, read_only=True) # Добавляем вложенные комменты
    # По желанию можно добавить и имя автора
    author_name = serializers.ReadOnlyField(source='author.username')
    is_private = serializers.BooleanField(default=False)

    documents = AdditionalDocumentSerializer(many=True, read_only=True)


    class Meta:
        model = AudioRecord
        # Добавляем author_id в список полей
        fields = [
            'id', 'title', 'file', 'category', 'description', 'created_at', 
            'author_id', 'author_name', 'author_department', 'is_favorite', 
            'is_private', 'comments', 'tags', 'file_format', 'bitrate', 
            'file_size', 'is_verified', 'security_level',
            'documents'
        ]

    def get_is_favorite(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            from .models import Favorite
            return Favorite.objects.filter(user=user, track=obj).exists()
        return False

class AudioRecordCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AudioRecord
        fields = ['title', 'file', 'category', 'description', 'is_private']
        
    # Метод для автоматической привязки автора при сохранении
    def create(self, validated_data):
        # Берем пользователя из контекста запроса
        validated_data['author'] = self.context['request'].user
        return super().create(validated_data)
    


class UserProfileSerializer(serializers.ModelSerializer):
    # Добавляем статистику прямо в профиль
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
    role = serializers.CharField(source='profile.role', read_only=True) # Убедись, что связь с профилем подтягивается
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'role', 'is_staff']



class PostSerializer(serializers.ModelSerializer):
    author_name = serializers.ReadOnlyField(source='author.username')
    # Берем отдел из связанного профиля пользователя
    author_department = serializers.ReadOnlyField(source='author.profile.department')
    likes_count = serializers.SerializerMethodField()
    is_liked = serializers.SerializerMethodField()
    # Подтягиваем список комментариев сразу (по желанию) или только их кол-во
    comments_count = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = [
            'id', 'author_name', 'author_department', 
            'text', 'image', 'created_at', 
            'likes_count', 'is_liked', 'comments_count'
        ]

    def get_likes_count(self, obj):
        return obj.likes.count()

    def get_is_liked(self, obj):
        user = self.context.get('request').user
        if user.is_authenticated:
            return obj.likes.filter(id=user.id).exists()
        return False
    
class PortalNewsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortalNews
        fields = '__all__'

class RegionalStatSerializer(serializers.ModelSerializer):
    class Meta:
        model = RegionalStat
        fields = '__all__'