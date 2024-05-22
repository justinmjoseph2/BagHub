from django.contrib import admin
from .models import  Customer, Seller, Category, Subcategory, Product, Order, OrderItem
from django.utils.html import format_html
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import contact


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'phone_no']
    search_fields = ['name', 'email', 'phone_no']

class SubcategoryInline(admin.TabularInline):
    model = Subcategory
    extra = 1

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = [SubcategoryInline]

    def get_subcategory_count(self, obj):
        return obj.subcategory_set.count()

    get_subcategory_count.short_description = 'Subcategory Count'

    list_display = ['category_name', 'get_subcategory_count']
    search_fields = ['category_name']


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    pass


from django.contrib import admin
from django.contrib.auth.models import User
from .models import Customer, Seller

from django.contrib import admin
from django.contrib.auth.models import User
from .models import Customer, Seller, Product

@admin.register(Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'email', 'contact_number', 'role']
    search_fields = ['customer_name', 'email', 'contact_number']
    list_editable = ['role']
    list_filter = ['role']
    actions = ['set_role_as_seller']

    def set_role_as_seller(self, request, queryset):
        queryset.update(role='seller')
        self.message_user(request, "Selected customers have been set as sellers.")

    set_role_as_seller.short_description = "Set selected customers as sellers"

    def get_form(self, request, obj=None, **kwargs):
        if obj:
            self.exclude = ['password']
        else:
            self.exclude = []
        return super().get_form(request, obj=obj, **kwargs)

    def formfield_for_dbfield(self, db_field, request, **kwargs):
        formfield = super().formfield_for_dbfield(db_field, request, **kwargs)
        if db_field.name == 'role':
            formfield.widget = admin.widgets.AdminRadioSelect(choices=[('customer', 'Customer'), ('seller', 'Seller')])
        return formfield

    def save_model(self, request, obj, form, change):
        if change:
            original_obj = self.model.objects.get(pk=obj.pk)
            if original_obj.role != obj.role:
                if obj.role == 'seller':
                    # Create a corresponding Seller object
                    seller = Seller.objects.create(
                        name=obj.customer_name,
                        email=obj.email,
                        phone_no=obj.contact_number,
                    )
                else:
                    # Delete the corresponding Seller object and associated products
                    seller = Seller.objects.filter(email=obj.email).first()
                    if seller:
                        # Retrieve seller's products and delete them
                        products = Product.objects.filter(seller=seller)
                        for product in products:
                            product.delete()
                        # Delete the corresponding Seller object
                        seller.delete()
        super().save_model(request, obj, form, change)

    def delete_model(self, request, obj):
        # Retrieve the seller associated with the customer
        seller = obj.seller_set.first()
        if seller:
            # Retrieve the products associated with the seller and set seller to NULL
            products = Product.objects.filter(seller=seller)
            products.update(seller=None)
            # Delete the seller
            seller.delete()
        # Call the superclass delete_model to delete the customer
        super().delete_model(request, obj)
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['display_image','name', 'seller', 'subcategory', 'price', 'quantity_in_stock']
    list_filter = ['seller','subcategory']
    search_fields = ['name']
    def display_image(self, obj):
        return format_html('<img src="{}" width="50px" height="50px" />', obj.image_1.url)

    display_image.short_description = 'Image'
    
    def changelist_view(self, request, extra_context=None):
        # Check stock levels for each product
        for product in Product.objects.all():
            if product.quantity_in_stock < product.reorder_level:
                messages.warning(request, f"Low stock alert: {product.name}")

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer', 'address', 'order_date', 'status']
    list_filter = ['status']
    search_fields = ['customer__customer_name']
    
    

class InventoryProduct(Product):
    class Meta:
        proxy = True
        verbose_name = 'Inventory'
        verbose_name_plural = 'Inventory'

class InventoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'quantity_in_stock', 'reorder_level']
    list_filter = ['seller','subcategory']
    fields = ('quantity_in_stock', 'reorder_level')

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [f.name for f in obj._meta.fields if f.name not in ['quantity_in_stock', 'reorder_level']]
    
    def changelist_view(self, request, extra_context=None):
        # Check stock levels for each product
        for product in InventoryProduct.objects.all():
            if product.quantity_in_stock < product.reorder_level:
                messages.warning(request, f"Low stock alert: {product.name}")
                
                # Send email to admin
                send_mail(
                    'Low stock alert',
                    f'The product "{product.name}" is low on stock.',
                    settings.EMAIL_HOST_USER,  # Replace with your email
                    ['justinmjoseph222@gmail.com'],  # Replace with admin email
                    fail_silently=False,
                )

        # Call the superclass changelist_view to render the page
        return super().changelist_view(request, extra_context=extra_context)

admin.site.register(InventoryProduct, InventoryAdmin)


from django.contrib import admin
from .models import contact
from .forms import ContactForm

class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message']
    search_fields = ['name']

admin.site.register(contact, ContactAdmin)
















from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.html import format_html
from django.contrib import messages
from .models import QuantityAlert, PurchaseOrder, Product

class QuantityAlertAdmin(admin.ModelAdmin):
    list_display = ('display_image', 'product', 'seller', 'required_quantity', 'created_at')
    readonly_fields = ('product', 'seller', 'created_at')
    actions = ['move_to_purchase_order']
    list_filter = ['seller']

    def display_image(self, obj):
        return format_html('<img src="{}" width="50px" height="50px" />', obj.product.image_1.url)

    display_image.short_description = 'Image'

    def move_to_purchase_order(self, request, queryset):
        for quantity_alert in queryset:
            # Create PurchaseOrder
            purchase_order = PurchaseOrder.objects.create(
                product=quantity_alert.product,
                seller=quantity_alert.seller,
                quantity=quantity_alert.required_quantity
            )
            # Copy image from Product to PurchaseOrder
            purchase_order.image_1 = quantity_alert.product.image_1
            purchase_order.save()
            
            # Delete QuantityAlert
            quantity_alert.delete()
            self.message_user(request, f"Order successfull for {purchase_order.product.name}")

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        return qs.filter(seller__in=request.user.seller.all())

admin.site.register(QuantityAlert, QuantityAlertAdmin)



class PurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ('display_image', 'product', 'seller', 'quantity', 'created_at')
    readonly_fields = ('product', 'seller', 'created_at')

    def display_image(self, obj):
        return format_html('<img src="{}" width="50px" height="50px" />', obj.product.image_1.url)
    
admin.site.register(PurchaseOrder, PurchaseOrderAdmin)




# admin.py

from django.contrib import admin
from .models import RecentOrder

@admin.register(RecentOrder)
class RecentOrderAdmin(admin.ModelAdmin):
    list_display = ('product', 'quantity', 'created_at', 'supplied')
    search_fields = ('product__name',)  
    list_filter = ('created_at', 'supplied')  
