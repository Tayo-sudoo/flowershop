from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.conf import settings
from django.contrib.auth.models import User
import urllib.parse
import urllib.request
import secrets
import json

from .models import Flower, Category, Order, OrderItem, Review, Profile
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .ai_helper import get_ai_response



def home(request):
    flowers = Flower.objects.filter(available=True).select_related('category').order_by('-created_at')[:8]
    return render(request, 'main/home.html', {'flowers': flowers})


def catalog(request):
    flowers = Flower.objects.filter(available=True).select_related('category')
    categories = Category.objects.all()
    search_query = request.GET.get('search', '')
    category_slug = request.GET.get('category', '')

    if search_query:
        flowers = flowers.filter(name__icontains=search_query)
    if category_slug:
        flowers = flowers.filter(category__slug=category_slug)

    return render(request, 'main/catalog.html', {
        'flowers': flowers,
        'categories': categories,
        'search_query': search_query,
    })


def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    reviews = Review.objects.filter(flower=flower, is_approved=True).select_related('user')
    related = Flower.objects.filter(category=flower.category, available=True).exclude(pk=pk)[:4]
    return render(request, 'main/flower_detail.html', {
        'flower': flower,
        'reviews': reviews,
        'related_flowers': related,
    })


def about(request):
    return render(request, 'main/about.html')


def contacts(request):
    if request.method == 'POST':
        messages.success(request, 'Сообщение отправлено! Мы свяжемся с вами скоро 🌸')
        return redirect('contacts')
    return render(request, 'main/contacts.html')


def cart(request):
    cart = request.session.get('cart', {})
    cart_items = []
    total = 0
    if cart:
        flower_ids = [int(fid) for fid in cart.keys()]
        flowers_map = {f.pk: f for f in Flower.objects.filter(pk__in=flower_ids).select_related('category')}
        for flower_id, qty in cart.items():
            flower = flowers_map.get(int(flower_id))
            if flower:
                item_total = flower.price * qty
                total += item_total
                cart_items.append({'flower': flower, 'quantity': qty, 'total': item_total})
    return render(request, 'main/cart.html', {'cart_items': cart_items, 'total': total})


def add_to_cart(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    cart = request.session.get('cart', {})
    key = str(pk)
    cart[key] = cart.get(key, 0) + 1
    request.session['cart'] = cart
    messages.success(request, f'🌸 {flower.name} добавлен в корзину!')
    return redirect('catalog')


@require_POST
def update_cart(request, pk):
    cart = request.session.get('cart', {})
    quantity = int(request.POST.get('quantity', 1))
    key = str(pk)
    if quantity > 0:
        cart[key] = quantity
    else:
        cart.pop(key, None)
    request.session['cart'] = cart
    return redirect('cart')


def remove_from_cart(request, pk):
    cart = request.session.get('cart', {})
    cart.pop(str(pk), None)
    request.session['cart'] = cart
    return redirect('cart')


@login_required
def checkout(request):
    cart = request.session.get('cart', {})
    if not cart:
        return redirect('cart')

    flower_ids = [int(fid) for fid in cart.keys()]
    flowers_map = {f.pk: f for f in Flower.objects.filter(pk__in=flower_ids).select_related('category')}

    if request.method == 'POST':
        address = request.POST.get('address', '').strip()
        phone = request.POST.get('phone', '').strip()
        comment = request.POST.get('comment', '').strip()
        payment_method = request.POST.get('payment_method', 'cash')
        if not address or not phone:
            messages.error(request, 'Укажите адрес и телефон.')
            cart_items = []
            total = 0
            for flower_id, qty in cart.items():
                flower = flowers_map.get(int(flower_id))
                if flower:
                    item_total = flower.price * qty
                    total += item_total
                    cart_items.append({'flower': flower, 'quantity': qty, 'total': item_total})
            return render(request, 'main/checkout.html', {'cart_items': cart_items, 'total': total})
        total = 0
        order = Order.objects.create(
            user=request.user, address=address, phone=phone,
            total_price=0, payment_method=payment_method, comment=comment
        )
        items_to_create = []
        for flower_id, qty in cart.items():
            flower = flowers_map.get(int(flower_id))
            if flower:
                items_to_create.append(OrderItem(order=order, flower=flower, quantity=qty, price=flower.price))
                total += flower.price * qty
        OrderItem.objects.bulk_create(items_to_create)
        order.total_price = total
        order.save()
        request.session['cart'] = {}
        return redirect('order_success', receipt_code=order.receipt_code)

    cart_items = []
    total = 0
    for flower_id, qty in cart.items():
        flower = flowers_map.get(int(flower_id))
        if flower:
            item_total = flower.price * qty
            total += item_total
            cart_items.append({'flower': flower, 'quantity': qty, 'total': item_total})
    return render(request, 'main/checkout.html', {'cart_items': cart_items, 'total': total})


def order_success(request, receipt_code):
    """Order success page with receipt."""
    order = get_object_or_404(Order, receipt_code=receipt_code)
    # Only owner or staff can view
    if order.user != request.user and not request.user.is_staff:
        from django.http import Http404
        raise Http404
    return render(request, 'main/order_success.html', {'order': order})


def check_receipt(request):
    """Public page to verify a receipt code."""
    order = None
    code = ''
    error = ''
    if request.method == 'POST' or request.GET.get('code'):
        code = (request.POST.get('code') or request.GET.get('code', '')).strip().upper()
        if code:
            try:
                order = Order.objects.prefetch_related('items__flower').get(receipt_code=code)
            except Order.DoesNotExist:
                error = 'Заказ с таким кодом не найден.'
    return render(request, 'main/check_receipt.html', {'order': order, 'code': code, 'error': error})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CustomAuthenticationForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'🐉 Добро пожаловать, {user.username}!')
        return redirect('home')
    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, '👋 Вы вышли из аккаунта')
    return redirect('home')


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')
    form = CustomUserCreationForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'🌸 Добро пожаловать, {user.username}! Аккаунт создан.')
        return redirect('home')
    return render(request, 'main/register.html', {'form': form})


