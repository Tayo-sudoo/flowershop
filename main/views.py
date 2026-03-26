from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.models import User

import urllib.parse
import urllib.request
import secrets
import json
import base64

from .models import Flower, Category, Order, OrderItem, Review, Profile
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from .ai_helper import get_ai_response


# =========================
# ОСНОВНЫЕ СТРАНИЦЫ
# =========================

def home(request):
    flowers = Flower.objects.filter(available=True).select_related('category')[:8]
    return render(request, 'main/home.html', {'flowers': flowers})


def catalog(request):
    flowers = Flower.objects.all().select_related('category')
    categories = Category.objects.all()

    search = request.GET.get('search')
    category = request.GET.get('category')

    if search:
        flowers = flowers.filter(name__icontains=search)

    if category:
        flowers = flowers.filter(category__slug=category)

    return render(request, 'main/catalog.html', {
        'flowers': flowers,
        'categories': categories
    })


def flower_detail(request, pk):
    flower = get_object_or_404(Flower, pk=pk)
    reviews = Review.objects.filter(flower=flower, is_approved=True)

    return render(request, 'main/flower_detail.html', {
        'flower': flower,
        'reviews': reviews
    })


# =========================
# AUTH
# =========================

def login_view(request):
    form = CustomAuthenticationForm(request, data=request.POST or None)

    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        return redirect('home')

    return render(request, 'main/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('home')


def register_view(request):
    form = CustomUserCreationForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect('home')

    return render(request, 'main/register.html', {'form': form})


# =========================
# КОРЗИНА
# =========================

def cart(request):
    cart = request.session.get('cart', {})
    items = []
    total = 0

    for fid, qty in cart.items():
        flower = Flower.objects.filter(id=fid).first()
        if flower:
            subtotal = flower.price * qty
            total += subtotal
            items.append({'flower': flower, 'qty': qty, 'total': subtotal})

    return render(request, 'main/cart.html', {'items': items, 'total': total})


def add_to_cart(request, pk):
    cart = request.session.get('cart', {})
    cart[str(pk)] = cart.get(str(pk), 0) + 1
    request.session['cart'] = cart
    return redirect('catalog')


# =========================
# ЗАКАЗ
# =========================

@login_required
def checkout(request):
    cart = request.session.get('cart', {})

    if not cart:
        return redirect('cart')

    if request.method == 'POST':
        order = Order.objects.create(user=request.user, total_price=0)

        total = 0
        for fid, qty in cart.items():
            flower = Flower.objects.get(id=fid)
            OrderItem.objects.create(
                order=order,
                flower=flower,
                quantity=qty,
                price=flower.price
            )
            total += flower.price * qty

        order.total_price = total
        order.save()

        request.session['cart'] = {}

        return redirect('order_success', receipt_code=order.receipt_code)

    return render(request, 'main/checkout.html')


def order_success(request, receipt_code):
    order = get_object_or_404(Order, receipt_code=receipt_code)
    return render(request, 'main/order_success.html', {'order': order})


# =========================
# GOOGLE LOGIN (FIX)
# =========================

def google_login(request):
    state = secrets.token_urlsafe(16)
    request.session['state'] = state

    redirect_uri = request.build_absolute_uri('/auth/google/callback/')

    params = {
        'client_id': settings.GOOGLE_CLIENT_ID,
        'redirect_uri': redirect_uri,
        'response_type': 'code',
        'scope': 'openid email profile',
        'state': state,
    }

    url = "https://accounts.google.com/o/oauth2/v2/auth?" + urllib.parse.urlencode(params)
    return redirect(url)


# =========================
# PAYME (БЕЗ ОШИБОК)
# =========================

PAYME_SECRET = "TEST_KEY"


@csrf_exempt
def payme(request):
    try:
        data = json.loads(request.body or "{}")
    except:
        return JsonResponse({"error": "invalid json"})

    method = data.get('method')
    params = data.get('params', {})
    request_id = data.get('id')

    def res(result=None, error=None):
        return JsonResponse({
            "jsonrpc": "2.0",
            "id": request_id,
            "result": result,
            "error": error
        })

    # AUTH
    auth = request.headers.get('Authorization')
    if not auth:
        return res(error={"code": -32504})

    key = base64.b64decode(auth.split()[1]).decode()
    if key != PAYME_SECRET:
        return res(error={"code": -32504})

    # CHECK
    if method == "CheckPerformTransaction":
        order_id = params.get('account', {}).get('order_id')

        if not Order.objects.filter(id=order_id).exists():
            return res(error={"code": -31050})

        return res(result={"allow": True})

    # CREATE
    if method == "CreateTransaction":
        order_id = params.get('account', {}).get('order_id')

        try:
            order = Order.objects.get(id=order_id)
        except Order.DoesNotExist:
            return res(error={"code": -31050})

        order.transaction_id = params.get('id')
        order.save()

        return res(result={"state": 1})

    # PERFORM
    if method == "PerformTransaction":
        transaction_id = params.get('id')

        try:
            order = Order.objects.get(transaction_id=transaction_id)
        except Order.DoesNotExist:
            return res(error={"code": -31050})

        order.status = 'paid'
        order.save()

        return res(result={"state": 2})

    return res(error={"code": -32601})