from django.urls import path
from . import views

from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/', views.loginUser, name="login"),
    path('register/', views.registerUser, name="register"),
    path('logout/', views.logoutUser, name="logout"),
    path('', views.store, name="home"),
    path('cart/', views.cart, name="cart"),
    path('checkout/', views.checkout, name="checkout"),
    path('update_item/', views.updateItem, name="update_item"),
    path('process_order/', views.processOrder, name="process_order"),
    path('all_orders/', views.allOrders, name='allOrders'),
    # Seller Section
    path('dashboard/', views.sellerDashboard, name='dashboard'),
    # Authentication Purpose
    path('dashboard/login/', views.sellerLogin, name='sellerLogin'),
    path('dashboard/register/', views.sellerRegister, name='sellerRegister'),
    path('dashboard/logout/', views.logout, name="sellerlogout"),
    # Forgot Passoword
    path('dashboard/forgot_password/', views.ForgotPassword, name='forgot_password'),
    path('dashboard/otp_check/', views.checkOTP, name='OTP_form'),
    path('dashboard/change_password/', views.password_change, name='password_change'),
    # Products Panel by Company
    path('dashboard/addproduct/', views.addProduct, name='add_product'),
    path('dashboard/products/', views.viewProducts, name='view_products'),
    path('dashboard/updateproduct/<int:pk>', views.updateProduct, name='update_product'),
    path('dashboard/deleteproduct/<int:pk>', views.deleteProduct, name='delete_product'),
    # Order Panel in Dashboard
    path('dashboard/orders/', views.SellerOrder, name='company_orders'),
    path('dashboard/acceptorder/<int:id>', views.AcceptOrder, name='accept_order'),
    path('dashboard/rejectorder/<int:id>', views.RejectOrder, name='reject_order'),

] + static(settings.STATIC_URL, document_root = settings.STATIC_ROOT)