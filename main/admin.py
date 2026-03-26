from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.urls import path, reverse
from django.shortcuts import redirect
from django.contrib import messages
from django.utils.html import format_html
from .models import Category, Flower, Order, OrderItem, Profile, Review


# 🔹 PROFILE INLINE
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = True
    fields = ['phone', 'address']
    extra = 0


# 🔹 USER ADMIN
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'is_active', 'is_staff', 'user_actions')

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('block/<int:user_id>/', self.admin_site.admin_view(self.block_user)),
            path('unblock/<int:user_id>/', self.admin_site.admin_view(self.unblock_user)),
            path('delete/<int:user_id>/', self.admin_site.admin_view(self.delete_user)),
        ]
        return custom_urls + urls

    def user_actions(self, obj):
        if obj.is_active:
            return format_html(
                '<a href="{}">🔒</a> | <a href="{}">🗑️</a>',
                reverse('admin:auth_user_block', args=[obj.id]),
                reverse('admin:auth_user_delete', args=[obj.id]),
            )
        return format_html(
            '<a href="{}">✅</a> | <a href="{}">🗑️</a>',
            reverse('admin:auth_user_unblock', args=[obj.id]),
            reverse('admin:auth_user_delete', args=[obj.id]),
        )

    user_actions.short_description = 'Действия'

    def block_user(self, request, user_id):
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.is_active = False
            user.save()
            messages.success(request, f'{user.username} заблокирован')
        return redirect('..')

    def unblock_user(self, request, user_id):
        user = User.objects.get(id=user_id)
        user.is_active = True
        user.save()
        messages.success(request, f'{user.username} разблокирован')
        return redirect('..')

    def delete_user(self, request, user_id):
        user = User.objects.get(id=user_id)
        if user != request.user:
            user.delete()
            messages.success(request, 'Пользователь удалён')
        return redirect('..')


admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


# 🔹 CATEGORY
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'flower_count']
    prepopulated_fields = {'slug': ('name',)}

    def flower_count(self, obj):
        return Flower.objects.filter(category=obj).count()

    flower_count.short_description = 'Цветов'


# 🔹 FLOWER
@admin.register(Flower)
class FlowerAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'available', 'created_at']
    list_filter = ['category', 'available']
    search_fields = ['name']
    list_editable = ['price', 'available']


# 🔹 ORDER
class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'status', 'total_price', 'created_at']
    inlines = [OrderItemInline]


# 🔹 REVIEW
@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['user', 'flower', 'rating', 'is_approved']
    list_editable = ['is_approved']


# 🔹 PROFILE
@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone']