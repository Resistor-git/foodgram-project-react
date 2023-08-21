from django.contrib import admin

from .models import CustomUser


#TODO добавить как-то отображение тегов
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email',
                    'first_name', 'last_name')
    list_editable = ('username', 'email',
                     'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')

admin.site.register(CustomUser, CustomUserAdmin)