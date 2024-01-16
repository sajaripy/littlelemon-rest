from rest_framework import generics
from rest_framework.response import Response
from .models import MenuItem, Category
from rest_framework.decorators import api_view
from django.shortcuts import get_object_or_404
from .serializers import MenuItemSerializer, CategorySerializer

@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category,pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)

class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.select_related('category').all()
    serializer_class = MenuItemSerializer

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer