from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Contact
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponse

def home(request):

    print("HOME VIEW HIT")

    if request.method == "POST":

        print("POST RECEIVED")

        Contact.objects.create(
            name=request.POST['name'],
            email=request.POST['email'],
            message=request.POST['message']
        )

        print("CONTACT SAVED")
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
def robots_txt(request):
    lines = [
        "User-agent: *",
        "Allow: /",
        "Sitemap: https://the-crochet-charm.onrender.com/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain")