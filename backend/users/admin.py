from django.contrib import admin

from .models import CustomUser, Subscription


#TODO добавить как-то отображение тегов
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('pk', 'username', 'email',
                    'first_name', 'last_name')
    list_editable = ('username', 'email',
                     'first_name', 'last_name')
    list_filter = ('username', 'email')
    search_fields = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_editable = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
