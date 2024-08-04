from django.shortcuts import render,redirect
from django.contrib import messages

def REGISTER(request):
	return render(request, "internship/intern_register.html")