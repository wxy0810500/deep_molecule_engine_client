# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect


def tempRoot(request):
    return redirect('/covid19')


def index(request):
    return render(request, 'index.html')
