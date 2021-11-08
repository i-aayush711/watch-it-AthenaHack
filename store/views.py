from django.shortcuts import redirect, render
from django.http import JsonResponse

from django.contrib import messages
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User

from .forms import RegisterForm, SellerProductForm
from .models import *
from .utils import cartData, guestOrder

import json
import datetime
import random
import string
import smtplib

# Customer Login
# Create your views here.
def registerUser(request):
    if request.user.is_authenticated:
            return redirect('home')
    form = RegisterForm()
    if request.POST:
        firstname = request.POST['firstname']
        lastname = request.POST['lastname']
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            email = form.cleaned_data.get('email')
            Customer.objects.create(user=user, name=firstname+' '+lastname, email=email)
            login(request, user)
            return redirect('home')
    context = {
        'form':form
    }    
    return render(request, 'store/auth/register.html',context)

def loginUser(request):
    if request.user.is_authenticated:
            return redirect('home')
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            username = user.username
            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request,user_auth)
                return redirect('home')
            else:
                messages.error(request,'Invalid Password')
        except:
            messages.error(request, 'Account Does Not Exists!')

    return render(request, 'store/auth/login.html')

def logoutUser(request):
    logout(request)
    return redirect('login')

def store(request):
    data = cartData(request)
    cartItems = data['cartItems']

    products = Product.objects.all().order_by('id')
    context = {
        'products':products,
        'cartItems':cartItems
    }
    return render(request, 'store/main/home.html', context)

