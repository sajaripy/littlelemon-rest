from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import Group, User
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import ManagerListSerializer, CategorySerializer, MenuItemSerializer, CartSerializer, CartAddSerializer, CartRemoveSerializer,SingleOrderSerializer, OrderSerializer, OrderInsertSerializer
from .permissions import IsManager, IsDeliveryCrew
from datetime import date
import math


# from rest_framework import generics, status, viewsets
# from rest_framework.response import Response
# from .models import MenuItem, Category
# from rest_framework.decorators import api_view, renderer_classes, permission_classes, throttle_classes
# from django.shortcuts import get_object_or_404
# from .serializers import MenuItemSerializer, CategorySerializer
# from django.core.paginator import Paginator, EmptyPage

# from rest_framework.renderers import TemplateHTMLRenderer, StaticHTMLRenderer
# from rest_framework_csv.renderers import CSVRenderer
# from rest_framework_yaml.renderers import YAMLRenderer

# from rest_framework.permissions import IsAuthenticated, IsAdminUser
# # from rest_framework.decorators import permission_classes

# from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
# from .throttles import TenCalllsPerMinute

# from django.contrib.auth.models import User, Group

# from django.views.generic.edit import UpdateView


from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from django.shortcuts import get_object_or_404
from django.http import HttpResponseBadRequest
from django.contrib.auth.models import Group, User
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import ManagerListSerializer, CategorySerializer, MenuItemSerializer, CartSerializer, CartAddSerializer, CartRemoveSerializer,SingleOrderSerializer, OrderSerializer, OrderInsertSerializer
from .permissions import IsManager, IsDeliveryCrew
from datetime import date
import math

class CategoriesView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [IsAdminUser]

class MenuItemsView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    search_fields = ['title','category__title']
    ordering_fields = ['price', 'category']
    
    def get_permissions(self):
        permission_classes = []
        if self.request.method != "GET":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return [permission() for permission in permission_classes]
    
class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        permission_classes = [IsAuthenticated]
        if self.request.method == "PATCH":
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        if self.request.method == "DELETE":
            permission_classes = [IsAuthenticated, IsAdminUser]
        return[permission() for permission in permission_classes]

    def patch(self, request, *args, **kwargs):
        menuitem = MenuItem.objects.get(pk=self.kwargs['pk'])
        menuitem.featured = not menuitem.featured
        menuitem.save()
        return Response({'message': f'Status of {str(menuitem.title)} changed to {str(menuitem.featured)}'}, status.HTTP_200_OK)

class ManagersView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Manager')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            managers = Group.objects.get(name='Manager')
            managers.user_set.add(user)
            return Response({'message':'User added to Managers'}, status.HTTP_201_CREATED) 

class ManagersRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    queryset = User.objects.filter(groups__name='Manager')

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Manager')
        managers.user_set.remove(user)
        return Response({'message':'User removed Managers'}, status.HTTP_200_OK)

class DeliveryCrewView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    queryset = User.objects.filter(groups__name='Delivery crew')
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]

    def post(self, request, *args, **kwargs):
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            crew = Group.objects.get(name='Delivery crew')
            crew.user_set.add(user)
            return Response({'message':'User added to Delivery Crew'}, status.HTTP_201_CREATED)

