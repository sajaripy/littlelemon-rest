from rest_framework import serializers
from .models import MenuItem, Cart, Category, Order, OrderItem
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError


class MenuItemSerializer(serializers.ModelSerializer):

    class Meta():
        model = MenuItem
        fields = ['id','title','price','featured','category']
        depth = 1

class CategorySerializer(serializers.ModelSerializer):
    class Meta():
        model = Category
        fields = ['slug']

class ManagerListSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['id','username','email']

class CartHelpSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['id','title','price']

class CartSerializer(serializers.ModelSerializer):
    menuitem = CartHelpSerializer()
    class Meta():
        model = Cart
        fields = ['menuitem','quantity','price']
        
class CartAddSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem','quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta():
        model = Cart
        fields = ['menuitem']

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']

class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    class Meta():
        model = Order
        fields = ['id','user','total','status','delivery_crew','date']

class SingleHelperSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['title','price']
class SingleOrderSerializer(serializers.ModelSerializer):
    menuitem = SingleHelperSerializer()
    class Meta():
        model = OrderItem
        fields = ['menuitem','quantity']


class OrderInsertSerializer(serializers.ModelSerializer):
    class Meta():
        model = Order
        fields = ['delivery_crew']
        
        
# from rest_framework import serializers
# from .models import MenuItem, Category
# from decimal import Decimal
# from rest_framework.validators import UniqueValidator, UniqueTogetherValidator
# import bleach

# class CategorySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Category
#         fields = ['id','slug','title']

# class MenuItemSerializer(serializers.HyperlinkedModelSerializer):
#     # stock = serializers.IntegerField(source='inventory')
#     price_after_tax = serializers.SerializerMethodField(method_name = 'calculate_tax')
#     category = CategorySerializer(read_only=True)
#     category_id = serializers.IntegerField() #write_only=True
#     # price = serializers.DecimalField(max_digits=6, decimal_places=2, min_value=2) #data_validation_Method 1: Conditions in the field
    
#     # #data_validation_Method:3 Using validate_field() method
#     # def validate_price(self, value):
#     #     if (value < 2):
#     #         raise serializers.ValidationError('Price should not be less than 2.0')
#     # def validate_stock(self, value):
#     #     if (value < 0):
#     #         raise serializers.ValidationError('Stock cannot be negative')
#     def validate_title(self, value):  #data_sanitization
#         return bleach.clean(value)
    
#     # def validate(self, attrs):  #data_validation_Method 4: Using the validate() method
#     #     attrs['title'] = bleach.clean(attrs['title'])  #data_sanitization
#     #     if(attrs['price']<2):
#     #         raise serializers.ValidationError('Price should not be less than 2.0')
#     #     if(attrs['inventory']<0):
#     #         raise serializers.ValidationError('Stock cannot be negative')
#     #     return super().validate(attrs)
    
#     # title = serializers.CharField(max_length=255, validators=[UniqueValidator(queryset=MenuItem.objects.all())])
    
#     class Meta:
#         model = MenuItem
#         fields = ['id','title','price','featured','price_after_tax','category','category_id']
#         # depth = 1
#         extra_kwargs = { #data_validation_Method 2: Using keyword arguments in the Meta class: for this to work comment out the stock definition line.
#             'price': {'min_value': 2},
#             # 'stock': {'source':'inventory', 'min_value': 0},
#         }
#         # extra_kwargs = {
#         #     'title': {
#         #         'validators': [UniqueValidator(queryset=MenuItem.objects.all())]
#         #     }
#         # }
        
#         # validators = [
#         #     UniqueTogetherValidator(
#         #         queryset=MenuItem.objects.all(),
#         #         fields=['title', 'price']
#         #     ),
#         # ]
    
#     def calculate_tax(self, product:MenuItem):
#         return product.price * Decimal(1.1)