from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages
from .forms import CustomerRegistrationForm
from orders.models import Order  # Imported directly; will be created in Phase 11

def register(request):
    """
    Renders registration page and creates new customer accounts.
    """
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomerRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            
            # Auto login user after registration
            login(request, user)
            messages.success(request, f"Welcome to Spark Sports, {user.username}! Your account has been created.")
            return redirect('home')
        else:
            messages.error(request, "Registration failed. Please correct the errors below.")
    else:
        form = CustomerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


def login_user(request):
    """
    Authenticates user credentials and initiates the session.
    """
    if request.user.is_authenticated:
        return redirect('profile')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome back, {username}!")
                next_url = request.GET.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('profile')
        else:
            messages.error(request, "Invalid username or password. Please try again.")
    else:
        form = AuthenticationForm()
        
    return render(request, 'accounts/login.html', {'form': form})


def logout_user(request):
    """
    Terminates the user session.
    """
    logout(request)
    messages.info(request, "You have successfully logged out. Hope to see you back on the pitch soon!")
    return redirect('home')


@login_required
def profile(request):
    """
    Renders customer dashboard with their order history.
    """
    # Fetch orders corresponding to the authenticated user
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    context = {
        'orders': orders,
    }
    return render(request, 'accounts/profile.html', context)
