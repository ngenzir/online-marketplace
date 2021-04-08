import os


from django.shortcuts import render, get_object_or_404


def home(request):
	return render("products/home.html")