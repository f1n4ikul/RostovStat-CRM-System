from django.contrib import admin
from .models import AudioRecord

@admin.register(AudioRecord)
class AudioRecordAdmin(admin.ModelAdmin):
    # Поля, которые будут видны в общей таблице
    list_display = ('id', 'title', 'author', 'category', 'created_at')
    
    # Боковая панель фильтрации (очень удобно для КИС)
    list_filter = ('category', 'author', 'created_at')
    
    # Поля, по которым работает поиск
    search_fields = ('title', 'description', 'author__username')
    
    # Поля, которые нельзя редактировать (дату создания ставит система)
    readonly_fields = ('created_at',)
    
    # Группировка полей при редактировании записи
    fieldsets = (
        ('Основная информация', {
            'fields': ('title', 'category', 'author')
        }),
        ('Контент и описание', {
            'fields': ('file', 'description')
        }),
        ('Служебная информация', {
            'fields': ('created_at',),
        }),
    )

    # Автоматическая подстановка текущего пользователя как автора при создании через админку
    def save_model(self, request, obj, form, change):
        if not obj.author:
            obj.author = request.user
        super().save_model(request, obj, form, change)