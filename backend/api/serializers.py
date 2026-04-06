from rest_framework import serializers
from .models import AudioRecord, Comment
from django.contrib.auth.models import User



class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'username', 'text', 'timestamp', 'created_at']



class AudioRecordSerializer(serializers.ModelSerializer):
    # Добавляем ID автора, чтобы фронтенд мог сравнивать его с ID текущего юзера
    author_id = serializers.ReadOnlyField(source='author.id')
    is_favorite = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True) # Добавляем вложенные комменты
    # По желанию можно добавить и имя автора
    author_name = serializers.ReadOnlyField(source='author.username')
    is_private = serializers.BooleanField(default=False)


    class Meta:
        model = AudioRecord
        # Добавляем author_id в список полей
        fields = ['id', 'title', 'file', 'category', 'description', 'created_at', 'author_id', 'author_name', 'is_favorite', 'is_private', 'comments']

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


