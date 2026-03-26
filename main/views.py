from django.shortcuts import render, redirect
from django.http import HttpResponse


def home(request):
    return HttpResponse("HOME OK")


def catalog(request):
    return HttpResponse("CATALOG OK")


def about(request):
    return HttpResponse("ABOUT OK")


def contacts(request):
    return HttpResponse("CONTACTS OK")


def cart(request):
    return HttpResponse("CART OK")


def add_to_cart(request, pk):
    return HttpResponse("ADD OK")


def update_cart(request, pk):
    return HttpResponse("UPDATE OK")


def remove_from_cart(request, pk):
    return HttpResponse("REMOVE OK")


def checkout(request):
    return HttpResponse("CHECKOUT OK")


def order_success(request, receipt_code):
    return HttpResponse("SUCCESS OK")


def login_view(request):
    return HttpResponse("LOGIN OK")


def logout_view(request):
    return HttpResponse("LOGOUT OK")


def register_view(request):
    return HttpResponse("REGISTER OK")


def profile(request):
    return HttpResponse("PROFILE OK")


def test_view(request):
    return HttpResponse("TEST OK")