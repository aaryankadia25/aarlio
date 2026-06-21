from django.shortcuts import render,redirect, get_object_or_404
from .models import Category,Product
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import Customer,Cart, Wishlist, Order, OrderItem
from .models import Coupon

def register(request):
    if request.method == "POST":
        name = request.POST['user_name']
        mobile = request.POST['user_mobile']
        email = request.POST['user_email']
        password = request.POST['user_password']
        address = request.POST['user_address']

        last_customer = Customer.objects.all().order_by('id').last()

        if last_customer:
            new_id = last_customer.id + 1
        else:
            new_id = 1

        user_id = "CUST" + str(1000 + new_id)

        # check email already exists
        if Customer.objects.filter(user_email=email).exists():
            return render(request, 'register.html', {'msg':'Email already exists'})

        Customer.objects.create(
            user_id=user_id,
            user_name=name,
            user_mobile=mobile,
            user_email=email,
            user_password=password,
            user_address=address
        )
        

        return redirect('login')

    return render(request,'register.html')

def user_login(request):
    if request.method == "POST":
        email = request.POST['user_email']
        password = request.POST['user_password']

        user = Customer.objects.filter(
            user_email=email,
            user_password=password
        ).first()

        if user:
            request.session['customer_id'] = user.id
            request.session['customer_name'] = user.user_name
            return redirect('home')
        else:
            return render(request,'login.html',{'msg':'Invalid Email or Password'})

    return render(request,'login.html')

def forgot_password(request):
    if request.method == "POST":
        email = request.POST['user_email']

        user = Customer.objects.filter(user_email=email).first()

        if user:
            return redirect('reset_password', email=email)
        else:
            return render(request,'forgot_password.html',{'msg':'Email not found'})

    return render(request,'forgot_password.html')


def reset_password(request, email):
    user = Customer.objects.get(user_email=email)

    if request.method == "POST":
        new_pass = request.POST['new_password']
        confirm_pass = request.POST['confirm_password']

        if new_pass == confirm_pass:
            user.user_password = new_pass
            user.save()
            return redirect('login')
        else:
            return render(request,'reset_password.html',{'msg':'Passwords do not match'})

    return render(request,'reset_password.html',{'email':email})

def user_logout(request):
    logout(request)
    return redirect('login')

def home(request):
    products = Product.objects.all()[:8]  # show limited products
    categories = Category.objects.all()

    return render(request, 'home.html', {
        "products": products,
        "categories": categories
    })

from .models import Cart, Customer, Product

def add_to_cart(request, pid):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)
    product = Product.objects.get(id=pid)

    item = Cart.objects.filter(customer=customer, product=product).first()

    if item:
        item.quantity += 1
        item.save()
    else:
        Cart.objects.create(
            customer=customer,
            product=product,
            quantity=1
        )

    return redirect('cart')

def cart(request):

    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    items = Cart.objects.filter(customer=customer)

    total = 0

    for i in items:
        total += i.product.price * i.quantity

    # COUPON DISCOUNT
    discount = request.session.get('coupon_discount', 0)

    # FINAL TOTAL
    final_total = total - discount

    # PREVENT NEGATIVE TOTAL
    if final_total < 0:
        final_total = 0

    return render(request, 'cart.html', {

        'items': items,

        'total': total,

        'discount': discount,

        'final_total': final_total

    })

def increase_qty(request, cid):
    item = Cart.objects.get(id=cid)
    item.quantity += 1
    item.save()
    return redirect('cart')

def decrease_qty(request, cid):
    item = Cart.objects.get(id=cid)

    if item.quantity > 1:
        item.quantity -= 1
        item.save()
    else:
        item.delete()

    return redirect('cart')

def remove_item(request, cid):
    item = Cart.objects.get(id=cid)
    item.delete()
    return redirect('cart')

def product_detail(request, pid):
    product = Product.objects.get(id=pid)
    return render (request, 'product_detail.html',{'product':product})

def add_to_wishlist(request, pid):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')  # only logged in users

    customer = Customer.objects.get(id=customer_id)
    product = Product.objects.get(id=pid)

    # prevent duplicate wishlist
    already = Wishlist.objects.filter(customer=customer, product=product).exists()

    if not already:
        Wishlist.objects.create(customer=customer, product=product)

    return redirect('display_product')

def remove_from_wishlist(request, wid):
    item = Wishlist.objects.get(id=wid)
    item.delete()
    return redirect('wishlist')

def wishlist(request):
    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    items = Wishlist.objects.filter(customer=customer)

    return render(request, 'wishlist.html', {'items': items})

def add_category(request):
    if request.method == "POST":
        txt1 = request.POST['txt1']
        Category.objects.create(title=txt1)
        return redirect('add_category')
    return render(request,'add-category.html')

def display_category(request):
    categorylist = Category.objects.all()
    return render(request, 'display-category.html',{'category': categorylist})

def delete_category(request, id):
    Category.objects.get(id=id).delete()
    return redirect('display_category')

def edit_category(request, id):
    category = Category.objects.get(id=id)
    if request.method == "POST":
        category.title = request.POST['txt1']
        category.save()
        return redirect('display_category')
    return render(request, 'edit-category.html', {'category':category})


def add_product(request):

    category = Category.objects.all()

    if request.method == "POST":

        cat = request.POST.get('category')

        Product.objects.create(
            category_id=cat,
            title=request.POST.get('title'),
            price=request.POST.get('price'),
            details=request.POST.get('details'),
            image=request.FILES.get('image')
        )

    context = {
        'category': category
    }

    return render(request,'add_product.html',context)

