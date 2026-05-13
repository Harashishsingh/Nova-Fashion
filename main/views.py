from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Order, SellerProfile, ProductSize, Wishlist, Cart, ShippingAddress,Contact
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import Q




# ================= HOME =================
def index(request):

    products = Product.objects.filter(
        is_featured=True,
        stock__gt=0
    )

    cart_count = 0

    # ✅ If user logged in then get cart count
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user=request.user).count()

    return render(request, 'index.html', {
        'products': products,
        'cart_count': cart_count,
    })


# ================= DASHBOARD =================
# ================= DASHBOARD =================
@login_required(login_url='signin')
def dashboard(request):

    user = request.user   # ✅ IMPORTANT

    # ================= USER ORDERS ONLY =================
    orders = Order.objects.filter(user=user).order_by('-ordered_at')

    total_orders = orders.count()

    total_sales = sum(order.amount for order in orders)
    total_earnings = total_sales

    # ================= PRODUCTS =================
    products = Product.objects.all()

    # ================= ADD PRODUCT =================
    if request.method == "POST" and "add_product" in request.POST:

        name = request.POST.get('name')
        price = request.POST.get('price') or 0
        category = request.POST.get('category')
        subcategory = request.POST.get('subcategory')
        description = request.POST.get('description')
        stock = request.POST.get('stock') or 0
        image = request.FILES.get('image')

        if not category:
            messages.error(request, "Select category")
            return redirect('dashboard')

        if not subcategory:
            messages.error(request, "Select subcategory")
            return redirect('dashboard')

        is_featured = True if request.POST.get('is_featured') else False

        product = Product.objects.create(
            name=name,
            price=int(price),
            category=category,
            subcategory=subcategory,
            description=description,
            stock=int(stock),
            image=image,
            is_featured=is_featured
        )

        sizes = request.POST.getlist('size[]')
        prices = request.POST.getlist('size_price[]')

        for s, p in zip(sizes, prices):
            if s and p:
                ProductSize.objects.create(
                    product=product,
                    size=s,
                    price=int(p)
                )

        messages.success(request, "Product Added Successfully!")
        return redirect('dashboard')

    # ================= UPDATE ORDER STATUS =================
    if request.method == "POST" and "update_order_status" in request.POST:

        order_id = request.POST.get('order_id')
        status = request.POST.get('status')

        order = Order.objects.get(id=order_id)

        # ⚠️ SECURITY FIX: only allow owner/admin
        if order.user == user:
            order.status = status
            order.save()
            messages.success(request, "Order updated!")
        else:
            messages.error(request, "Not allowed!")

        return redirect('dashboard')

    # ================= PROFILE =================
    profile, created = SellerProfile.objects.get_or_create(user=user)

    return render(request, 'dashboard.html', {

        'products': products,
        'orders': orders,   # ✅ ONLY USER ORDERS

        'total_orders': total_orders,
        'total_sales': total_sales,
        'total_earnings': total_earnings,

        'profile': profile,
    })
# ================= PRODUCT PAGE (SEARCH + FILTER) =================
def product_page(request, category, subcategory):

    products = Product.objects.filter(
        category=category,
        subcategory=subcategory,
        stock__gt=0
    )

    # 🔍 SEARCH
    query = request.GET.get('q')
    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query)
        )

    # 💰 PRICE FILTER
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(price__gte=min_price)

    if max_price:
        products = products.filter(price__lte=max_price)

    # 📏 SIZE FILTER
    size = request.GET.get('size')
    if size:
        products = products.filter(sizes__size=size)

    return render(request, 'product_page.html', {
        'products': products,
        'title': f"{category} - {subcategory}",
        'query': query
    })


# ================= PRODUCT DETAIL =================
def product_detail(request, id):
    product = get_object_or_404(Product, id=id)

    # ✅ FIX: ORDER SIZES PROPERLY
    size_order = ['XS', 'S', 'M', 'L', 'XL', 'XXL']

    sizes = sorted(
        product.sizes.all(),
        key=lambda x: size_order.index(x.size) if x.size in size_order else 0
    )

    return render(request, 'product_detail.html', {
        'product': product,
        'sizes': sizes
    })


# ================= DELETE =================
@login_required
def delete_product(request, id):
    product = get_object_or_404(Product, id=id)
    product.delete()
    return redirect('dashboard')


# ================= UPDATE =================
@login_required
def update_product(request, id):
    product = get_object_or_404(Product, id=id)
    sizes = product.sizes.all()

    if request.method == "POST":
        product.name = request.POST.get('name')
        product.price = int(request.POST.get('price') or 0)
        product.category = request.POST.get('category')
        product.subcategory = request.POST.get('subcategory')
        product.description = request.POST.get('description')
        product.stock = int(request.POST.get('stock') or 0)

        if request.FILES.get('image'):
            product.image = request.FILES['image']

        product.save()

        # 🔥 DELETE OLD SIZES
        product.sizes.all().delete()

        # 🔥 ADD UPDATED SIZES
        sizes_list = request.POST.getlist('size[]')
        prices_list = request.POST.getlist('size_price[]')

        for s, p in zip(sizes_list, prices_list):
            if s and p:
                ProductSize.objects.create(
                    product=product,
                    size=s,
                    price=int(p)
                )

        return redirect('dashboard')

    return render(request, 'update_product.html', {
        'product': product,
        'sizes': sizes
    })


