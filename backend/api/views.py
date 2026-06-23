import os
import re
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.http import FileResponse, HttpResponse
from rest_framework import status, viewsets
from rest_framework.decorators import api_view, permission_classes, parser_classes, action
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication

from .models import (
    RegionalStat, PortalNews, Favorite, AudioRecord,
    UserProfile, Post, PostComment, AdditionalDocument, FeedComment,
)
from .serializers import (
    AudioRecordSerializer, AudioRecordCreateSerializer,
    CommentSerializer, PostSerializer, PostCommentSerializer,
    PortalNewsSerializer, RegionalStatSerializer, UserCreateByAdminSerializer
)
from .permissions import IsSystemAdmin, IsAuthorOrReadOnly


# ─── Утилиты ──────────────────────────────────────────────────────────────────

def get_user_role_info(user):
    if user.is_superuser:
        return "Системный администратор", "admin"
    if user.is_staff:
        return "Модератор (Редактор)", "moderator"
    return "Сотрудник", "employee"


# ─── Auth ─────────────────────────────────────────────────────────────────────

# @api_view(['POST'])
# @permission_classes([AllowAny])
# def register_user(request):
#     data = request.data
#     employee_code = data.get('employee_code')
#     password = data.get('password')
#     email = data.get('email')
#     role = data.get('role', 'employee')
#     department = data.get('department', 'Общий отдел')

#     if not all([employee_code, password, email]):
#         return Response({'error': 'Заполните все обязательные поля'}, status=400)
#     if User.objects.filter(username=employee_code).exists():
#         return Response({'error': 'Табельный номер уже занят'}, status=400)

#     user = User.objects.create_user(
#         username=employee_code, password=password, email=email, first_name=department
#     )
#     user.is_staff = role in ('admin', 'moderator')
#     user.is_superuser = role == 'admin'
#     user.save()

#     profile = user.profile
#     profile.department = department
#     profile.role = role if role in ('employee', 'moderator', 'admin') else 'employee'
#     profile.save()

#     token, _ = Token.objects.get_or_create(user=user)
#     role_label, _ = get_user_role_info(user)
#     return Response({'token': token.key, 'username': user.username, 'role': role_label}, status=201)


@api_view(['POST'])
@permission_classes([AllowAny])
def custom_auth_token(request):
    identity = request.data.get('employee_code') or request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=str(identity), password=password)
    if not user:
        return Response({'error': 'Неверные данные входа'}, status=400)
    token, _ = Token.objects.get_or_create(user=user)
    role_label, _ = get_user_role_info(user)
    return Response({'token': token.key, 'user_id': user.pk, 'username': user.username, 'role': role_label})


# ─── Профиль и администрирование ──────────────────────────────────────────────

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSystemAdmin])
def admin_create_user(request):
    serializer = UserCreateByAdminSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response({
            'message': 'Сотрудник успешно добавлен в систему',
            'id': user.id,
            'username': user.username
        }, status=status.HTTP_201_CREATED) # Строго 201 статус!
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user
    role_label, role_code = get_user_role_info(user)
    category_stats = list(AudioRecord.objects.values('category').annotate(count=Count('id')))
    recent_tracks = list(AudioRecord.objects.order_by('-created_at')[:3].values('id', 'title'))

    return Response({
        'id': user.id, 'username': user.username, 'email': user.email,
        'department': user.first_name or 'Общий отдел',
        'role': role_label, 'role_code': role_code,
        'date_joined': user.date_joined.strftime('%d %b %Y'),
        'last_login': user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else '---',
        'summary': {
            'my_records': AudioRecord.objects.filter(author=user).count(),
            'my_favorites': Favorite.objects.filter(user=user).count(),
            'total_system_files': AudioRecord.objects.count(),
        },
        'stats': {'categories': category_stats, 'recent_activity': recent_tracks},
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSystemAdmin])
def get_all_users_for_admin(request):
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    data = [{
        'id': u.id, 'username': u.username, 'email': u.email,
        'department': u.first_name or 'Общий отдел',
        'role': u.profile.role if hasattr(u, 'profile') else 'employee',
        'date_joined': u.date_joined.strftime('%d.%m.%Y'),
        'is_active': u.is_active,
    } for u in users]
    return Response(data)


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSystemAdmin])
def change_user_role(request, user_id):
    try:
        target = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)

    new_role = request.data.get('role')
    if new_role not in ('employee', 'moderator', 'admin'):
        return Response({'error': 'Неверная роль'}, status=400)

    target.is_staff = new_role in ('moderator', 'admin')
    target.is_superuser = new_role == 'admin'
    target.save()

    profile, _ = UserProfile.objects.get_or_create(user=target)
    profile.role = new_role
    profile.save()
    return Response({'message': 'Роль изменена', 'new_role': new_role})


# ─── Аудио/Видео операции ─────────────────────────────────────────────────────

