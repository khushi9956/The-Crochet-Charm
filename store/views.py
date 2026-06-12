from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Contact
from django.core.mail import send_mail
from django.conf import settings

def home(request):

    if request.method == "POST":

        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            message=request.POST['message']
        )
        send_mail(
    'New Crochet Inquiry 🧶',
    f'''
Name: {request.POST["name"]}

Email: {request.POST["email"]}

Message:
{request.POST["message"]}
''',
    settings.EMAIL_HOST_USER,
    [settings.EMAIL_HOST_USER],
    fail_silently=False,
)

        messages.success(
            request,
            "Thank you! Your message has been sent successfully. 💖"
        )

        return redirect('/')
        

    products = Product.objects.all()

    search = request.GET.get('search')

    if search:
        products = products.filter(
            name__icontains=search
        )

    return render(
        request,
        'index.html',
        {'products': products}
        
    )
    