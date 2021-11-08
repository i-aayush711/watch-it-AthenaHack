from django.db import models
from django.contrib.auth.models import User
from PIL import Image
# Create your models here.
class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField('Customer Name', max_length=200, null=True)
    email = models.EmailField('Customer Email', max_length=200, null=True)

    def __str__(self):
        return self.name

class Seller(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True,)
    name = models.CharField('Supplier Name', max_length=200, null=True)
    email = models.EmailField('Supplier Email', max_length=200, null=True)

    def __str__(self):
        return self.name
    
class Categories(models.Model):
    name = models.CharField(max_length=50, null=True)

    def __str__(self):
        return self.name

class Product(models.Model):
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank=True, null=True)
    name = models.CharField("Product Name", max_length=200, null=True)
    price = models.PositiveIntegerField()
    stock = models.PositiveIntegerField(default=0)
    category = models.ForeignKey(Categories, on_delete=models.SET_NULL, null=True)
    image = models.ImageField(upload_to='products', null=True, blank=True)

    def __str__(self):
        return self.name

    @property
    def imageURL(self):
        try:
            url = self.image.url
        except:
            url= ""
        return url

class Order(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    date_ordered= models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, null=True)

    def __str__(self):
        return str(self.id)

    @property
    def get_cart_total(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderitems])
        return total

    @property
    def get_cart_items(self):
        orderitems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderitems])
        return total

class OrderItem(models.Model):
    CHOICES = [
        ('Accepted', 'Accepted'),
        ('Pending Approval', 'Pending Approval'),
        ('Rejected', 'Rejected')
    ]
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, blank=True, null=True)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)
    status = models.CharField('Order Status', max_length = 30 , choices=CHOICES, default="Pending Approval")

    def __str__(self):
        return f'{self.product}:{self.order}'

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total
    
class ShippingAddress(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=200, null=True)
    city = models.CharField(max_length=200, null=True)
    state = models.CharField(max_length=200, null=True)
    zipcode = models.CharField(max_length=200, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.customer}:{self.address}'