def category_products(request, cid):

    categories = Category.objects.all()

    products = Product.objects.filter(
        category_id=cid
    )

    context = {
        'products': products,
        'categories': categories
    }

    return render(request,'home.html',context)

from django.contrib import messages
from django.shortcuts import render, redirect

def place_order(request):
    if not request.session.get('customer_id'):
        return redirect('login')

    customer = Customer.objects.get(id=request.session['customer_id'])
    cart_items = Cart.objects.filter(customer=customer)

    if not cart_items:
        messages.warning(request, "Your cart is empty!")
        return redirect('cart')

    # 👉 (Optional: save order in DB here)

    # Clear cart
    cart_items.delete()

    # Redirect to success page
    return redirect('order_success')


def order_success(request):
    return render(request, 'order_success.html')

def checkout(request):

    customer_id = request.session.get('customer_id')

    customer = Customer.objects.get(id=customer_id)

    cart_items = Cart.objects.filter(customer=customer)

    total = sum(
        i.product.price * i.quantity
        for i in cart_items
    )

    discount = request.session.get(
        'coupon_discount',
        0
    )

    final_total = total - discount

    if final_total < 0:
        final_total = 0

    return render(request, 'checkout.html', {

        'cart_items': cart_items,

        'total': total,

        'discount': discount,

        'final_total': final_total

    })

def display_product(request):
    productlist = Product.objects.all()
    return render(request, 'display-product.html',{'product': productlist})

def delete_product(request, id):
    Product.objects.get(id=id).delete()
    return redirect('display_product')

def edit_product(request, id):
    
    p = Product.objects.get(id=id)
    categories = Category.objects.all()

    if request.method == "POST":
    # Get data from the form
        p.title = request.POST.get('productname')  
        p.price = request.POST.get('price')
        p.details = request.POST.get('details')   
        
        # Handle Category Update
        c_id = request.POST.get('category')
        if c_id:
            p.category = Category.objects.get(id=c_id)

        # Handle Image Update only if a new file is uploaded
        if 'image' in request.FILES:
            p.image = request.FILES['image']

        p.save()
        return redirect('display_product')  # Redirect to list view after saving

    return render(request, 'edit-product.html', {
        'product': p,
        'category': categories,
    })

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # You can store in DB OR just show success message
        # (For now we'll just show message)

        messages.success(request, "✅ Your message has been sent!")

        return redirect('contact')

    return render(request, 'contact.html')

def place_order(request):

    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    cart_items = Cart.objects.filter(customer=customer)

    if not cart_items:
        return redirect('cart')

    # TOTAL CALCULATION
    total = sum(i.product.price * i.quantity for i in cart_items)

    if request.method == "POST":

        name = request.POST.get('name')
        mobile = request.POST.get('mobile')
        address = request.POST.get('address')
        city = request.POST.get('city')
        pincode = request.POST.get('pincode')

        # CREATE ORDER
        order = Order.objects.create(
            customer=customer,
            name=name,
            mobile=mobile,
            address=address,
            city=city,
            pincode=pincode,
            total_amount=total,
            status='Pending'
        )

        # CREATE ORDER ITEMS
        for item in cart_items:

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

        # CLEAR CART
        cart_items.delete()

        # SUCCESS MESSAGE
        messages.success(request, "✅ Order placed successfully!")

        return redirect('invoice', order_id=order.id)

    return redirect('checkout')

def invoice(request, order_id):
    order = Order.objects.get(id=order_id)
    items = OrderItem.objects.filter(order=order)

    return render(request, 'invoice.html', {
        'order': order,
        'items': items
    })

from .models import *

def my_orders(request):

    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    try:
        customer = Customer.objects.get(id=customer_id)

    except Customer.DoesNotExist:
        request.session.flush()  # clear invalid session
        return redirect('login')

    orders = Order.objects.filter(customer=customer).order_by('-id')

    return render(request, 'my_orders.html', {
        'orders': orders
    })

from django.db.models import Q

def search(request):

    query = request.GET.get('q')

    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(details__icontains=query)
    )

    return render(request, 'search.html', {
        'products': products,
        'query': query
    })

def profile(request):

    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    return render(request, 'profile.html', {
        'customer': customer
    })


def edit_profile(request):

    customer_id = request.session.get('customer_id')

    if not customer_id:
        return redirect('login')

    customer = Customer.objects.get(id=customer_id)

    if request.method == "POST":

        customer.name = request.POST.get('name')
        customer.email = request.POST.get('email')
        customer.mobile = request.POST.get('mobile')
        customer.address = request.POST.get('address')

        # PASSWORD CHANGE
        new_password = request.POST.get('password')

        if new_password:
            customer.password = new_password

        # PROFILE PHOTO
        if 'profile_photo' in request.FILES:
            customer.profile_photo = request.FILES['profile_photo']

        customer.save()

        request.session['customer_name'] = customer.name

        messages.success(request, "Profile Updated Successfully ✅")

        return redirect('profile')

    return render(request, 'edit_profile.html', {
        'customer': customer
    })

def apply_coupon(request):

    if request.method == "POST":

        code = request.POST.get('coupon_code')

        try:
            coupon = Coupon.objects.get(
                code=code,
                is_active=True
            )

            request.session['coupon_discount'] = coupon.discount
            request.session['coupon_code'] = coupon.code

            messages.success(
                request,
                f'Coupon Applied! ₹{coupon.discount} OFF'
            )

        except Coupon.DoesNotExist:

            messages.error(
                request,
                'Invalid Coupon'
            )

    return redirect('cart')
