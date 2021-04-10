import os
from django.http import Http404, HttpResponse, JsonResponse
from django.shortcuts import render, get_object_or_404



from .models import Product

def home(request):
	return render(request, 'products/home.html')

def product_list_view(request, *args, **kwargs):
	qs= Product.objects.all()
	
	product_list = [{"id":  x.id, "content": x.content} for x in qs]
	data = {
		"response":product_list

	}
	return JsonResponse(data)
