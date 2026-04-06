from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AudioViewSet, register_user, upload_audio, toggle_favorite, get_user_favorites,get_user_profile,add_comment, custom_auth_token, get_all_users_for_admin, change_user_role, delete_audio, download_audio
from . import views

router = DefaultRouter()
router.register(r'records', AudioViewSet, basename='audiorecord')

urlpatterns = [
    path('', include(router.urls)),
    path('register/', register_user),
    path('upload/', upload_audio),
    path('tracks/<int:track_id>/toggle-favorite/', toggle_favorite),
    path('favorites/', get_user_favorites),
    path('profile/', get_user_profile),
    path('audio/<int:track_id>/add_comment/', add_comment),
    path('login/', custom_auth_token),
    path('admin/users/', get_all_users_for_admin),
    path('admin/users/<int:user_id>/role/', change_user_role),
    path('records/<int:pk>/delete/', delete_audio),
    path('records/<int:pk>/download/', download_audio),
]