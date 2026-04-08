from rest_framework import viewsets
from .serializers import AudioRecordSerializer, AudioRecordCreateSerializer, CommentSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated
from .models import Favorite, AudioRecord, UserProfile
from django.db.models import Count
from django.db.models import Q
from .permissions import IsModeratorOrAdmin, IsSystemAdmin
from django.http import FileResponse
import os


@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    
    employee_code = request.data.get('employee_code') 
    password = request.data.get('password')
    email = request.data.get('email')
    role = request.data.get('role')
    department = request.data.get('department', 'Общий отдел')

  
    if not employee_code or not password or not email:
        return Response(
            {'error': 'Табельный номер, пароль и Email обязательны для регистрации'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
   
    if User.objects.filter(username=employee_code).exists():
        return Response(
            {'error': 'Сотрудник с таким табельным номером уже зарегистрирован в системе'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

   
    user = User.objects.create_user(
        username=employee_code, 
        password=password,
        email=email
    )

    user.first_name = department

    if role in ['admin', 'moderator']:
        user.is_staff = True
    
    user.save()

    profile = user.profile
    profile.department = department
    profile.role = role if role in ['employee', 'moderator', 'admin'] else 'employee'
    profile.save()
    
    # Создаем токен для автоматического входа после регистрации
    token = Token.objects.create(user=user)

    if profile.role in ['admin', 'moderator']:
        user.is_staff = True
        user.save()
    
    return Response({
        'token': token.key,
        'username': user.username, # Возвращаем табельный номер
        'role': 'Модератор' if user.is_staff else 'Сотрудник'
    }, status=status.HTTP_201_CREATED)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsModeratorOrAdmin]) 
@parser_classes([MultiPartParser, FormParser])
def upload_audio(request):
    
    # Передаем данные, включая поле is_private с фронтенда
    serializer = AudioRecordCreateSerializer(
        data=request.data, 
        context={'request': request}
    )
    
    if serializer.is_valid():
        # Указываем автора явно при сохранении
        serializer.save(author=request.user) 
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_favorites(request):
    # Получаем только те треки, которые лайкнул текущий пользователь
    favorites = Favorite.objects.filter(user=request.user).select_related('track')
    tracks = [fav.track for fav in favorites]
    serializer = AudioRecordSerializer(tracks, many=True, context={'request': request})
    return Response(serializer.data)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_profile(request):
    user = request.user

    # --- БЛОК 1: РОЛЕВАЯ МОДЕЛЬ (RBAC) ---
    # Определяем понятное название роли для интерфейса
    if user.is_superuser:
        role_label = "Системный администратор"
        role_code = "admin"
    elif user.is_staff:
        role_label = "Модератор (Редактор)"
        role_code = "moderator"
    else:
        role_label = "Сотрудник"
        role_code = "employee"

    # Форматируем даты
    last_login_formatted = user.last_login.strftime('%d.%m.%Y %H:%M') if user.last_login else "Первый вход"
    date_joined_formatted = user.date_joined.strftime('%d %b %Y')

    # --- БЛОК 2: АНАЛИТИКА ---
    # Считаем статистику категорий для графиков в профиле
    category_stats = AudioRecord.objects.values('category').annotate(count=Count('id'))
    
    # Последние 3 загрузки (вообще в системе или личные - оставим системные для мониторинга)
    recent_tracks = AudioRecord.objects.order_by('-created_at')[:3]
    recent_data = [{
        'id': t.id, 
        'title': t.title, 
        'date': t.created_at.strftime('%d.%m %H:%M')
    } for t in recent_tracks]

    # --- БЛОК 3: ИТОГОВЫЙ ОТВЕТ ---
    return Response({
        # Личные данные
        'id': user.id,
        'username': user.username, # Табельный номер
        'email': user.email,
        'department': user.first_name or "Общий отдел", # Берем из first_name
        
        # Ролевая модель (теперь с кодом для логики во Vue)
        'role': role_label,
        'role_code': role_code, 
        
        # Служебная информация
        'date_joined': date_joined_formatted,
        'last_login': last_login_formatted,
        
        # Права доступа (чтобы фронтенд не гадал по строке роли)
        'permissions': {
            'can_upload': user.is_staff,
            'can_delete_others': user.is_staff,
            'is_admin': user.is_superuser
        },
        
        # Статистика (сводка для карточек)
        'summary': {
            'my_records': AudioRecord.objects.filter(author=user).count(),
            'my_favorites': Favorite.objects.filter(user=user).count(),
            'total_system_files': AudioRecord.objects.count(),
        },
        
        # Данные для графиков и логов
        'stats': {
            'categories': list(category_stats),
            'recent_activity': recent_data
        }
    })


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_audio(request, pk):
    try:
        track = AudioRecord.objects.get(pk=pk)
        
        # ПРОВЕРКА ПРАВ:
        # Разрешаем удаление, если юзер — Админ ИЛИ если он автор трека
        # (Убедись, что в модели AudioRecord есть поле author = models.ForeignKey(User...))
        if request.user.is_staff or (hasattr(track, 'author') and track.author == request.user):
            track.delete()
            return Response({'message': 'Файл удален'}, status=status.HTTP_204_NO_CONTENT)
        
        return Response({'error': 'У вас недостаточно прав для удаления этого файла'}, 
                        status=status.HTTP_403_FORBIDDEN)
                        
    except AudioRecord.DoesNotExist:
        return Response({'error': 'Файл не найден'}, status=status.HTTP_404_NOT_FOUND)
    


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_category(request, pk):
    # Только админ может менять категорию системных файлов
    if not request.user.is_staff:
        return Response({'error': 'Только администратор может менять категории'}, 
                        status=status.HTTP_403_FORBIDDEN)
    
    track = AudioRecord.objects.get(pk=pk)
    track.category = request.data.get('category')
    track.save()
    return Response({'message': 'Категория обновлена'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, track_id):
    try:
        track = AudioRecord.objects.get(id=track_id)
        favorite, created = Favorite.objects.get_or_create(user=request.user, track=track)

        if not created:
            favorite.delete()
            return Response({'is_favorite': False}, status=status.HTTP_200_OK)

        return Response({'is_favorite': True}, status=status.HTTP_201_CREATED)
    except AudioRecord.DoesNotExist:
        return Response({'error': 'Трек не найден'}, status=status.HTTP_404_NOT_FOUND)



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_comment(request, track_id):
    try:
        track = AudioRecord.objects.get(id=track_id)
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, record=track)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except AudioRecord.DoesNotExist:
        return Response({'error': 'Запись не найдена'}, status=status.HTTP_404_NOT_FOUND)
    

class AudioViewSet(viewsets.ModelViewSet):
    serializer_class = AudioRecordSerializer

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return AudioRecord.objects.none()

        # 1. Базовая зона доступа (Общая + Личная)
        if user.is_staff:
            queryset = AudioRecord.objects.all()
        else:
            queryset = AudioRecord.objects.filter(Q(is_private=False) | Q(author=user))

        # 2. УМНЫЙ ПОИСК (по параметру ?search=)
        search_query = self.request.query_params.get('search', None)
        if search_query:
            queryset = queryset.filter(
                Q(title__icontains=search_query) | 
                Q(author__username__icontains=search_query) |
                Q(tags__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # 3. ФИЛЬТР ПО КАТЕГОРИИ (по параметру ?category=)
        category_filter = self.request.query_params.get('category', None)
        if category_filter:
            queryset = queryset.filter(category=category_filter)

        return queryset.order_by('-created_at')

        
@api_view(['POST'])
@permission_classes([AllowAny]) # Явно разрешаем вход всем
def custom_auth_token(request):
    print(f"DATA RECEIVED: {request.data}") # ЭТО ПОЯВИТСЯ В ТЕРМИНАЛЕ DJANGO
    login_identity = request.data.get('employee_code') or request.data.get('username')
    # Логика получения данных точно такая же, как в регистрации
    password = request.data.get('password')

    if not login_identity or not password:
        return Response(
            {'error': 'Табельный номер и пароль обязательны'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Проверяем в базе
    user = authenticate(username=str(login_identity), password=password)

    if user is not None:
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'role': 'Модератор' if user.is_staff else 'Сотрудник'
        }, status=status.HTTP_200_OK)
    
    return Response(
        {'error': 'Неверный табельный номер или пароль'}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['GET'])
@permission_classes([IsAuthenticated, IsSystemAdmin]) # Защита: только Админ
def get_all_users_for_admin(request):
    """Возвращает список всех пользователей с их ролями для админки"""
    users = User.objects.all().select_related('profile').order_by('-date_joined')
    data = []
    for u in users:
        # Получаем отдел из first_name (как при регистрации)
        dept = u.first_name or "Общий отдел"
        role = u.profile.role if hasattr(u, 'profile') else 'employee'
        
        data.append({
            'id': u.id,
            'username': u.username, # Табельный номер
            'email': u.email,
            'department': dept,
            'role': role,
            'date_joined': u.date_joined.strftime('%d.%m.%Y'),
            'is_active': u.is_active
        })
    return Response(data)

@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSystemAdmin])
def change_user_role(request, user_id):
    try:
        target_user = User.objects.get(pk=user_id)
        new_role = request.data.get('role')
        
        if new_role not in ['employee', 'moderator', 'admin']:
            return Response({'error': 'Неверная роль'}, status=status.HTTP_400_BAD_REQUEST)

        if target_user == request.user and new_role != 'admin':
             return Response({'error': 'Вы не можете снять с себя права администратора'}, 
                            status=status.HTTP_400_BAD_REQUEST)

        # 1. Обновляем профиль
        profile, _ = UserProfile.objects.get_or_create(user=target_user)
        profile.role = new_role
        profile.save()

        # 2. Синхронизируем системные флаги Django
        # Важно: если роль admin, можно давать и is_superuser для полной власти
        target_user.is_staff = (new_role in ['moderator', 'admin'])
        if new_role == 'admin':
            target_user.is_superuser = True
        else:
            target_user.is_superuser = False
            
        target_user.save()

        # 3. Возвращаем актуальные данные, чтобы фронтенд обновил массив
        return Response({
            'message': f'Роль изменена',
            'new_role': new_role,
            'is_staff': target_user.is_staff
        })
        
    except User.DoesNotExist:
        return Response({'error': 'Пользователь не найден'}, status=status.HTTP_404_NOT_FOUND)
    

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def download_audio(request, pk):
    try:
        track = AudioRecord.objects.get(pk=pk)
        file_path = track.file.path

        if os.path.exists(file_path):
            # Открываем файл в бинарном режиме
            response = FileResponse(open(file_path, 'rb'), as_attachment=True)
            
            # Формируем красивое имя файла из заголовка записи
            # Очищаем от лишних символов, чтобы не было ошибок в заголовках
            filename = f"{track.title}.mp3".replace('"', '')
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
        
        return Response({'error': 'Файл на сервере не найден'}, status=status.HTTP_404_NOT_FOUND)
        
    except AudioRecord.DoesNotExist:
        return Response({'error': 'Запись не найдена'}, status=status.HTTP_404_NOT_FOUND)