def cart(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context={
        'items':items,
        'order': order,
        'cartItems':cartItems
    }
    return render(request,'store/main/cart.html', context)

def checkout(request):
    data = cartData(request)
    items = data['items']
    order = data['order']
    cartItems = data['cartItems']

    context={
        'items':items,
        'order': order,
        'cartItems':cartItems
    }
    return render(request,'store/main/checkout.html', context)

def updateItem(request):
    data = json.loads(request.body)
    ProductId = data['productId']
    action = data['action']
    
    customer = request.user.customer
    product = Product.objects.get(id=ProductId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    orderItem, created = OrderItem.objects.get_or_create(order=order, seller=product.seller, product=product)
    if action == 'add':
        if orderItem.quantity==product.stock:
            return redirect('cart')
        orderItem.quantity = (orderItem.quantity + 1)
    elif action == 'remove':
        orderItem.quantity = (orderItem.quantity - 1)

    orderItem.save()

    if orderItem.quantity <= 0:
        orderItem.delete()
   
    return JsonResponse('Item Was Added', safe=False)

from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def processOrder(request):
    transaction_id = "T"+datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    data = json.loads(request.body)

    if request.user.is_authenticated:
        customer = request.user.customer

        order, created = Order.objects.get_or_create(customer=customer, complete=False)
    else:
        customer, order = guestOrder(request, data)

    total = data['form']['total']
    order.transaction_id = transaction_id
    if int(total) == int(order.get_cart_total):
        order.complete = True
    order.save()
    
    ShippingAddress.objects.create(
            customer = customer,
            order = order,
            address = data['shipping']['address'],
            city = data['shipping']['city'],
            state = data['shipping']['state'],
            zipcode = data['shipping']['zip']
        )

    return JsonResponse('Payment Completed', safe=False)

def allOrders(request):
    if not request.user.is_authenticated:
            return redirect('login')
    data = cartData(request)
    cartItems = data['cartItems']
    customer = Customer.objects.get(user = request.user)
    orders = OrderItem.objects.filter(order__customer = customer).exclude(order__transaction_id = None)

    context = {
        'orders': orders,
        'cartItems':cartItems
    }
    return render(request, 'store/main/allOrders.html', context)

# Seller:
#--------------------------------------------------------------
def sellerLogin(request):
    if request.user.is_authenticated:
            return redirect('dashboard')
    if request.POST:
        email = request.POST['email']
        password = request.POST['password']
        try:
            user = User.objects.get(email=email)
            username = user.username

            user_auth = authenticate(request, username=username, password=password)
            if user_auth is not None:
                login(request,user_auth)
                return redirect('dashboard')
            else:
                messages.error(request,'Invalid Password')
        except:
            messages.error(request, 'Account Does Not Exists!')

    return render(request, 'seller/authentication/login.html')


# Register:
def sellerRegister(request):
    if request.user.is_authenticated:
            return redirect('dashboard')
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        re_password = request.POST['re_pass']
        try:
            check = Seller.objects.get(email = email)
            if check:
                messages.error(request, "Account Already Exist! Use New Email..")
        except:
            user = Seller()
            if password == re_password:
                user.name = username
                user.email = email
                user.password = password
                user.save()
                return redirect('sellerLogin')
            else:
                messages.error(request, "Password Doesn't Match, Try Again")
                
    return render(request, 'seller/authentication/register.html')

# Logout:
def sellerLogout(request):
    logout(request)
    return redirect('sellerLogin')

# OTP Generation:
def generateOTP():
    otp = random.randrange(100000,999999)
    return otp

# Send Mail:
def SendMail(email, OTP):
    sender = 'coreydoe9@gmail.com'
    password = 'corey@123'
    receiver = email

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()

        smtp.login(sender, password)

        subject = 'OTP for Resetting Your Password'
        body = f'Hello, Your OTP for Resetting Your Account Password is: \n{OTP}'
        message = f'Subject:{subject}\n\n{body}'
        smtp.sendmail(sender, receiver, message)
    
# Forgot Password:
def ForgotPassword(request):
    if request.POST:
        email = request.POST['email']
        try:
            valid = Seller.objects.get(email = email)
            if valid:
                otp = generateOTP()
                request.session['OTP'] = otp
                request.session['TempID'] = valid.id
                try:
                    SendMail(email=email, OTP=otp)
                    messages.success(request, 'We have Mailed You The OTP Please Enter Here!')
                    return redirect('OTP_form')
                except:
                    messages.error(request, 'Some Error Occured Please Try Again Later!')
        except:
            messages.error(request, 'No Such Email Found! Please Enter Correct Email')

    return render(request, 'seller/authentication/forgot_password.html')

def checkOTP(request):
    if 'OTP' not in request.session.keys() and 'TempID' not in request.session.keys():
        return redirect('login')
    else:
        if request.POST:
            userOTP = int(request.POST['otp'])
            sessionOTP = int(request.session['OTP'])
            if userOTP == sessionOTP:
                del request.session['OTP']
                return redirect('password_change')
            else:
                messages.error(request,'OTP Invalid Enter Again')
        return render(request,'seller/authentication/OTP_form.html')

def password_change(request):
    if 'TempID' not in request.session.keys():
        return redirect('login')
    else:
        User = Seller.objects.get(id = request.session['TempID'])
        if request.POST:
            password = request.POST['pwd']
            re_password = request.POST['re_pwd']
            if password == re_password:
                User.password = password
                User.save()
                del request.session['TempID']
                messages.success(request, 'Password Changed! You May Login Now!')
                return redirect('login')
            else:
                messages.error(request, 'Both Password Doesnt Match, Enter Properly')
        return render(request, 'seller/authentication/password_change.html')
      
def sellerDashboard(request):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
    User = Seller.objects.get(user=request.user)
    product_count = Product.objects.filter(seller=User).count()
    
    accepted_orders = OrderItem.objects.filter(seller=User, status='Accepted').count()
    waiting_orders = OrderItem.objects.filter(seller=User, status='Pending Approval').count()
    rejected_orders = OrderItem.objects.filter(seller=User, status='Rejected').count()

    context = {
        'User':User,
        'product_count':product_count,
        'accepted_orders':accepted_orders,
        'waiting_orders':waiting_orders,
        'rejected_orders':rejected_orders,
    }
    return render(request, 'seller/dashboard/home.html', context)
# Sending Customer Email:
def generatePassword():
    data = string.digits + string.ascii_lowercase + string.ascii_uppercase
    password= "".join(random.choices(data, k=8))
    return password

def send_email_to_customer(email, password):
    sender = 'coreydoe9@gmail.com'
    user_password = 'corey@123'
    receiver = email

    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()
        smtp.login(sender, user_password)
        subject = 'Welcome User'
        body = f'Hello,\nYour Password to login E-commerce Website is:  {password}\nYou can Login By Clicking here: http://127.0.0.1:8000/customer/login/ \n\n P.S.:Please Change The Password as you login'
        message = f'Subject:{subject}\n\n{body}'
        smtp.sendmail(sender, receiver, message)

def deleteCustomer(request, pk):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
         
    Customer.objects.get(id = pk).delete()
    return redirect('view_customers')

# Company Products Panel:
def addProduct(request):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
    User = Seller.objects.get(user=request.user)
    form = SellerProductForm()
    if request.POST:
        form = SellerProductForm(request.POST, request.FILES)
        if form.is_valid():
            product = form.save(commit=False)
            product.seller = User
            product.save()
            return redirect('view_products')
    context = {
        'User':User,
        'form':form,
        'action': 'Add',
    }
    return render(request, 'seller/dashboard/product_form.html', context)

def viewProducts(request):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
    User = Seller.objects.get(user=request.user)
    products = Product.objects.filter(seller = User)
    context = {
        'User':User,
        'products':products,
    }

    return render(request, 'seller/dashboard/view_products.html', context)

def updateProduct(request,pk):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
    User = Seller.objects.get(user=request.user)
    product = Product.objects.get(id=pk)
    form = SellerProductForm(instance=product)
    if request.POST:
        form = SellerProductForm(request.POST, request.FILES, instance= product)
        if form.is_valid():
            form.save()
            return redirect('view_products')

    context = {
        'form':form,
        'User':User,
        'action':'Update'
    }
    return render(request, 'seller/dashboard/product_form.html', context)

def deleteProduct(request,pk):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
    Product.objects.get(id=pk).delete()
    return redirect('view_products')

def SellerOrder(request):
    if not request.user.is_authenticated:
        return redirect('sellerLogin')
    seller = Seller.objects.get(user=request.user)
    orders = OrderItem.objects.filter(seller = seller)
    context = {
        'User':seller,
        'allorders': orders,
    }
    return render(request, 'seller/dashboard/orders.html', context)

def AcceptOrder(request, id):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')

    order = OrderItem.objects.get(id = id)
    order.status = 'Accepted'
    order.save()
    return redirect('company_orders')

def RejectOrder(request, id):
    if not request.user.is_authenticated:
            return redirect('sellerLogin')
    order = OrderItem.objects.get(id = id)

    order.status = 'Rejected'
    order.save()
    return redirect('company_orders')