class DeliveryCrewRemoveView(generics.DestroyAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = ManagerListSerializer
    permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
    queryset = User.objects.filter(groups__name='Delivery crew')

    def delete(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        user = get_object_or_404(User, pk=pk)
        managers = Group.objects.get(name='Delivery crew')
        managers.user_set.remove(user)
        return Response({'message':'User removed from the Delivery crew'}, status.HTTP_200_OK)

class CartView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Cart.objects.filter(user=self.request.user)

    def post(self, request, *args, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        except:
            return Response({'message':'Item already in cart'}, status.HTTP_409_CONFLICT)
        return Response({'message':'Item added to cart!'}, status.HTTP_201_CREATED)
    
    def delete(self, request, *args, **kwargs):
        if request.data['menuitem']:
           serialized_item = CartRemoveSerializer(data=request.data)
           serialized_item.is_valid(raise_exception=True)
           menuitem = request.data['menuitem']
           cart = get_object_or_404(Cart, user=request.user, menuitem=menuitem )
           cart.delete()
           return Response({'message':'Item removed from cart'}, status.HTTP_200_OK)
        else:
            Cart.objects.filter(user=request.user).delete()
            return Response({'message':'All Items removed from cart'}, status.HTTP_200_OK)

class OrderView(generics.ListCreateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = OrderSerializer

    def get_queryset(self):
        user = self.request.user
        if user.is_superuser or user.groups.filter(name="Manager").exists():
            return Order.objects.all()
        elif user.groups.filter(name='Delivery Crew').exists():  # delivery crew
            return Order.objects.filter(delivery_crew = user)  # only show orders assigned to him
        else:
            return Order.objects.filter(user=user)

    def get_permissions(self):
        if self.request.method == "GET" or "POST":
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        return [permission() for permission in permission_classes]
    
    def post(self, request, *args, **kwargs):
        cart = Cart.objects.filter(user=request.user)
        value_list=cart.values_list()
        if len(value_list) == 0:
            return HttpResponseBadRequest()
        total = math.fsum([float(value[-1]) for value in value_list])
        order = Order.objects.create(user=request.user, status=False, total=total, date=date.today())
        for i in cart.values():
            menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
            orderitem = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'])
            orderitem.save()
        cart.delete()
        return Response({'message':f'Your order has been placed. Your id is {str(order.id)}'}, status.HTTP_201_CREATED)

class SingleOrderView(generics.RetrieveUpdateAPIView):
    throttle_classes = [AnonRateThrottle, UserRateThrottle]
    serializer_class = SingleOrderSerializer
    
    def get_permissions(self):
        user = self.request.user
        method = self.request.method
        order = Order.objects.get(pk=self.kwargs['pk'])
        if user == order.user and method == 'GET':
            permission_classes = [IsAuthenticated]
        elif method == 'PUT' or method == 'DELETE':
            permission_classes = [IsAuthenticated, IsManager | IsAdminUser]
        else:
            permission_classes = [IsAuthenticated, IsDeliveryCrew | IsManager | IsAdminUser]
        return[permission() for permission in permission_classes] 

    def get_queryset(self, *args, **kwargs):
            query = OrderItem.objects.filter(order_id=self.kwargs['pk'])
            return query


    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response({'message':'Status of order #'+ str(order.id)+' changed to '+str(order.status)}, status.HTTP_201_CREATED)

    def put(self, request, *args, **kwargs):
        serialized_item = OrderInsertSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        order_pk = self.kwargs['pk']
        crew_pk = request.data['delivery_crew'] 
        order = get_object_or_404(Order, pk=order_pk)
        crew = get_object_or_404(User, pk=crew_pk)
        order.delivery_crew = crew
        order.save()
        return Response({'message':str(crew.username)+' was assigned to order #'+str(order.id)}, status.HTTP_201_CREATED)

    def delete(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order_number = str(order.id)
        order.delete()
        return Response({'message':f'Order #{order_number} was deleted'}, status.HTTP_200_OK)



# @api_view() 
# @renderer_classes([TemplateHTMLRenderer])
# def menu(request):
#     items = MenuItem.objects.select_related('category').all()
#     serialized_item = MenuItemSerializer(items, many=True)
#     return Response({'data':serialized_item.data}, template_name='menu-items.html')

# @api_view(['GET'])
# @renderer_classes([StaticHTMLRenderer])
# def welcome(request):
#     data = '<html><body><h1>Welcome To Little Lemon API Project</h1></body></html>'
#     return Response(data)


# @api_view()
# def category_detail(request, pk):
#     category = get_object_or_404(Category,pk=pk)
#     serialized_category = CategorySerializer(category)
#     return Response(serialized_category.data)

# # class MenuItemsView(generics.ListCreateAPIView):    
# #     def list(self, request):
# #         if request.method == 'GET':
# #             queryset = MenuItem.objects.select_related('category').all()
# #             serializer_class = MenuItemSerializer(queryset, many=True)
# #             return Response(serializer_class.data)
# #     def create(self, request):
# #         if request.method == 'POST':
# #             serializer_class = MenuItemSerializer(data=request.data)
# #             serializer_class.is_valid(raise_exception=True)
# #             serializer_class.save()
# #             return Response(serializer_class.data, status.HTTP_201_CREATED)

 
# class MenuItemsViewSet(viewsets.ModelViewSet):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
#     ordering_fields=['price','featured']
#     search_fields=['title','category__title']
#     # throttle_classes = [AnonRateThrottle, UserRateThrottle]
#     def get_throttles(self):
#         if self.action == 'create': #create for POST calls and list for GET calls
#             throttle_classes = [UserRateThrottle]
#         else:
#             throttle_classes = []
#         return [throttle() for throttle in throttle_classes]
#     def list(self, request):
#         if request.method == 'GET':
#             queryset = MenuItem.objects.select_related('category').all()
#             serializer_class = MenuItemSerializer(queryset, many=True)
#             return Response(serializer_class.data)

#     def create(self, request, pk):
#         if request.method == 'POST' and request.user.groups.filter(name='Manager').exists():
#             serialized_item = MenuItemSerializer(data=request.data)
#             # serialized_item.is_valid(raise_exception=True)
#             serialized_item.save()
#             return Response(serialized_item.data, status.HTTP_201_CREATED)
#         return Response({"message": "error"}, status.HTTP_403_FORBIDDEN)
    
# #     def CandidatesCreate(request, *args, **kwargs):
# # parser_classes = (FileUploadParser,)

# # if request.method == 'PATCH' or request.method == 'POST':

# #     serializer = CandidatesSerializer(data=request.data)
# #     if serializer.is_valid():
# #         instance, created = Candidates.objects.update_or_create(email=serializer.validated_data.get('email', None), defaults=serializer.validated_data) 
# #         if not created:
# #             serializer.update(instance, serializer.validated_data)
# #         return Response(serializer.data, status=status.HTTP_202_ACCEPTED)
# #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

#     def partial_update(self, request, *args, **kwargs):
#         # serialized_item = MenuItemSerializer(data=request.data)
#         # queryset = MenuItem.objects.select_related('pk')
#         # serializer_class = MenuItemSerializer(queryset, many=True)
#         menu_object = self.get_object()
#         data = MenuItemSerializer(data=request.data)
#         if data.is_valid():
#             if request.method == 'PATCH' and request.user.groups.filter(name='Manager').exists():
#                 try:
#                     category_object = Category.objects.get(category_id = data["category_id"])
#                     menu_object.category_object = category_object
#                 except KeyError:
#                     pass
#                 menu_object.title = data.get("title", menu_object.title)
#                 menu_object.price = data.get("price", menu_object.price)
#                 menu_object.featured = data.get("featured", menu_object.featured)
#                 menu_object.category_id = data.get("category_id", menu_object.category_id)
                    
#                         # serialized_item = MenuItemSerializer(data=request.data)
#                         # serialized_item.get('id')
#                 # data.is_valid(raise_exception=True)
#                 # menu_object.save()
#                 # serialized_item = MenuItemSerializer(menu_object)
#             return Response(data.data, status.HTTP_201_CREATED)
#         return Response({"message": "error"}, status.HTTP_403_FORBIDDEN)
    
#         #     serialized_item = MenuItemSerializer(data=request.data)
#         #     # serialized_item.is_valid(raise_exception=True)
#         #     # serialized_item.save()
#         #     if serialized_item.is_valid():
#         #         MenuItem.objects.update(id=serialized_item.validated_data.get('id', pk), defaults=serialized_item.validated_data)
#         #         # serialized_item.update(instance, serialized_item.validated_data)
#         #         serialized_item.save()
#         #     return Response(serialized_item.data, status=status.HTTP_202_ACCEPTED)
#         # return Response({"message": "error"}, status.HTTP_403_FORBIDDEN)
    


# class SingleMenuItemView(viewsets.ModelViewSet):
#     queryset = MenuItem.objects.all()
#     serializer_class = MenuItemSerializer
    
#     # def update(self, request):
#     #     if request.method == 'PATCH' and request.user.groups.filter(name='Manager').exists():
#     #         serialized_item = MenuItemSerializer(data=request.data)
#     #         serialized_item.is_valid(raise_exception=True)
#     #         serialized_item.save()
#     #         return Response(serialized_item.data, status.HTTP_201_CREATED)
#     #     return Response({"message": "error"}, status.HTTP_403_FORBIDDEN)


# # from django.shortcuts import render
# # from rest_framework.response import Response
# # from rest_framework import status
# # from rest_framework.decorators import api_view
# # from rest_framework.views import APIView

# # Create your views here.
# @api_view(['GET','POST'])
# # @renderer_classes([CSVRenderer])
# # @renderer_classes([YAMLRenderer])
# def menu_items(request):
#     if request.method == 'GET':
#         items = MenuItem.objects.select_related('category').all()
#         category_name = request.query_params.get('category')
#         to_price = request.query_params.get('to_price')
#         search = request.query_params.get('search')
#         ordering = request.query_params.get('ordering')
#         perpage = request.query_params.get('perpage', default=2)
#         page = request.query_params.get('page', default=1)
#         if category_name:
#             items = items.filter(category__title=category_name)
#         if to_price:
#             items = items.filter(price__lte=to_price)
#         if search:
#             items = items.filter(title__icontains=search)
#         if ordering:
#             ordering_fields = ordering.split(",")
#             items = items.order_by(*ordering_fields)
        
#         # paginator = Paginator(items, per_page=perpage)
#         # try:
#         #     items = paginator.page(number=page)
#         # except EmptyPage:
#         #     items = []
#         serialized_item = MenuItemSerializer(items, many=True, context={'request': request})
#         return Response(serialized_item.data)
#     if request.method == 'POST' and request.user.groups.filter(name='Manager').exists():
#         serialized_item = MenuItemSerializer(data=request.data)
#         serialized_item.is_valid(raise_exception=True)
#         serialized_item.save()
#         return Response(serialized_item.data, status.HTTP_201_CREATED)
#     return Response({"message": "error"}, status.HTTP_403_FORBIDDEN)

# @api_view(['GET','PUT','PATCH'])
# def single_item(request, pk):
#     # menu_object = self.get_object()
#     data = MenuItemSerializer(data=request.data)
#     item = get_object_or_404(MenuItem,pk=pk)
#     serialized_item = MenuItemSerializer(data=item)
#     if request.method == 'GET':
#         return Response(serialized_item.data)
#     def patch(self, request, *args, **kwargs):
#         menu_object = MenuItem.objects.get()
#         data = MenuItemSerializer(data=request.data)
#     # elif request.method == 'PATCH' and request.user.groups.filter(name='Manager').exists():
#     #     # serialized_item = MenuItemSerializer(data=request.data)
#     #     data.is_valid(raise_exception=True)
#     #     data.save()
#     #     return Response(serialized_item.data, status.HTTP_201_CREATED)
#     # else:
#     #     return Response({"message": "error"}, status.HTTP_403_FORBIDDEN)
#     return Response(serialized_item.data)

# @api_view()
# @permission_classes([IsAuthenticated])
# def secret(request):
#     return Response({'message':'Some secret message'})

# @api_view()
# @permission_classes([IsAuthenticated])
# def manager_view(request):
#     if request.user.groups.filter(name='Manager').exists():
#         return Response({"message": "Only Manager Should See This"})
#     else:
#         return Response({"message": "You are not authorized"}, 403)

# @api_view()
# @throttle_classes([AnonRateThrottle])
# def throttle_check(request):
#     return Response({"message":"successful"})

# @api_view()
# @permission_classes([IsAuthenticated])
# @throttle_classes([TenCalllsPerMinute])
# def throttle_check_auth(request):
#     return Response({"message": "message for the logged in users only"})

# @api_view(['POST', 'DELETE'])
# @permission_classes([IsAdminUser])
# def managers(request):
#     username = request.data['username']
#     if username:
#         user = get_object_or_404(User, username=username)
#         managers = Group.objects.get(name='Manager')
#         if request.method == 'POST':
#             managers.user_set.add(user)
#         elif request.method == 'DELETE':
#             managers.user_set.remove(user)
#         return Response({"message": "ok"})
#     return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)