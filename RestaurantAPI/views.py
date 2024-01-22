from rest_framework import generics, status
from rest_framework.response import Response
from .models import MenuItem, Category
from rest_framework.decorators import api_view, renderer_classes
from django.shortcuts import get_object_or_404
from .serializers import MenuItemSerializer, CategorySerializer

from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
from rest_framework_csv.renderers import CSVRenderer
from rest_framework_yaml.renderers import YAMLRenderer

@api_view() 
@renderer_classes([TemplateHTMLRenderer])
def menu(request):
    items = MenuItem.objects.select_related('category').all()
    serialized_item = MenuItemSerializer(items, many=True)
    return Response({'data':serialized_item.data}, template_name='menu-items.html')

@api_view(['GET'])
@renderer_classes([StaticHTMLRenderer])
def welcome(request):
    data = '<html><body><h1>Welcome To Little Lemon API Project</h1></body></html>'
    return Response(data)


@api_view()
def category_detail(request, pk):
    category = get_object_or_404(Category,pk=pk)
    serialized_category = CategorySerializer(category)
    return Response(serialized_category.data)

# class MenuItemsView(generics.ListCreateAPIView):    
#     def list(self, request):
#         if request.method == 'GET':
#             queryset = MenuItem.objects.select_related('category').all()
#             serializer_class = MenuItemSerializer(queryset, many=True)
#             return Response(serializer_class.data)
#     def create(self, request):
#         if request.method == 'POST':
#             serializer_class = MenuItemSerializer(data=request.data)
#             serializer_class.is_valid(raise_exception=True)
#             serializer_class.save()
#             return Response(serializer_class.data, status.HTTP_201_CREATED)

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer


# from django.shortcuts import render
# from rest_framework.response import Response
# from rest_framework import status
# from rest_framework.decorators import api_view
# from rest_framework.views import APIView

# Create your views here.
@api_view(['GET','POST'])
# @renderer_classes([CSVRenderer])
# @renderer_classes([YAMLRenderer])
def menu_items(request):
    if request.method == 'GET':
        items = MenuItem.objects.select_related('category').all()
        category_name = request.query_params.get('category')
        to_price = request.query_params.get('to_price')
        search = request.query_params.get('search')
        ordering = request.query_params.get('ordering')
        if category_name:
            items = items.filter(category__title=category_name)
        if to_price:
            items = items.filter(price__lte=to_price)
        if search:
            items = items.filter(title__icontains=search)
        if ordering:
            ordering_fields = ordering.split(",")
            items = items.order_by(*ordering_fields)
        serialized_item = MenuItemSerializer(items, many=True, context={'request': request})
        return Response(serialized_item.data)
    if request.method == 'POST':
        serialized_item = MenuItemSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        serialized_item.save()
        return Response(serialized_item.data, status.HTTP_201_CREATED)

# @api_view(['GET','PUT'])
# def single_item(request, id):
#     item = get_object_or_404(MenuItem,pk=id)
#     serialized_item = MenuItemSerializer(item)
#     return Response(serialized_item.data)
