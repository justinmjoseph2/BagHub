from django.urls import path
from .views import contact_view, reset_password
from eapp.models import contact
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('customer_dashboard/',views.customer_dashboard,name='customer_dashboard'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('change_password/', views.change_password, name='change_password'),
    path('forgot_password/', views.forgot_password, name='forgot_password'),
    path('reset_password/<uidb64>/<token>/', views.reset_password, name='reset_password'),
    path('logout/', views.user_logout, name='logout'),
    path('edit_customer/', views.edit_customer, name='edit_customer'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('address/', views.address_list, name='address_list'),
    path('address/add/', views.address_create, name='address_create'),
    path('contact/', contact_view, name='contact'),
    path('address/delete/<int:pk>/', views.address_delete, name='address_delete'),
    path("cart/", views.cart, name="cart"),
    path('add_to_cart/', views.add_to_cart, name='add_to_cart'),
    path('cart/increase/<int:cart_item_id>/', views.increase_quantity, name='increase_quantity'),
    path('cart/decrease/<int:cart_item_id>/', views.decrease_quantity, name='decrease_quantity'),
    path('delete_item_in_cart/<int:id>/', views.delete_item_in_cart, name='delete_item_in_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('order_list/', views.order_list, name='order_list'),
    path('order_detail/<int:order_id>/', views.order_detail, name='order_detail'),
    path('product_list',views.product_list,name='product_list'),
    path('address/<int:pk>/', views.address_edit, name='address_edit'),
    path('search/', views.search_results, name='search_results'),
    path('category/<int:category_id>/', views.category_products, name='category_products'),
    path('subcategory/<int:subcategory_id>/', views.subcategory_products, name='subcategory_products'),
    path('products/filter/', views.filter_products, name='filter_products'),
    path('supplier/', views.supplier_index, name='supplier_index'),
    path('button/', views.button, name='button'),
    path('typography/', views.typography, name='typography'),
    path('products/', views.products, name='products'),
    path('widget/', views.widget, name='widget'),
    path('form/', views.form, name='form'),
    path('table/', views.table, name='table'),
    path('chart/', views.chart, name='chart'),
    path('signin/', views.signin, name='signin'),
    path('not_found/', views.not_found, name='not_found'),
    path('blank/', views.blank, name='blank'),
    path('reset_pass/', views.reset_pass, name='reset_pass'),
    path('purchaseOrders/', views.purchaseOrders, name='purchaseOrders'),
    path('accept_purchase_order/', views.accept_purchase_order, name='accept_purchase_order'),
    path('recentOredrs/', views.recentOredrs, name='recentOredrs'),
    path('products_graph/<int:product_id>/', views.products_graph, name='products_graph'),
    path('products_weekly_sales/<int:product_id>/<str:month>/', views.products_weekly_sales, name='products_weekly_sales'),
    path('cancel_order/<int:order_id>/', views.cancel_order, name='cancel_order'),
]

    