@login_required
def profile(request):
    profile_obj, _ = Profile.objects.get_or_create(user=request.user)
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        profile_obj.phone = request.POST.get('phone', '')
        profile_obj.address = request.POST.get('address', '')
        if 'avatar' in request.FILES:
            profile_obj.avatar = request.FILES['avatar']
        profile_obj.save()
        messages.success(request, '✅ Профиль обновлён!')
        return redirect('profile')
    orders = Order.objects.filter(user=request.user).prefetch_related('items__flower').order_by('-created_at')
    return render(request, 'main/profile.html', {'orders': orders, 'profile': profile_obj})


@require_POST
def add_review(request):
    if not request.user.is_authenticated:
        return JsonResponse({'error': 'not authenticated'}, status=403)
    flower_id = request.POST.get('flower_id')
    rating = int(request.POST.get('rating', 5))
    text = request.POST.get('text', '')
    flower = get_object_or_404(Flower, pk=flower_id)
    Review.objects.create(user=request.user, flower=flower, rating=rating, text=text)
    messages.success(request, '💬 Отзыв отправлен на модерацию!')
    return redirect('flower_detail', pk=flower_id)


def reviews_api(request, flower_id):
    reviews = Review.objects.filter(flower_id=flower_id, is_approved=True).values('user__username', 'rating', 'text')
    return JsonResponse({'reviews': list(reviews)})


@require_POST
def ai_chat(request):
    try:
        data = json.loads(request.body)
        question = data.get('question', '')
        lang = request.session.get('language', 'ru')
        response = get_ai_response(question, lang)
        return JsonResponse({'response': response})
    except Exception as e:
        return JsonResponse({'response': 'Извините, произошла ошибка 🌸'})


@require_POST
def change_language(request):
    lang = request.POST.get('language', 'ru')
    if lang in ('ru', 'uz', 'en'):
        request.session['language'] = lang
    return JsonResponse({'status': 'ok'})


def google_login(request):
    state = secrets.token_urlsafe(16)
    request.session['google_oauth_state'] = state
    # Динамически берём текущий host из запроса (работает с любым IP)
    redirect_uri = request.build_absolute_uri('/auth/google/callback/')
    request.session['google_redirect_uri'] = redirect_uri
    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
    }
    url = 'https://accounts.google.com/o/oauth2/v2/auth?' + urllib.parse.urlencode(params)
    return redirect(url)


def google_callback(request):
    if request.GET.get('state', '') != request.session.get('google_oauth_state', ''):
        messages.error(request, '⚠️ Ошибка безопасности.')
        return redirect('login')

    code = request.GET.get('code')
    if not code:
        messages.error(request, '⚠️ Вход через Google отменён.')
        return redirect('login')

    try:
        # Берём тот же redirect_uri который использовался при логине
        redirect_uri = request.session.get('google_redirect_uri', request.build_absolute_uri('/auth/google/callback/'))
        token_data = urllib.parse.urlencode({
            'code': code,
            'client_id': settings.GOOGLE_CLIENT_ID,
            'client_secret': settings.GOOGLE_CLIENT_SECRET,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code',
        }).encode()
        req = urllib.request.Request(
            'https://oauth2.googleapis.com/token',
            data=token_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            tokens = json.loads(resp.read())
    except Exception as e:
        messages.error(request, f'⚠️ Ошибка токена: {e}')
        return redirect('login')

    access_token = tokens.get('access_token')
    try:
        req2 = urllib.request.Request(
            'https://www.googleapis.com/oauth2/v2/userinfo',
            headers={'Authorization': f'Bearer {access_token}'},
        )
        with urllib.request.urlopen(req2, timeout=10) as resp:
            userinfo = json.loads(resp.read())
    except Exception as e:
        messages.error(request, f'⚠️ Ошибка профиля: {e}')
        return redirect('login')

    email = userinfo.get('email')
    if not email:
        messages.error(request, '⚠️ Google не дал email.')
        return redirect('login')

    user, created = User.objects.get_or_create(
        email=email,
        defaults={
            'username': email.split('@')[0][:30],
            'first_name': userinfo.get('given_name', ''),
            'last_name': userinfo.get('family_name', ''),
        }
    )
    if created:
        user.set_unusable_password()
        user.save()
        Profile.objects.get_or_create(user=user)

    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    msg = f'🌸 Добро пожаловать, {user.first_name or user.username}!'
    messages.success(request, msg)
    return redirect('home')

from django.contrib.auth.decorators import user_passes_test

@user_passes_test(lambda u: u.is_staff)
def admin_block_user(request, user_id):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=user_id)
    if user != request.user:  # нельзя заблокировать себя
        user.is_active = not user.is_active
        user.save()
        status = 'заблокирован' if not user.is_active else 'разблокирован'
        messages.success(request, f'Пользователь {user.username} {status}')
    else:
        messages.error(request, 'Нельзя заблокировать себя')
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


@user_passes_test(lambda u: u.is_staff)
def admin_delete_user(request, user_id):
    from django.contrib.auth.models import User
    user = get_object_or_404(User, pk=user_id)
    if user != request.user:  # нельзя удалить себя
        username = user.username
        user.delete()
        messages.success(request, f'Пользователь {username} удалён')
    else:
        messages.error(request, 'Нельзя удалить себя')
    return redirect(request.META.get('HTTP_REFERER', '/admin/'))


