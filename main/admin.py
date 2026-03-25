from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import Category, Flower, Order, OrderItem, Profile, Review


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    verbose_name_plural = 'Профиль'
    fields = ['phone', 'address']
    extra = 0


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_active', 'is_staff', 'user_actions')
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'groups')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_per_page = 20
    actions = None

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('block-user/<int:user_id>/', self.admin_site.admin_view(self.block_user), name='block-user'),
            path('unblock-user/<int:user_id>/', self.admin_site.admin_view(self.unblock_user), name='unblock-user'),
            path('delete-user/<int:user_id>/', self.admin_site.admin_view(self.delete_user), name='delete-user'),
        ]
        return custom_urls + urls

    def user_actions(self, obj):
        if obj.is_active:
            return format_html(
                '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px;" onclick="return confirm(\'Вы уверены?\')">🔒 Заблокировать</a>'
                '<a class="button" href="{}" style="background-color: #17a2b8; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" onclick="return confirm(\'Вы уверены?\')">🗑️ Удалить</a>',
                f'/admin/auth/user/block-user/{obj.id}/',
                f'/admin/auth/user/delete-user/{obj.id}/'
            )
        else:
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none; margin-right: 5px;">✅ Разблокировать</a>'
                '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 4px; text-decoration: none;" onclick="return confirm(\'Вы уверены?\')">🗑️ Удалить</a>',
                f'/admin/auth/user/unblock-user/{obj.id}/',
                f'/admin/auth/user/delete-user/{obj.id}/'
            )

    user_actions.short_description = 'Действия'

    def block_user(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                messages.error(request, 'Нельзя заблокировать себя!')
            else:
                user.is_active = False
                user.save()
                messages.success(request, f'{user.username} заблокирован')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:auth_user_changelist')

    def unblock_user(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            user.is_active = True
            user.save()
            messages.success(request, f'{user.username} разблокирован')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:auth_user_changelist')

    def delete_user(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)
            if user == request.user:
                messages.error(request, 'Нельзя удалить себя!')
            else:
                username = user.username
                user.delete()
                messages.success(request, f'{username} удалён')
        except User.DoesNotExist:
            messages.error(request, 'Пользователь не найден')
        return redirect('admin:auth_user_changelist')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'flower_count']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']

    def flower_count(self, obj):
        return obj.flowers.count()

    flower_count.short_description = 'Цветов'


@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available', 'created_at', 'action_buttons']
    list_filter = ['category', 'available']
    search_fields = ['name', 'description']
    list_editable = ['price', 'available']
    list_per_page = 25

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; margin-right: 3px;">✏️</a>'
            '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;" onclick="return confirm(\'Удалить?\')">🗑️</a>',
            f'/admin/main/flower/{obj.id}/change/',
            f'/admin/main/flower/{obj.id}/delete/'
        )

    action_buttons.short_description = 'Действия'


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'status_colored', 'total_price', 'action_buttons']
    list_filter = ['status', 'created_at']
    search_fields = ['user__username', 'address', 'phone']
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 30

    def status_colored(self, obj):
        colors = {
            'new': '#17a2b8',
            'processing': '#ffc107',
            'delivered': '#28a745',
            'cancelled': '#dc3545'
        }
        status_names = {
            'new': '🆕 Новый',
            'processing': '⚙️ В обработке',
            'delivered': '✅ Доставлен',
            'cancelled': '❌ Отменён'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 20px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            status_names.get(obj.status, obj.status)
        )

    status_colored.short_description = 'Статус'

    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="{}" style="background-color: #007bff; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; margin-right: 3px;">👁️</a>'
            '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;" onclick="return confirm(\'Удалить?\')">🗑️</a>',
            f'/admin/main/order/{obj.id}/change/',
            f'/admin/main/order/{obj.id}/delete/'
        )

    action_buttons.short_description = 'Действия'


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'flower', 'quantity', 'price']
    list_filter = ['order__status']
    search_fields = ['order__id', 'flower__name']


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'flower', 'rating_stars', 'created_at', 'is_approved', 'action_buttons']
    list_filter = ['rating', 'is_approved', 'created_at']
    search_fields = ['user__username', 'text']
    list_editable = ['is_approved']
    list_per_page = 30

    def rating_stars(self, obj):
        return '⭐' * obj.rating

    rating_stars.short_description = 'Рейтинг'

    def action_buttons(self, obj):
        if not obj.is_approved:
            return format_html(
                '<a class="button" href="{}" style="background-color: #28a745; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none; margin-right: 3px;">✅</a>'
                '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;" onclick="return confirm(\'Удалить?\')">🗑️</a>',
                f'/admin/main/review/{obj.id}/change/',
                f'/admin/main/review/{obj.id}/delete/'
            )
        return format_html(
            '<a class="button" href="{}" style="background-color: #dc3545; color: white; padding: 3px 8px; border-radius: 3px; text-decoration: none;" onclick="return confirm(\'Удалить?\')">🗑️</a>',
            f'/admin/main/review/{obj.id}/delete/'
        )

    action_buttons.short_description = 'Действия'


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'phone', 'address']
    search_fields = ['user__username', 'phone']
    list_filter = ['user__is_active']
    list_per_page = 25
    raw_id_fields = ['user']

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')