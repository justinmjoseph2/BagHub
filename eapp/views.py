from urllib import request
from django import forms
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, authenticate, logout
from django.contrib import messages
from django.core.exceptions import ValidationError
from django.urls import reverse, reverse_lazy
from .models import Customer
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.decorators import login_required
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth import authenticate, login
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.models import User
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes, force_str
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.contrib import messages
from .models import *
from .forms import AddressForm, ContactForm
from django.template.loader import get_template
from xhtml2pdf import pisa
from django.http import HttpResponse
from django.template.loader import get_template
from django.template import Context
import pydotplus
from graphviz import Digraph

# Create your views here.
# Create your views here.
def index(request):
    products = Product.objects.all()
    categories = Category.objects.prefetch_related('subcategory_set').all()
    return render(request, 'index.html', {'products': products, 'categories': categories})


def customer_dashboard(request):
    return render(request, 'customer/customer_dashboard.html')


from .models import Customer

from .models import Customer

def register(request):
    if request.method == 'POST':
        full_name = request.POST.get('full-name')
        email = request.POST.get('your-email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')
        phone_number = request.POST.get('phone-number')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords Do Not Match!')
            return render(request, 'customer/register.html')

        # Check password strength using Django's built-in validators
        try:
            validate_password(password)
        except ValidationError as e:
            messages.error(request, ', '.join(e.messages))
            return render(request, 'customer/register.html')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists!')
            return render(request, 'customer/register.html')

        # Check if phone number already exists
        if Customer.objects.filter(contact_number=phone_number).exists():
            messages.error(request, 'Phone number already exists!')
            return render(request, 'customer/register.html')

        # Check if phone number has exactly 10 digits
        if len(phone_number) != 10:
            messages.error(request, 'Phone number must have exactly 10 digits!')
            return render(request, 'customer/register.html')

        # Create user
        try:
            user = User.objects.create_user(username=email, email=email, password=password)
        except:
            messages.error(request, 'Failed to create user.')
            return render(request, 'customer/register.html')

        # Create customer
        customer = Customer.objects.create(user=user, customer_name=full_name, email=email, contact_number=phone_number)

        # Authenticate and login user
        user = authenticate(request, username=email, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, 'Your Account Has Been Registered Successfully!')
            return redirect('index')
        else:
            messages.error(request, 'Failed to login user.')
            return render(request, 'customer/register.html')

    return render(request, 'customer/register.html')

from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.shortcuts import render, redirect
from django.contrib.auth.models import User

from django.contrib.auth import get_user_model

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            user = get_user_model().objects.get(email=email)
            user = authenticate(request, username=user.username, password=password)
            if user is not None:
                if user.customer.role == "customer":
                    login(request, user)
                    messages.success(request, 'You have successfully logged in!')
                    return redirect('index')
                elif user.customer.role == "seller":
                    login(request, user)
                    messages.success(request, 'You have successfully logged in!')
                    return redirect('supplier_index')
            else:
                # Incorrect password
                error_message = "Incorrect email or password."
        except get_user_model().DoesNotExist:
            # User not found
            error_message = "User with this email does not exist."
        except Exception as e:
            # Other error occurred
            error_message = f"An error occurred: {str(e)}"
            
        messages.error(request, error_message)
        
    return render(request, 'customer/login.html')

def user_logout(request):
    logout(request)
    return redirect('index') 


