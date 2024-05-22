# BagHub-1

pip install -r requirements.txt


replace the following in admin.py

# Send email to admin
                send_mail(
                    'Low stock alert',
                    f'The product "{product.name}" is low on stock.',
                    settings.EMAIL_HOST_USER, 
                    ['example@gmail.com'],  # Replace with admin email
                    fail_silently=False,
                )

replace following on Settings.py

1. 

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'example@gmail.com'      #Replace with your email
EMAIL_HOST_PASSWORD = ''      #replace with google app specific password.


2.

STRIPE_SECRET_KEY = '****************'
STRIPE_PUBLIC_KEY = '****************'

#login to stripe and get your api keys. (Payment module)



for more details:  justinmjoseph222@gmail.com
