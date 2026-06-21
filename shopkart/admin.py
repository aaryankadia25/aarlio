from django.contrib import admin
from .models import Category,Product,Customer,Wishlist, Order, OrderItem
from .models import Coupon
admin.site.register(Category)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'price')
    list_filter = ('category',)
    search_fields = ('title',)

admin.site.site_header = "MyProject Admin"
admin.site.site_title = "MyProject Admin Portal"
admin.site.index_title = "Welcome to MyProject Admin Dashboard"

admin.site.register(Customer)

admin.site.register(Wishlist)

admin.site.register(Order)

admin.site.register(OrderItem)

admin.site.register(Coupon)