@login_required
def change_password(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user  # Assuming the user is already logged in

        if user.check_password(old_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully.")
                return redirect('login')
            else:
                messages.error(request, "New passwords do not match.")
        else:
            messages.error(request, "Old password is incorrect.")

    return render(request, 'customer/change_password.html')


class CustomTokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, user, timestamp):
        return (
            str(user.pk) + user.password + str(timestamp)
        )



def forgot_password(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = CustomTokenGenerator().make_token(user)
            reset_password_url = request.build_absolute_uri('/reset_password/{}/{}/'.format(uid, token))
            email_subject = 'Reset Your Password'

            # Render both HTML and plain text versions of the email
            email_body_html = render_to_string('customer/reset_password_email.html', {
                'reset_password_url': reset_password_url,
                'user': user,
            })
            email_body_text = "Click the following link to reset your password: {}".format(reset_password_url)

            # Create an EmailMultiAlternatives object to send both HTML and plain text versions
            email = EmailMultiAlternatives(
                email_subject,
                email_body_text,
                settings.EMAIL_HOST_USER,
                [email],
            )
            email.attach_alternative(email_body_html, 'text/html')  # Attach HTML version
            email.send(fail_silently=False)

            messages.success(request, 'An email has been sent to your email address with instructions on how to reset your password.')
            return redirect('login')
        except User.DoesNotExist:
            messages.error(request, "User with this email does not exist.")
    return render(request, 'customer/forgot_password.html')


def reset_password(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and CustomTokenGenerator().check_token(user, token):
        if request.method == 'POST':
            new_password = request.POST.get('new_password')
            confirm_password = request.POST.get('confirm_password')

            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password reset successfully. You can now login with your new password.")
                return redirect('login')
            else:
                messages.error(request, "Passwords do not match.")
        return render(request, 'customer/reset_password.html')
    else:
        messages.error(request, "Invalid reset link. Please try again or request a new reset link.")
        return redirect('login')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Customer

@login_required
def edit_customer(request):
    # Retrieve the current logged-in user
    current_user = request.user
    # Check if the current user has a corresponding Customer instance
    try:
        customer = Customer.objects.get(user=current_user)
    except Customer.DoesNotExist:
        # Handle the case where the logged-in user does not have a corresponding Customer instance
        return HttpResponse("You are not associated with any customer profile.")

    if request.method == 'POST':
        # Update customer details with the data from the form
        customer.customer_name = request.POST['full-name']
        customer.email = request.POST['your-email']
        customer.contact_number = request.POST['phone-number']
        customer.save()

        # Update associated user's email
        current_user.email = request.POST['your-email']
        current_user.username = request.POST['your-email']
        current_user.save()

        # Redirect to the customer detail page after editing
        return redirect('index')

    # If it's a GET request, display the edit form with existing customer details
    return render(request, 'customer/edit_customer.html', {'customer': customer})


    

@login_required
def address_list(request):
    addresses = Address.objects.filter(customer=request.user.customer)
    return render(request, 'customer/address_list.html', {'addresses': addresses})

@login_required
def address_create(request):
    if request.method == 'POST':
        form = AddressForm(request.POST)
        if form.is_valid():
            # Custom validation for phone number and postal code
            recepient_contact = form.cleaned_data.get('recepient_contact')
            postal_code = form.cleaned_data.get('postal_code')

            if len(recepient_contact) != 10 or not recepient_contact.isdigit():
                messages.error(request, "Phone number must have exactly 10 digits.")
                return render(request, 'customer/address_form.html', {'form': form})

            if not (6 <= len(postal_code) <= 10) or not postal_code.isdigit():
                messages.error(request, "Postal code must be a number with 6-10 digits.")
                return render(request, 'customer/address_form.html', {'form': form})

            address = form.save(commit=False)
            address.customer = request.user.customer
            address.save()
            return redirect('address_list')
    else:
        form = AddressForm()
    return render(request, 'customer/address_form.html', {'form': form})

from .forms import ContactForm

@login_required
def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your message has been sent successfully!')
            return redirect('contact')  # Redirect back to the contact page
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f'Error in {field}: {error}', extra_tags='alert-dismissible')
    else:
        form = ContactForm()
    return render(request, 'contact_form.html', {'form': form})


@login_required
def address_edit(request, pk):
    address = get_object_or_404(Address, pk=pk, customer=request.user.customer)
    if request.method == 'POST':
        form = AddressForm(request.POST, instance=address)
        if form.is_valid():
            form.save()
            return redirect('address_list')
    else:
        form = AddressForm(instance=address)
    return render(request, 'customer/address_form.html', {'form': form})

@login_required
def address_delete(request, pk):
    address = get_object_or_404(Address, pk=pk, customer=request.user.customer)
    if request.method == 'POST':
        address.delete()
        return redirect('address_list')
    return render(request, 'customer/address_confirm_delete.html', {'address': address})

def product_detail(request, product_id):
    product = get_object_or_404(Product, pk=product_id)
    num_recommendations = 4
    recommended_products = product.get_similar_products(request, num_recommendations)
    return render(request, 'product-details.html', {'product': product, 'recommended_products': recommended_products})

@login_required
def cart(request):
    customer = request.user.customer
    cart_items = Cart.objects.filter(customer=customer)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    context = {
        'cart_items': cart_items,
        'total_price': total_price,
    }
    return render(request, 'cart.html', context)

@login_required
def add_to_cart(request):
    if request.method == 'POST':
        product_id = request.POST.get('product_id')
        quantity = request.POST.get('quantity')
        if product_id and quantity:
            try:
                product = Product.objects.get(pk=product_id)
                customer = request.user.customer
                cart_item, created = Cart.objects.get_or_create(customer=customer, product=product)
                cart_item.quantity += int(quantity)
                if cart_item.quantity <= product.quantity_in_stock:
                    cart_item.save()
                    messages.success(request, f'{quantity} item(s) added to cart.')
                else:
                    messages.error(request, 'Requested quantity exceeds available stock.')
            except Product.DoesNotExist:
                messages.error(request, 'Product does not exist.')
        else:
            messages.error(request, 'Invalid request.')
    return redirect('cart')

@login_required
def delete_item_in_cart(request, id):
    customer = request.user.customer
    product = get_object_or_404(Product, id=id)
    cart_item = Cart.objects.get(customer=customer, product=product)
    cart_item.delete()
    return redirect('cart')


@login_required
def increase_quantity(request, cart_item_id):
    cart_item = Cart.objects.get(pk=cart_item_id)
    if cart_item.quantity < cart_item.product.quantity_in_stock:
        cart_item.quantity += 1
        cart_item.save()
    return redirect('cart')

@login_required
def decrease_quantity(request, cart_item_id):
    cart_item = Cart.objects.get(pk=cart_item_id)
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    else:
        cart_item.delete()
    return redirect('cart')


from django.http import HttpResponseBadRequest

@login_required
def checkout(request):
    customer = request.user.customer
    cart_items = Cart.objects.filter(customer=customer)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    total_price_in_cents = total_price * 100

    if request.method == 'POST':
        address_id = request.POST.get('address_id')
        if not address_id.isdigit():
            return HttpResponseBadRequest("Invalid address ID")

        try:
            address = Address.objects.get(id=address_id)
        except Address.DoesNotExist:
            return HttpResponseBadRequest("Address does not exist")

        order = Order.objects.create(customer=customer, address=address)
        for item in cart_items:
            OrderItem.objects.create(order=order, product=item.product, quantity=item.quantity)
            item.product.quantity_in_stock -= item.quantity
            item.product.save()
            item.delete()
        
        # Send confirmation email to customer
        email_subject = 'Order Confirmation'
        email_body_html = render_to_string('order_confirmation_email.html', {'order': order})
        email_body_text = "Thank you for your order. Your order ID is {}. We will process it shortly.".format(order.id)
        email = EmailMultiAlternatives(
            email_subject,
            email_body_text,
            settings.EMAIL_HOST_USER,
            [customer.email],
        )
        email.attach_alternative(email_body_html, 'text/html')
        email.send()
        
        # Generate PDF bill
        pdf_template = get_template('bill_template.html')
        html = pdf_template.render({'order': order})
        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = 'filename="bill.pdf"'
        pisa_status = pisa.CreatePDF(html, dest=response)
        if pisa_status.err:
            return HttpResponse('We had some errors <pre>' + html + '</pre>')
        return response
        
        return redirect('order_detail', order.id)
    else:
        addresses = Address.objects.filter(customer=customer)
        context = {
            'cart_items': cart_items,
            'total_price': total_price,
            'total_price_in_cents': total_price_in_cents,
            'addresses': addresses,
            'STRIPE_PUBLIC_KEY': settings.STRIPE_PUBLIC_KEY,
        }
        return render(request, 'checkouts.html', context)

@login_required
def order_list(request):
    customer = request.user.customer
    orders = Order.objects.filter(customer=customer).order_by('-order_date')
    context = {
        'orders': orders,
    }
    return render(request, 'order_list.html', context)


from django.shortcuts import redirect

def cancel_order(request, order_id):
    order = Order.objects.get(pk=order_id)
    if order.status != 'Delivered':
        for item in order.orderitem_set.all():
            product = item.product
            product.quantity_in_stock += item.quantity
            product.save()
        order.status = 'Cancelled'
        order.save()
    return redirect('order_list')

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    context = {
        'order': order,
    }
    return render(request, 'order_detail.html', context)

def product_list(request):
    products = Product.objects.all()
    categories = Category.objects.prefetch_related('subcategory_set').all()
    return render(request, 'product_list.html', {'products': products, 'categories': categories})

def search_results(request):
    query = request.GET.get('q')
    products = Product.objects.filter(name__icontains=query) | \
               Product.objects.filter(subcategory__subcategory_name__icontains=query) | \
               Product.objects.filter(subcategory__parent_category__category_name__icontains=query)
    categories = Category.objects.prefetch_related('subcategory_set').all()

    return render(request, 'search_results.html', {'products': products, 'query': query, 'categories': categories})

def category_products(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(subcategory__parent_category=category)
    categories = Category.objects.prefetch_related('subcategory_set').all()

    return render(request, 'category_products.html', {'category': category, 'products': products, 'categories': categories})

def category_products(request, category_id):
    category = get_object_or_404(Category, pk=category_id)
    products = Product.objects.filter(subcategory__parent_category=category)
    categories = Category.objects.prefetch_related('subcategory_set').all()

    return render(request, 'category_products.html', {'category': category, 'products': products, 'categories': categories})


def subcategory_products(request, subcategory_id):
    subcategory = get_object_or_404(Subcategory, pk=subcategory_id)
    products = Product.objects.filter(subcategory=subcategory)
    categories = Category.objects.prefetch_related('subcategory_set').all()

    return render(request, 'subcategory_products.html', {'subcategory': subcategory, 'products': products, 'categories': categories})


def filter_products(request):
    filter_type = request.GET.get('filter')
    products = Product.objects.all()

    if filter_type == 'ascending':
        products = products.order_by('name')
    elif filter_type == 'descending':
        products = products.order_by('-name')
    elif filter_type == 'price_high_to_low':
        products = products.order_by('-price')
    elif filter_type == 'price_low_to_high':
        products = products.order_by('price')

    return render(request, 'product_list.html', {'products': products})


import matplotlib.pyplot as plt
import io
import base64
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Customer, Order, Seller, Product
from .models import PurchaseOrder

def supplier_index(request, total_demand=None):
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.role == 'seller':
                seller = Seller.objects.get(email=customer.email)
                products = Product.objects.filter(seller=seller)
                total_products = products.count()

                # Calculate total demand for each product
                product_demand = {}
                for product in products:
                    orders = Order.objects.filter(orderitem__product=product).distinct()
                    product_demand[product.name] = sum(item.quantity for order in orders for item in order.orderitem_set.all())

                total_orders = PurchaseOrder.objects.filter(seller=seller).distinct().count()

                # Generate chart
                chart_data = generate_chart(product_demand)

                # Filter PurchaseOrder instances for the logged-in user's seller account
                purchase_orders = PurchaseOrder.objects.filter(seller=seller)

                # Pass the PurchaseOrder instances to the template context
                return render(request, 'supplier_index.html', {
                    'all_products': products,
                    'total_products': total_products,
                    'total_orders': total_orders,
                    'product_demand': product_demand,
                    'chart_data': chart_data,
                    'purchase_orders': purchase_orders,
                })
            else:
                return HttpResponse("You are not authorized to access this page.")
        except Customer.DoesNotExist:
            return HttpResponse("You are not authorized to access this page.")
    else:
        return redirect('login')


import matplotlib.pyplot as plt
import base64
import random
import io
import numpy as np


def generate_chart(data):
    if not data:
        # If data is empty, create an empty plot
        plt.figure(figsize=(8, 6))
        plt.text(0.5, 0.5, 'No data available', horizontalalignment='center', verticalalignment='center', fontsize=14, color='gray')
        plt.axis('off')

        # Convert plot to base64 string
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

        plt.close()

        return chart_image

    # Convert data to lists for plotting
    products = list(data.keys())
    demand = list(data.values())

    # Generate a list of colors for each bar
    colors = plt.cm.viridis(np.linspace(0, 1, len(products)))

    # Plotting
    plt.figure(figsize=(10, 6))
    bars = plt.bar(products, demand, color=colors, edgecolor='black')

    # Customizing plot aesthetics
    plt.xlabel('Products', fontsize=12)
    plt.ylabel('Demand', fontsize=12)
    plt.title('Product Demand Histogram', fontsize=14)
    plt.xticks(rotation=45, fontsize=10)  # Rotate x-axis labels for better readability
    plt.yticks(fontsize=10)
    plt.grid(axis='y', linestyle='--', alpha=0.5)

    # Remove top and right spines
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)

    # Add data labels above each bar
    for bar, d in zip(bars, demand):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, str(d), ha='center', fontsize=10)

    # Convert plot to base64 string
    buffer = io.BytesIO()
    plt.tight_layout()
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.close()

    return chart_image







    
    
    



def products(request):
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.role == 'seller':
                # Retrieve the corresponding Seller instance
                seller = Seller.objects.get(email=customer.email)
                # Filter products associated with the seller
                products = Product.objects.filter(seller=seller)
                return render(request, 'products.html', {'all_products': products})
            else:
                # Handle the case for customers who are not sellers
                return HttpResponse("You are not authorized to access this page.")
        except Customer.DoesNotExist:
            # Handle the case where the user is not associated with any customer
            return HttpResponse("You are not authorized to access this page.")
    else:
        return redirect('login')



def button(request):
    return render(request, 'button.html')

def typography(request):
    return render(request, 'typography.html')


def widget(request):
    return render(request, 'widget.html')

def form(request):
    return render(request, 'form.html')

def table(request):
    return render(request, 'table.html')

def chart(request):
    return render(request, 'chart.html')

from django.shortcuts import render, redirect
from .models import Seller

def signin(request):
    error_message = None
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        
        try:
            seller = Seller.objects.get(email=email)
            if seller.password == password:  # Compare plain text passwords
                # Authentication successful
                return redirect('supplier_index')  # Redirect to supplier_index.html
            else:
                # Incorrect password
                error_message = "Incorrect email or password."
        except Seller.DoesNotExist:
            # User not found
            error_message = "User with this email does not exist."
        except Exception as e:
            # Other error occurred
            error_message = f"An error occurred: {str(e)}"
    
    return render(request, 'signin.html', {'error_message': error_message})


def not_found(request):
    return render(request, 'not_found.html')

def blank(request):
    return render(request, 'blank.html')

def reset_pass(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')
        user = request.user  # Assuming the user is already logged in

        if user.check_password(old_password):
            if new_password == confirm_password:
                user.set_password(new_password)
                user.save()
                messages.success(request, "Password changed successfully.")
                return redirect('login')
            else:
                messages.error(request, "New passwords do not match.")
        else:
            messages.error(request, "Old password is incorrect.")

    return render(request, 'reset_pass.html')


def purchaseOrders(request):
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.role == 'seller':
                seller = Seller.objects.get(email=customer.email)
                purchase_orders = PurchaseOrder.objects.filter(seller=seller)

                # Pass the PurchaseOrder instances to the template context
                return render(request, 'purchaseOrders.html', {
                    'all_products': products,
                    'purchase_orders': purchase_orders,
                })
            else:
                return HttpResponse("You are not authorized to access this page.")
        except Customer.DoesNotExist:
            return HttpResponse("You are not authorized to access this page.")
    else:
        return redirect('login')
    

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import RecentOrder
from .models import Customer, Seller

def recentOredrs(request):
    if request.user.is_authenticated:
        try:
            customer = Customer.objects.get(user=request.user)
            if customer.role == 'seller':
                seller = Seller.objects.get(email=customer.email)
                recent = RecentOrder.objects.filter(product__seller=seller)

                # Pass the RecentOrder instances to the template context
                return render(request, 'recentOredrs.html', {
                    'purchase_orders': recent,
                })
            else:
                return HttpResponse("You are not authorized to access this page.")
        except Customer.DoesNotExist:
            return HttpResponse("You are not authorized to access this page.")
    else:
        return redirect('login')













    # views.py

from django.shortcuts import render, redirect
from .models import PurchaseOrder, Product, RecentOrder

def accept_purchase_order(request):
    if request.method == 'POST':
        # Get the purchase order ID from the form submission
        purchase_order_id = request.POST.get('purchase_order_id')
        
        # Retrieve the purchase order
        purchase_order = PurchaseOrder.objects.get(id=purchase_order_id)
        
        # Update the quantity in stock for the product
        product = purchase_order.product
        product.quantity_in_stock += purchase_order.quantity
        product.save()
        
        # Move the row to the RecentOrder model
        RecentOrder.objects.create(
            product=product,
            quantity=purchase_order.quantity,
            created_at=purchase_order.created_at,
            supplied=False
        )
        
        # Delete the purchase order
        purchase_order.delete()
        
        # Redirect back to the page where the form was submitted from
        return redirect(request.META.get('HTTP_REFERER', '/'))  # Redirect to the previous page or home if not available
    else:
        # Handle GET request appropriately
        pass


import io
import base64
from datetime import datetime, timedelta
from django.shortcuts import render, get_object_or_404
from .models import Product, OrderItem
import matplotlib.pyplot as plt
import numpy as np

def products_graph(request, product_id):
    # Retrieve the product object
    product = get_object_or_404(Product, pk=product_id)

    # Calculate revenue for each of the last five months from the current month
    today = datetime.now().date()
    months = []
    revenues = []

    for i in range(5):
        month_start = (today.replace(day=1) - timedelta(days=30 * i)).replace(day=1)
        month_end = (month_start.replace(day=1) + timedelta(days=30)).replace(day=1)
        order_items = OrderItem.objects.filter(product=product, order__order_date__range=(month_start, month_end))
        total_revenue = sum(item.total_price() for item in order_items)
        months.append(month_start.strftime('%Y-%m'))  # Add line break for better readability
        revenues.append(total_revenue)

    # Create the bar chart with improved styling
    plt.figure(figsize=(12, 6))
    plt.bar(months, revenues, color='#5A9BD4', edgecolor='grey', linewidth=1)

    # Add title and labels with enhanced font styling
    plt.title('Total Revenue for {} Over Last Five Months'.format(product.name), fontsize=16)
    plt.ylabel('Total Revenue ($)', fontsize=14)

    # Rotate x-axis labels for better readability
    plt.xticks(rotation=0, ha='center', fontsize=12)  # Adjust rotation angle and alignment
    plt.yticks(fontsize=12)

    # Add grid lines for better visualization
    plt.grid(axis='y', linestyle='--', alpha=0.7)

    # Add data labels above each bar
    for i, revenue in enumerate(revenues):
        plt.text(i, revenue + 50, f'${revenue:,}', ha='center', fontsize=12)

    # Save the plot to a buffer and convert it to base64 string
    buffer = io.BytesIO()
    plt.tight_layout()  # Adjust layout for better appearance
    plt.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    plt.close()

    # Create a list of previous five months as links
    month_links = []
    for month in months:
        month_links.append(reverse('products_weekly_sales', args=(product.id, month)))

    return render(request, 'products_graph.html', {'product': product, 'chart_image': chart_image, 'month_links': month_links})








from django.shortcuts import render
from django.shortcuts import get_object_or_404
from datetime import datetime, timedelta
from.models import Product, OrderItem

def products_weekly_sales(request, product_id, month):
    # Retrieve the product object
    product = get_object_or_404(Product, pk=product_id)

    # Parse the month input and set the month start and end dates
    month_start = datetime.strptime(month, '%Y-%m').replace(day=1)
    month_end = month_start.replace(day=1, month=month_start.month % 12 + 1) - timedelta(days=1)

    # Calculate revenue for each week in the selected month
    weeks = []
    revenues = []

    current_week_start = month_start
    while current_week_start <= month_end:
        current_week_end = current_week_start + timedelta(days=6)
        order_items = OrderItem.objects.filter(product=product, order__order_date__range=(current_week_start, current_week_end))
        total_revenue = sum(item.total_price() for item in order_items)
        weeks.append(current_week_start.strftime('%b %d, %Y - %d'))
        revenues.append(float(total_revenue))  # Convert Decimal to float
        current_week_start = current_week_end + timedelta(days=1)

    # Render the products_weekly_sales.html template
    return render(request, 'products_weekly_sales.html', {'product': product, 'weeks': weeks, 'revenues': revenues})