class AudioViewSet(viewsets.ModelViewSet):
    serializer_class = AudioRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return AudioRecord.objects.none()
        qs = AudioRecord.objects.all() if user.is_staff else \
            AudioRecord.objects.filter(Q(is_private=False) | Q(author=user))
        search = self.request.query_params.get('search')
        if search:
            qs = qs.filter(Q(title__icontains=search) | Q(tags__icontains=search))
        return qs.select_related('author').order_by('-created_at')


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_audio(request):
    serializer = AudioRecordCreateSerializer(data=request.data, context={'request': request})
    if not serializer.is_valid():
        return Response(serializer.errors, status=400)

    record = serializer.save(author=request.user)
    docs = [
        AdditionalDocument(audio_record=record, file=f, file_name=f.name)
        for f in request.FILES.getlist('documents')
    ]
    if docs:
        AdditionalDocument.objects.bulk_create(docs)
    return Response(AudioRecordSerializer(record, context={'request': request}).data, status=201)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_audio(request, pk):
    try:
        track = AudioRecord.objects.get(pk=pk)
    except AudioRecord.DoesNotExist:
        return Response(status=404)
    if not (request.user.is_staff or track.author == request.user):
        return Response({'error': 'Нет прав'}, status=403)
    track.delete()
    return Response(status=204)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_audio(request, pk):
    """Стриминг MP4-файла с поддержкой HTTP Range-запросов."""
    track = AudioRecord.objects.filter(pk=pk).first()
    if not track:
        return Response(status=404)
    if track.is_private and not request.user.is_staff and track.author != request.user:
        return Response({'error': 'Доступ ограничен'}, status=403)

    file_path = track.file.path
    file_size = os.path.getsize(file_path)
    content_type = 'video/mp4'
    range_header = request.META.get('HTTP_RANGE', '').strip()

    if range_header:
        match = re.match(r'bytes=(\d+)-(\d*)', range_header)
        if match:
            start = int(match.group(1))
            end = int(match.group(2)) if match.group(2) else file_size - 1
            end = min(end, file_size - 1)
            length = end - start + 1
            with open(file_path, 'rb') as f:
                f.seek(start)
                data = f.read(length)
            response = HttpResponse(data, status=206, content_type=content_type)
            response['Content-Range'] = f'bytes {start}-{end}/{file_size}'
            response['Accept-Ranges'] = 'bytes'
            response['Content-Length'] = str(length)
            return response

    response = FileResponse(open(file_path, 'rb'), content_type=content_type)
    response['Accept-Ranges'] = 'bytes'
    response['Content-Length'] = str(file_size)
    return response


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, track_id):
    track = AudioRecord.objects.filter(id=track_id).first()
    if not track:
        return Response(status=404)
    fav, created = Favorite.objects.get_or_create(user=request.user, track=track)
    if not created:
        fav.delete()
    return Response({'is_favorite': created})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_favorites(request):
    tracks = AudioRecord.objects.filter(favorited_by__user=request.user)
    return Response(AudioRecordSerializer(tracks, many=True, context={'request': request}).data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, track_id):
    track = AudioRecord.objects.filter(id=track_id).first()
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid() and track:
        serializer.save(user=request.user, record=track)
        return Response(serializer.data, status=201)
    return Response(status=400)


# ─── Лента (посты) ────────────────────────────────────────────────────────────

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().prefetch_related('comments', 'likes').order_by('-created_at')
    serializer_class = PostSerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'])
    def comments(self, request, pk=None):
        post = self.get_object()
        serializer = PostCommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, post=post)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_post_like(request, pk):
    post = Post.objects.filter(pk=pk).first()
    if not post:
        return Response(status=404)
    if post.likes.filter(id=request.user.id).exists():
        post.likes.remove(request.user)
        liked = False
    else:
        post.likes.add(request.user)
        liked = True
    return Response({'is_liked': liked, 'likes_count': post.likes.count()})


# ─── Портал и статистика ──────────────────────────────────────────────────────

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_live_stats(request):
    from .services import get_fallback_stats
    return Response(get_fallback_stats())


class PortalNewsViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PortalNews.objects.all()
    serializer_class = PortalNewsSerializer

    @action(detail=False, methods=['get'])
    def latest_important(self, request):
        news = self.get_queryset().filter(is_important=True).first() or self.get_queryset().first()
        return Response(self.get_serializer(news).data) if news else Response(status=404)


class RegionalStatViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = RegionalStat.objects.all()
    serializer_class = RegionalStatSerializer


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_category(request, pk):
    if not request.user.is_staff:
        return Response(status=403)
    track = AudioRecord.objects.get(pk=pk)
    track.category = request.data.get('category')
    track.save()
    return Response({'message': 'OK'})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_document(request, pk):
    doc = AdditionalDocument.objects.get(pk=pk)
    return FileResponse(open(doc.file.path, 'rb'), as_attachment=True)



@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsSystemAdmin])
def admin_delete_user(request, user_id):
    if request.user.id == int(user_id):
        return Response({'error': 'Вы не можете удалить самого себя'}, status=400)
    try:
        target_user = User.objects.get(pk=user_id)
        target_user.delete()
        return Response(status=204)
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=404)