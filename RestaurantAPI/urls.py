from django.urls import path
from . import views

from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/category', views.CategoriesView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('groups/manager/users', views.ManagersView.as_view()),
    path('groups/manager/users/<int:pk>', views.ManagersRemoveView.as_view()),
    path('groups/delivery-crew/users', views.DeliveryCrewView.as_view()),
    path('groups/delivery-crew/users/<int:pk>', views.DeliveryCrewRemoveView.as_view()),
    path('cart/menu-items', views.CartView.as_view()),
    path('order', views.OrderView.as_view()),
    path('orders/<int:pk>', views.SingleOrderView.as_view()),
    # # path('menu-items', views.menu_items),
    # # path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    # # path('menu-items/<int:pk>', views.single_item),
    # path('category/<int:pk>', views.category_detail, name='category-detail'),
    # path('menu', views.menu),
    # path('welcome', views.welcome),
    # path('menu-items',views.menu_items),
    # path('menu-items/<int:pk>',views.single_item),
    # path('secret', views.secret),
    # path('api-token-auth', obtain_auth_token),
    # path('manager-view', views.manager_view),
    # path('throttle-check', views.throttle_check),
    # path('throttle-check-auth', views.throttle_check_auth),
    # path('groups/manager/users', views.managers),
]