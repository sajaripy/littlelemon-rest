from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponse, HttpResponseRedirect
from .models import Menu, About
from restaurant.forms import BookForm

# Create your views here.
def home(request):
    return HttpResponse("Hello")

def index(request):
    return render(request, 'index.html', {})

def menu(request):
    menu_items = Menu.objects.all()
    items_dict = {"menu":menu_items}
    return render(request, "menu.html", items_dict)

def display_menu_item(request, pk=None):
    if pk:
        menu_item = Menu.objects.get(pk=pk)
    else:
        menu_item = ''
    return render(request, "menu_item.html", {"menu_item":menu_item})

def about(request):
    about = About.objects.all()
    about_dict = {"about":about}
    return render(request, "about.html", about_dict)

def contact(request):
    return render(request, "contact.html", {})

def book(request):
    form = BookForm()
    if request.method == 'POST':
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Form submission successful')
            # return redirect('/')
            return HttpResponseRedirect("/book")
    context = {"form":form}
    return render(request, "book.html", context)