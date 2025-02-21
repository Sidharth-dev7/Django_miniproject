from django.urls import path
from . import views

urlpatterns=[

    path("registerr",views.registration,name="registerr"),
    path("", views.vieww, name = "view"),
    path("detailview/<str:pk>",views.detailvieww,name="detailview"),
    path('userlog/',views.userlog,name="userlogs"),
    path('logins/',views.loginn,name='logins'),
    path('userreg/',views.reg2,name='userreg'),
    path('add-to-cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart_view, name='cart'),
    path('cart/increment/<int:cart_item_id>/', views.increment_quantity, name='increment_quantity'),
    path('cart/decrement/<int:cart_item_id>/', views.decrement_quantity, name='decrement_quantity'),
    path('logout/', views.user_logout, name='logout'),
    path('cart/delete/<int:item_id>/', views.delete_from_cart, name='delete_from_cart'), # Cart page
    path('checkout/', views.checkout, name='checkout'),  # Checkout page
    path('process-checkout/', views.process_checkout, name='process_checkout'), # Handles order placemen
    path('order-history/', views.order_historyy, name='order_history'),  # Order History page
    path('invoice/<int:order_id>/', views.generate_invoice, name='generate_invoice')
]