# ================= PROFILE =================
@login_required
def update_profile_image(request):
    if request.method == "POST":
        profile = SellerProfile.objects.get(user=request.user)

        if request.FILES.get('profile_image'):
            profile.profile_image = request.FILES['profile_image']
            profile.save()

    return redirect('dashboard')


@login_required
def edit_profile(request):
    profile, _ = SellerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        messages.success(request, "Profile updated successfully!")
        return redirect('dashboard')

    return render(request, 'edit_profile.html', {'profile': profile})


# ================= AUTH =================
def signup(request):
    if request.method == "POST":
        User.objects.create_user(
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        return redirect('signin')

    return render(request, 'signup.html')


def signin(request):
    if request.method == "POST":
        user = authenticate(
            request,
            username=request.POST.get('username'),
            password=request.POST.get('password')
        )
        if user:
            login(request, user)
            return redirect('home')

    return render(request, 'signin.html')


@login_required
def signout(request):
    logout(request)
    return redirect('/')


@login_required
def edit_profile(request):
    profile, created = SellerProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        # You can expand later (name, bio, etc.)
        messages.success(request, "Profile updated successfully!")
        return redirect('dashboard')

    return render(request, 'edit_profile.html', {'profile': profile})

# ================= GLOBAL SEARCH =================
def search_products(request):

    query = request.GET.get('q')

    products = Product.objects.filter(stock__gt=0)

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(subcategory__icontains=query)
        )

    return render(request, 'product_page.html', {
        'products': products,
        'title': f"Search: {query}"
    })

@login_required
def add_to_wishlist(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    Wishlist.objects.get_or_create(user=request.user, product=product)
    return redirect(request.META.get('HTTP_REFERER', '/'))

@login_required
def wishlist_view(request):
    # Get all products linked to this user in Wishlist model
    wishlist_items = Wishlist.objects.filter(user=request.user).select_related('product')
    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items,
        'title': 'My Wishlist'
    })

@login_required
def remove_from_wishlist(request, product_id):
    Wishlist.objects.filter(user=request.user, product_id=product_id).delete()
    return redirect('wishlist_view')

# ================= FORGOT PASSWORD LOGIC =================
def forgot_password(request):
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        
        # Look for a user with both matching username and email
        user = User.objects.filter(username=username, email=email).first()
        
        if user:
            # If valid, send to reset page with user's ID
            return render(request, 'reset_password.html', {'user_id': user.id})
        else:
            messages.error(request, "No account found with those details.")
            return redirect('forgot_password')

    return render(request, 'forgot_password.html')

def reset_password(request):
    if request.method == "POST":
        user_id = request.POST.get('user_id')
        new_pass = request.POST.get('password')
        confirm_pass = request.POST.get('confirm_password')
        
        user = get_object_or_404(User, id=user_id)
        
        if new_pass == confirm_pass:
            # .set_password() handles the hashing/encryption
            user.set_password(new_pass)
            user.save()
            messages.success(request, "Password updated! Please Sign In.")
            return redirect('signin')
        else:
            messages.error(request, "Passwords did not match.")
            return render(request, 'reset_password.html', {'user_id': user.id})
            
    return redirect('forgot_password')

def about(request):
    return render(request,'about.html')


# ================= ADD TO CART =================
# ================= ADD TO CART =================
def add_to_cart(request, product_id):

    # ✅ CHECK LOGIN FIRST
    if not request.user.is_authenticated:

        messages.error(
            request,
            "You have to sign in first to add products to cart."
        )

        return redirect('signin')

    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":

        size = request.POST.get('size')

        # ✅ SIZE VALIDATION
        if not size:

            messages.error(
                request,
                "Please select a size"
            )

            return redirect('product_detail', id=product.id)

        # ✅ CREATE OR UPDATE CART ITEM
        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size
        )

        if not created:

            cart_item.quantity += 1
            cart_item.save()

        messages.success(
            request,
            "Product added to cart successfully!"
        )

        return redirect('cart_view')

    return redirect('product_detail', id=product.id)


# ================= CART PAGE =================
@login_required
def cart_view(request):

    cart_items = Cart.objects.filter(user=request.user)

    subtotal = 0

    for item in cart_items:

        size_obj = ProductSize.objects.filter(
            product=item.product,
            size=item.size
        ).first()

        if size_obj:
            item_price = size_obj.price
        else:
            item_price = item.product.price

        subtotal += item_price * item.quantity

    delivery = 0

    final_total = subtotal + delivery

    cart_count = cart_items.count()

    return render(request, 'cart.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'delivery': delivery,
        'final_total': final_total,
        'cart_count': cart_count,
    })

