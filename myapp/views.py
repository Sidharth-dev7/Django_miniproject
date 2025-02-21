from django.shortcuts import render,redirect,get_object_or_404
from .models import Cart
from .forms import imgForm,regForm
from .models import media,Order,OrderItem
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib import messages
from reportlab.pdfgen import canvas
from io import BytesIO
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from django.contrib.auth import authenticate, login
from django.contrib.auth.hashers import make_password


def registration(request):
    form = imgForm()
    if request.method == "POST":
        form = imgForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
    return render(request,"register.html",{'form': form})

def vieww(request):
    cr = media.objects.all()
    return render(request,"view_products.html", {'cr':cr})

def detailvieww(request,pk):
    cr=media.objects.get(id=pk)
    return render(request,"detailed_view.html",{'cr':cr})





def userlog(request):
    if request.method == 'POST':
        username = request.POST.get("username")
        password = request.POST.get("password")
        
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)  # Logs in the user and starts a session
            return redirect('view')  # Redirect to the home page after login
        else:
            messages.error(request, 'Invalid username or password')

    return render(request, 'login.html')



def loginn(request):
    return render(request, "login.html")

def reg2(request):
    form = regForm()
    if request.method == "POST":
        form = regForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.save()

            # Re-authenticate the user after saving
            user = authenticate(request, username=user.username, password=request.POST['password'])
            
            if user is not None:
                login(request, user)
                messages.success(request, "Registration successful! You are now logged in.")
                return redirect('view')  # Redirect to the home page or another page after successful login

            # If authentication failed (shouldn't happen), show error
            messages.error(request, "There was an error during login. Please try again.")
            return redirect('logins')  # Or redirect to login page

    return render(request, "register2.html", {'form': form})







def user_logout(request):
    logout(request)
    return redirect('view') 



@login_required(login_url='/logins/')
def add_to_cart(request, product_id):
    product = get_object_or_404(media, id=product_id)
    
    # Check if the product is already in the cart
    cart_item, created = Cart.objects.get_or_create(user=request.user, product=product)
    
    if not created:
        # If the product is already in the cart, increment the quantity
        cart_item.quantity += 1
        cart_item.save()

    return redirect('cart')  # Redirect to the cart page




def cart_view(request):
    cart_items = Cart.objects.filter(user=request.user)
    total_price = sum(item.get_total_price() for item in cart_items)
    
    return render(request, 'cart.html', {'cart_items': cart_items, 'total_price': total_price})



def increment_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart')


def decrement_quantity(request, cart_item_id):
    cart_item = get_object_or_404(Cart, id=cart_item_id, user=request.user)
    
    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()
    
    return redirect('cart')


def delete_from_cart(request, item_id):
    item = get_object_or_404(Cart, id=item_id)
    item.delete()
    return redirect('cart')






def checkout(request):
    cart_items = Cart.objects.all()
    total_price = sum(item.get_total_price() for item in cart_items)

    return render(request, 'checkout.html', {'cart_items': cart_items, 'total_price': total_price})

def process_checkout(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        address = request.POST.get("address")
        payment_method = request.POST.get("payment_method")

        cart_items = Cart.objects.all()
        total_price = sum(item.get_total_price() for item in cart_items)

        if not cart_items:
            messages.error(request, "Your cart is empty!")
            return redirect('cart')

        # Create Order
        order = Order.objects.create(
            name=name,
            email=email,
            address=address,
            payment_method=payment_method,
            total_price=total_price
        )

        # Create OrderItems
        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product_name=item.product.name,
                quantity=item.quantity,
                price=item.get_total_price()
            )

        # Clear the cart
        cart_items.delete()

        messages.success(request, "Order placed successfully!")
        return redirect('view')  # Redirect to home page

    return redirect('checkout')



@login_required
def order_historyy(request):
    # Retrieve all orders of the logged-in user
    orders = Order.objects.filter(email=request.user.email).order_by('-created_at')
    
    return render(request, 'order_history.html', {'orders': orders})








@login_required
def generate_invoice(request, order_id):
    # Get the order details using the order ID
    order = get_object_or_404(Order, id=order_id, email=request.user.email)
    
    # Create an in-memory buffer to hold the PDF data
    buffer = BytesIO()

    # Create a canvas object for generating the PDF
    p = canvas.Canvas(buffer)
    
    # Add invoice title
    p.setFont("Helvetica-Bold", 18)
    p.drawString(100, 800, f"Invoice for Order #{order.id}")

    # Add order details
    p.setFont("Helvetica", 12)
    p.drawString(100, 770, f"Name: {order.name}")
    p.drawString(100, 750, f"Email: {order.email}")
    p.drawString(100, 730, f"Address: {order.address}")
    p.drawString(100, 710, f"Payment Method: {order.payment_method}")
    p.drawString(100, 690, f"Total Price: ${order.total_price}")
    
    # Add a line break
    p.line(100, 680, 500, 680)

    # Add the ordered items (using the correct related name 'items')
    y_position = 660
    p.drawString(100, y_position, "Items Ordered:")
    y_position -= 20
    for item in order.items.all():  # Use 'items' instead of 'orderitem_set'
        p.drawString(100, y_position, f"{item.product_name} (x{item.quantity}) - ${item.price}")
        y_position -= 20

    # Close the canvas and save the PDF to the buffer
    p.showPage()
    p.save()

    # Rewind the buffer to the beginning so we can read the PDF data
    buffer.seek(0)

    # Create a response with the PDF data
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{order.id}.pdf"'
    response.write(buffer.getvalue())
    
    return response



    