# ================= INCREASE CART =================
@login_required
def increase_cart(request, cart_id):

    cart = get_object_or_404(Cart, id=cart_id, user=request.user)

    cart.quantity += 1
    cart.save()

    return redirect('cart_view')


# ================= DECREASE CART =================
@login_required
def decrease_cart(request, cart_id):

    cart = get_object_or_404(Cart, id=cart_id, user=request.user)

    if cart.quantity > 1:
        cart.quantity -= 1
        cart.save()
    else:
        cart.delete()

    return redirect('cart_view')


# ================= REMOVE CART =================
@login_required
def remove_cart(request, cart_id):

    cart = get_object_or_404(Cart, id=cart_id, user=request.user)

    cart.delete()

    messages.success(request, "Item removed from cart")

    return redirect('cart_view')


# ================= ORDER PAGE =================
@login_required
def order_page(request):

    cart_items = Cart.objects.filter(user=request.user)

    subtotal = 0

    for item in cart_items:

        size_obj = ProductSize.objects.filter(
            product=item.product,
            size=item.size
        ).first()

        if size_obj:
            item_price = size_obj.price
        else:
            item_price = item.product.price

        subtotal += item_price * item.quantity

    discount = 0

    # DEFAULT TOTAL
    final_total = subtotal

    # APPLY COUPON
    if request.method == "POST":

        coupon = request.POST.get('coupon')

        if coupon == "NOVA10":

            discount = subtotal * 0.10

            final_total = subtotal - discount

            messages.success(request, "NOVA10 Coupon Applied Successfully!")

        elif coupon == "NOVA20":

            discount = subtotal * 0.20

            final_total = subtotal - discount

            messages.success(request, "NOVA20 Coupon Applied Successfully!")

        else:
            messages.error(request, "Invalid Coupon")

    # SAVE TOTAL IN SESSION
    request.session['final_total'] = float(final_total)

    return render(request, 'OrderPage.html', {
        'cart_items': cart_items,
        'subtotal': subtotal,
        'discount': discount,
        'final_total': final_total,
    })

# ================= PAYMENT PAGE =================
@login_required
def payment_page(request):

    cart_items = Cart.objects.filter(user=request.user)

    # GET FINAL TOTAL FROM SESSION
    total = request.session.get('final_total')

    # IF SESSION EMPTY THEN NORMAL TOTAL
    if not total:

        total = 0

        for item in cart_items:

            size_obj = ProductSize.objects.filter(
                product=item.product,
                size=item.size
            ).first()

            if size_obj:
                item_price = size_obj.price
            else:
                item_price = item.product.price

            total += item_price * item.quantity

    if request.method == "POST":

        address = ShippingAddress.objects.create(

            user=request.user,

            first_name=request.POST.get('first_name'),

            last_name=request.POST.get('last_name'),

            email=request.POST.get('email'),

            phone=request.POST.get('phone'),

            address=request.POST.get('address'),

            postal_code=request.POST.get('postal_code'),

            state=request.POST.get('state'),

            city=request.POST.get('city'),

            total_amount=total
        )

        # ================= SAVE ORDERS =================
        for item in cart_items:

            size_obj = ProductSize.objects.filter(
                product=item.product,
                size=item.size
            ).first()

            if size_obj:
                item_price = size_obj.price
            else:
                item_price = item.product.price

            # ✅ CREATE ORDER
            Order.objects.create(

                user=request.user,

                product=item.product,

                amount=item_price * item.quantity,

                quantity=item.quantity,

                size=item.size,

                status="Ordered"

            )

            # ✅ REDUCE STOCK
            item.product.stock -= item.quantity
            item.product.save()

        # ================= CLEAR CART =================
        cart_items.delete()

        # ================= CLEAR SESSION =================
        if 'final_total' in request.session:
            del request.session['final_total']

        messages.success(
            request,
            "Order placed successfully! Delivery in 12 days."
        )

        return redirect('home')

    return render(request, 'payment.html', {
        'total': total
    })


# ================= MY ORDERS =================
@login_required
def my_orders(request):

    orders = Order.objects.filter(
        user=request.user
    ).order_by('-ordered_at')

    return render(request, 'my_orders.html', {
        'orders': orders
    })

# ================= CONTACT PAGE =================
def contact(request):

    if request.method == "POST":

        Contact.objects.create(

            first_name=request.POST.get('first_name'),

            last_name=request.POST.get('last_name'),

            email=request.POST.get('email'),

            phone=request.POST.get('phone'),

            username=request.POST.get('username'),

            subject=request.POST.get('subject'),

            message=request.POST.get('message')

        )

        messages.success(
            request,
            "Message sent successfully!"
        )

        return redirect('contact')

    return render(request, 'contact.html')