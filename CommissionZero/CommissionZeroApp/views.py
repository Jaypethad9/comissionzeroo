from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.hashers import make_password
from django.db.models import Count, Sum, Q, Avg
from django.utils.timezone import localtime
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib import messages
from datetime import datetime, date, timedelta
from collections import defaultdict, OrderedDict
from django.utils.timezone import localtime  # ✅ Keep this one
from .models import EmailOTP  # your new EmailOTP model
from django.core.mail import send_mail

from chat_app.models import Message
from .decorators import role_required
from .forms import (
    CustomerRegisterForm,
    ProviderRegisterForm,
    ProviderServiceForm,
    QuotationForm,
    PortfolioProjectForm,
    ReviewForm
)
from .models import (
    CustomerProfile,
    ProviderProfile,
    ProviderService,
    Quotation,
    Review,
    Tender,
    PortfolioProject,
    Earning,
    PhoneOTP
)
from CommissionZeroApp.models import PortfolioProject, Tender, Quotation
import twilio_config
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
import random
import calendar
import json






# Create your views here.
#main pages

def send_otp(phone_number, otp):
    client = Client(twilio_config.TWILIO_ACCOUNT_SID, twilio_config.TWILIO_AUTH_TOKEN)
    try:
        message = client.messages.create(
            body=f"Your OTP is {otp}",
            from_=twilio_config.TWILIO_FROM_NUMBER,
            to=phone_number
        )
        return message.sid
    except TwilioRestException as e:
        print(f"Twilio error: {e}")
        return None


def home(request,):
    return render(request, 'CommissionZeroApp/home.html')

# def login(request,):
#     return render(request, 'CommissionZeroApp/login.html')

# def register(request,):
#     return render(request, 'CommissionZeroApp/register.html')

# def register_p(request,):
#     return render(request, 'CommissionZeroApp/register_provider.html')

def about(request,):
    return render(request, 'CommissionZeroApp/about.html')

def contact(request,):
    return render(request, 'CommissionZeroApp/contact.html')

def services(request,):
    return render(request, 'CommissionZeroApp/services.html') 

#customer pages

def service(request,):
    return render(request, 'CommissionZeroApp/service.html')




def register_customer(request):
    if request.method == 'POST':
        form = CustomerRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = str(random.randint(100000, 999999))
            
            # Save OTP linked to email
            EmailOTP.objects.update_or_create(
                email=email,
                defaults={'otp': otp, 'is_verified': False, 'timestamp': timezone.now()}
            )
            
            # Send OTP email
            send_otp_email(email, otp)
            
            # Store form data in session (with email as key)
            request.session['pending_customer_data'] = {
                'username': form.cleaned_data['username'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': email,
                'password1': form.cleaned_data['password1'],
                'password2': form.cleaned_data['password2'],
                'phone': form.cleaned_data.get('phone', '')  # optional
            }
            request.session['pending_email'] = email
            
            return redirect('verify_customer_otp')
        else:
            return render(request, 'CommissionZeroApp/register.html', {'form': form, 'type': 'customer'})
    else:
        form = CustomerRegisterForm()
    return render(request, 'CommissionZeroApp/register.html', {'form': form, 'type': 'customer'})



def verify_customer_otp(request):
    email = request.session.get('pending_email')
    if not email:
        return redirect('register_customer')

    if request.method == 'POST':
        input_otp = request.POST.get('otp')

        try:
            otp_obj = EmailOTP.objects.get(email=email)
            if not otp_obj.is_expired() and otp_obj.otp == input_otp:
                otp_obj.is_verified = True
                otp_obj.save()

                data = request.session.get('pending_customer_data')
                if not data:
                    return render(request, 'CommissionZeroApp/otp/verify_otp.html', {'error': 'Session expired. Please try again.'})

                # Create User
                user = User.objects.create_user(
                    username=data['username'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    password=data['password1']
                )

                # Create CustomerProfile
                CustomerProfile.objects.create(
                    user=user,
                    phone_number=data.get('phone', '')
                )
                
                login(request, user)

                # Clear session
                for key in list(request.session.keys()):
                    if key.startswith('pending_'):
                        del request.session[key]

                return redirect('customer_dashboard')
            else:
                return render(request, 'CommissionZeroApp/otp/verify_otp.html', {'error': 'Invalid or expired OTP'})
        except EmailOTP.DoesNotExist:
            return render(request, 'CommissionZeroApp/otp/verify_otp.html', {'error': 'Email not found'})

    return render(request, 'CommissionZeroApp/otp/verify_otp.html')

def register_provider(request):
    if request.method == 'POST':
        form = ProviderRegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            otp = str(random.randint(100000, 999999))

            # Save OTP linked to email
            EmailOTP.objects.update_or_create(
                email=email,
                defaults={'otp': otp, 'is_verified': False, 'timestamp': timezone.now()}
            )

            # Send the OTP email
            send_otp_email(email, otp)

            # Store form data in session to use after OTP verification
            request.session['pending_provider_data'] = {
                'username': form.cleaned_data['username'],
                'first_name': form.cleaned_data['first_name'],
                'last_name': form.cleaned_data['last_name'],
                'email': email,
                'password1': form.cleaned_data['password1'],
                'phone': form.cleaned_data['phone'],  # optional, keep if needed
                'location': form.cleaned_data['location'],
                'business_name': form.cleaned_data['business_name'],
                'categories': ",".join(form.cleaned_data['categories'])
            }
            request.session['pending_email'] = email

            return redirect('verify_provider_otp')
    else:
        form = ProviderRegisterForm()

    return render(request, 'CommissionZeroApp/register_provider.html', {'form': form, 'type': 'provider'})


def send_otp_email(email, otp):
    subject = "CommissionZero OTP Code"
    message = f"Your OTP code is: {otp}"
    from_email = 'your_email@gmail.com'  # replace with your sending email
    recipient_list = [email]

    send_mail(subject, message, from_email, recipient_list)


def register_provider_otp(request):
    email = request.session.get('pending_email')

    if not email:
        # If session expired or no email in session, redirect or show error
        return redirect('register_provider')

    if request.method == "POST":
        input_otp = request.POST.get("otp")

        try:
            otp_obj = EmailOTP.objects.get(email=email)
            if not otp_obj.is_expired() and otp_obj.otp == input_otp:
                otp_obj.is_verified = True
                otp_obj.save()

                data = request.session.get('pending_provider_data')
                if not data:
                    return render(request, "CommissionZeroApp/otp/verify_otp_provider.html", {
                        "error": "Session expired. Please try again."
                    })

                # Create the user
                user = User.objects.create_user(
                    username=data['username'],
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    email=data['email'],
                    password=data['password1']
                )

                # Create Provider Profile
                ProviderProfile.objects.create(
                    user=user,
                    phone=data.get('phone', ''),
                    business_name=data.get('business_name', ''),
                    categories=data['categories'],
                    location=data['location'],
                    status='pending'  # or 'ongoing' depending on your flow
                )

                # Log in the new user
                login(request, user)

                # Clear session data used during registration
                for key in list(request.session.keys()):
                    if key.startswith('pending_'):
                        del request.session[key]

                return redirect('waiting_approval')

            else:
                return render(request, "CommissionZeroApp/otp/verify_otp_provider.html", {
                    "error": "Invalid or expired OTP"
                })

        except EmailOTP.DoesNotExist:
            return render(request, "CommissionZeroApp/otp/verify_otp_provider.html", {
                "error": "Email not found"
            })

    return render(request, "CommissionZeroApp/otp/verify_otp_provider.html")




def user_login(request):
    if request.method == 'POST':
        identifier = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user_obj = User.objects.get(email=identifier)
            username = user_obj.username
        except User.DoesNotExist:
            username = identifier

        user = authenticate(username=username, password=password)
        if user:
            if hasattr(user, 'providerprofile'):
                provider = user.providerprofile
                if provider.status == 'pending':
                    return redirect('waiting_approval')  # 🚫 show wait page
                elif provider.status == 'suspended':
                    return render(request, 'CommissionZeroApp/login.html', {'error': 'Your account is suspended.'})

            login(request, user)

            if user.is_superuser:
                return redirect('admin_dashboard')
            elif hasattr(user, 'providerprofile'):
                return redirect('service_dashboard')
            elif hasattr(user, 'customerprofile'):
                return redirect('customer_dashboard')
            else:
                logout(request)
                return render(request, 'CommissionZeroApp/login.html', {'error': 'Unknown user type'})
        else:
            return render(request, 'CommissionZeroApp/login.html', {'error': 'Invalid credentials'})
    return render(request, 'CommissionZeroApp/login.html')

def request_otp_view(request):
    if request.method == "POST":
        phone = request.POST.get("phone_number")
        otp = str(random.randint(100000, 999999))

        PhoneOTP.objects.update_or_create(
            phone_number=phone,
            defaults={'otp': otp, 'is_verified': False, 'timestamp': timezone.now()}
        )

        send_otp(phone, otp)
        request.session['pending_phone'] = phone
        request.session['user_type'] = request.POST.get('user_type')  # 'customer' or 'provider'

        return redirect('verify_otp')

    return render(request, "CommissionZeroApp/otp/request_otp.html")

def verify_otp_view(request):
    phone = request.session.get('pending_phone')

    if request.method == "POST":
        input_otp = request.POST.get("otp")

        try:
            otp_obj = PhoneOTP.objects.get(phone_number=phone)
            if not otp_obj.is_expired() and otp_obj.otp == input_otp:
                otp_obj.is_verified = True
                otp_obj.save()

                # ✅ Use updated session format
                pending_data = request.session.get('pending_data')

                if not pending_data:
                    return render(request, "CommissionZeroApp/otp/verify_otp.html", {
                        "error": "Session expired. Please try again."
                    })

                # ✅ Create User
                user, created = User.objects.get_or_create(
                    username=pending_data['username'],
                    defaults={
                        'email': pending_data['email'],
                        'first_name': pending_data['first_name'],
                        'last_name': pending_data['last_name'],
                        'password': make_password(pending_data['password1']),
                    }
                )

                # ✅ Create CustomerProfile
                profile, _ = CustomerProfile.objects.get_or_create(user=user)
                profile.phone_number = pending_data['phone']
                profile.save()

                login(request, user)

                # ✅ Clear session
                for key in list(request.session.keys()):
                    if key.startswith('pending_') or key == 'pending_data':
                        del request.session[key]

                return redirect("customer_dashboard")

            else:
                return render(request, "CommissionZeroApp/otp/verify_otp.html", {"error": "Invalid or expired OTP"})

        except PhoneOTP.DoesNotExist:
            return render(request, "CommissionZeroApp/otp/verify_otp.html", {"error": "Phone number not found"})

    return render(request, "CommissionZeroApp/otp/verify_otp.html")



def waiting_approval(request):
    return render(request, 'CommissionZeroApp/waiting_approval.html')


def logout_view(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('login') 

@role_required(['customer'])
@login_required
def customer_dashboard(request):
    user = request.user

    active_tenders_count = Tender.objects.filter(user=user, status='open').count()
    pending_quotes_count = Quotation.objects.filter(tender__user=user, status='pending').count()
    active_projects_count = Tender.objects.filter(user=user, status='ongoing').count()

    tenders = (
        Tender.objects
        .filter(user=user)
        .annotate(num_quotes=Count('quotation'))
        .order_by('-created_at')[:5]
    )

    # ✅ Add progress attribute to each tender
    for tender in tenders:
        try:
            # Use the latest quotation (adjust if needed)
            quotation = Quotation.objects.filter(tender=tender).order_by('-created_at').first()
            tender.progress = quotation.progress if quotation else None
        except Exception:
            tender.progress = None

    # ✅ OUTSIDE the loop
    context = {
        'tenders': tenders,
        'active_tenders_count': active_tenders_count,
        'pending_quotes_count': pending_quotes_count,
        'active_projects_count': active_projects_count,
    }

    return render(request, 'CommissionZeroApp/customer/customer_dashboard.html', context)



@login_required
@role_required(['customer'])
def track_tender(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id, user=request.user)
    try:
        quote = Quotation.objects.get(tender=tender, status='accepted')
    except Quotation.DoesNotExist:
        quote = None

    return render(request, 'CommissionZeroApp/customer/track_tender.html', {'tender': tender, 'quote': quote})



@role_required(['customer'])
@login_required
def tender_creation(request):
    if request.method == 'POST':
        tender = Tender(
            user=request.user,
            title=request.POST['title'],
            description=request.POST['description'],
            category=request.POST['category'],
            budget=request.POST.get('budget') or None,
            urgency=request.POST['urgency'],
            address=request.POST['address'],
            postcode=request.POST['postcode'],
            start_date=request.POST.get('start_date') or None,
            deadline=request.POST['deadline'],
            notes=request.POST.get('notes', ''),
            images=request.FILES.get('images', None)
        )
        tender.save()
        return redirect('my_tenders')
    return render(request, 'CommissionZeroApp/customer/tender_creation.html')


@role_required(['customer'])
@login_required
def my_tenders(request):
    tenders = Tender.objects.filter(user=request.user)
    return render(request, 'CommissionZeroApp/customer/my_tenders.html', {'tenders': tenders})


@role_required(['customer'])
@login_required
def accept_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    if quotation.tender.user == request.user:
        quotation.status = 'accepted'
        quotation.save()
        # Update tender status
        quotation.tender.status = 'ongoing'
        quotation.tender.save()
    return redirect('view_quotation', tender_id=quotation.tender.id)


@role_required(['customer'])
@login_required
def reject_quotation(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    if quotation.tender.user == request.user:
        quotation.status = 'rejected'
        quotation.save()
    return redirect('view_quotation', tender_id=quotation.tender.id)



@login_required
def mark_quotation_completed(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    
    if quotation.status != 'completed':
        quotation.status = 'completed'
        quotation.save()

        Earning.objects.create(
            provider=quotation.provider,
            amount=quotation.total_cost,
            project_name=quotation.tender.title,
            client_name=quotation.tender.user.get_full_name() or quotation.tender.user.username,
            status='Paid'
        )

    return redirect('view_quotation', tender_id=quotation.tender.id)

# @role_required(['admin'])
# @login_required
# def quotes_admin(request):
#     from .models import Quotation
#     quotations = Quotation.objects.select_related('provider', 'tender').all()
#     return render(request, 'quotes_admin.html', {'quotations': quotations})

# @role_required(['admin'])
# @login_required
# def delete_quotation_admin(request, quotation_id):
#     quotation = get_object_or_404(Quotation, id=quotation_id)
#     quotation.delete()
#     return redirect('quotes_admin')




@role_required(['customer'])
@login_required
def tender_detail_customer(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id, user=request.user)
    return render(request, 'CommissionZeroApp/customer/tender_detail_customer.html', {'tender': tender})



@login_required
def submit_review(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id, user=request.user)
    completed_quotation = Quotation.objects.filter(tender=tender, status='completed').first()

    if not completed_quotation:
        messages.error(request, "You can only review after completion.")
        return redirect('my_tenders')

    provider = completed_quotation.provider

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.tender = tender
            review.provider = provider
            review.customer = request.user
            review.save()
            messages.success(request, "Review submitted successfully.")
            return redirect('view_quotation', tender_id=tender.id)
    else:
        form = ReviewForm()

    return render(request, 'CommissionZeroApp/customer/submit_review.html', {
        'form': form,
        'provider': provider,
    })



def view_reviews(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id)
    reviews = Review.objects.filter(tender=tender)
    return render(request, 'reviews.html', {'tender': tender, 'reviews': reviews})


@role_required(['customer'])
@login_required
def delete_review(request, review_id):
    review = get_object_or_404(Review, id=review_id, customer=request.user)

    if request.method == "POST":
        review.delete()
        return redirect('reviews')  # Change this to your actual view name

    return redirect('reviews')

@role_required(['customer'])
@login_required
def reviews(request):
    reviews = Review.objects.filter(customer=request.user).order_by('-created_at')
    
    customer_username = request.user.username if reviews else ""

    return render(request, 'CommissionZeroApp/customer/reviews.html', {
        'reviews': reviews,
        'customer_username': customer_username,
        'star_range': range(1, 6)
    })



@role_required(['customer'])
def messages_customer(request,):
    return render(request, 'CommissionZeroApp/customer/messages_customer.html')


@role_required(['customer'])
def find_professionals(request):
    providers = ProviderProfile.objects.select_related('user').all()
    context = {
        'providers': providers
    }
    return render(request, 'CommissionZeroApp/customer/find_professionals.html', context)




@role_required(['customer'])
@login_required
def settings(request):
    user = request.user
    profile = user.customerprofile

    if request.method == 'POST':
        user.username = request.POST.get('username', user.username)
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        profile.phone_number = request.POST.get('phone', profile.phone_number)

        user.save()
        profile.save()
        messages.success(request, "Your profile has been updated.")
        return redirect('settings')

    context = {
        'user': user,
        'profile': profile,
    }
    return render(request, 'CommissionZeroApp/customer/settings.html', context)



@role_required(['customer'])
@login_required
def change_password(request):
    if request.method == 'POST':
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # prevent logout
            messages.success(request, 'Password updated successfully!')
        else:
            messages.error(request, 'Please correct the errors below.')
    return redirect('settings')



@csrf_exempt
@login_required
def verify_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        password = data.get('password')
        is_valid = request.user.check_password(password)
        return JsonResponse({'valid': is_valid})
    return JsonResponse({'valid': False})


@role_required(['customer'])
def help_center(request,):
    return render(request, 'CommissionZeroApp/customer/help_center.html')


# service provider pages

@role_required(['provider'])
@login_required
def tender_detail_service(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id)
    quotation = Quotation.objects.filter(tender=tender, provider=request.user).first()
    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/tender_detail_service.html', {
        'tender': tender,
        'quotation': quotation,
        'avg_rating': avg_rating,
    })


@role_required(['provider'])
@login_required
def tenders(request):
    # Order tenders by created_at descending (newest first)
    tenders = Tender.objects.exclude(user=request.user).order_by('-created_at')
    
    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/tenders.html', {
        'tenders': tenders,
        'avg_rating': avg_rating,
    })




@login_required
@role_required(['provider'])
def service_dashboard(request):
    provider = request.user
    now = datetime.now()
    one_week_ago = now - timedelta(days=7)
    one_month_ago = now - timedelta(days=30)

    # ACTIVE TENDERS
    active_tenders = Tender.objects.filter(status='open').exclude(
        quotation__provider=provider
    )
    active_tender_count = active_tenders.count()
    last_week_tenders = Tender.objects.filter(status='open', created_at__range=(one_week_ago, now)).exclude(
        quotation__provider=provider
    ).count()
    tender_change = active_tender_count - last_week_tenders

    # PENDING QUOTES
    pending_quotes = Quotation.objects.filter(provider=provider, status='pending')
    pending_count = pending_quotes.count()
    prev_day = now - timedelta(days=1)
    yesterday_pending = Quotation.objects.filter(provider=provider, status='pending', created_at__date=prev_day.date()).count()
    quote_change = pending_count - yesterday_pending

    # ACTIVE PROJECTS
    active_projects = Quotation.objects.filter(provider=provider, status='accepted').count()

    # MONTHLY EARNINGS
    this_month = Earning.objects.filter(provider=provider, date__year=now.year, date__month=now.month, status='Paid')
    last_month = Earning.objects.filter(
        provider=provider,
        date__year=one_month_ago.year,
        date__month=one_month_ago.month,
        status='Paid'
    )
    monthly_earnings = this_month.aggregate(total=Sum('amount'))['total'] or 0
    last_month_earnings = last_month.aggregate(total=Sum('amount'))['total'] or 0

    # Calculate % change
    if last_month_earnings == 0:
        earning_change = None  # Cannot divide by zero
    else:
        earning_change = round(((monthly_earnings - last_month_earnings) / last_month_earnings) * 100)

    recent_quotes = Quotation.objects.filter(provider=provider).order_by('-created_at')[:3]

    # RECOMMENDED TENDERS
    recommended_tenders = Tender.objects.filter(status='open').exclude(quotation__provider=provider).order_by('-created_at')[:3]

    # AVG RATING
    avg_rating = get_avg_rating(provider)

    return render(request, 'CommissionZeroApp/service_provider/service_dashboard.html', {
        'active_tenders': active_tender_count,
        'pending_quotes': pending_count,
        'active_projects': active_projects,
        'monthly_earnings': monthly_earnings,
        'recent_quotes': recent_quotes,
        'tender_change': tender_change,
        'quote_change': quote_change,
        'earning_change': earning_change,
        'recommended_tenders': recommended_tenders,
        'avg_rating': avg_rating,  # include it in context
    })

# views.py
@login_required
@role_required(['provider'])
def update_progress(request, quotation_id):
    quote = get_object_or_404(Quotation, id=quotation_id, provider=request.user)

    if quote.status != 'accepted':
        return HttpResponseForbidden("Cannot update progress")

    if quote.progress < 100:
        quote.progress += 10
        quote.progress = min(100, quote.progress)
        quote.save()

    return redirect('service_dashboard')

@login_required
@role_required(['provider'])
def quotes(request):
    quotes = Quotation.objects.filter(provider=request.user).select_related('tender')
    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/quotes.html', {
        'quotes': quotes,
        'avg_rating': avg_rating,
    })




from decimal import Decimal
@role_required(['provider'])
@login_required
def submit_quotation(request, tender_id):
    tender = get_object_or_404(Tender, id=tender_id)
    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    if request.method == 'POST':
        form = QuotationForm(request.POST)
        if form.is_valid():
            quote = form.save(commit=False)
            quote.tender = tender
            quote.provider = request.user

            # Use Decimal for safe arithmetic
            subtotal = quote.labor_cost + quote.material_cost + quote.misc_cost
            gst_rate = Decimal('0.18')
            convenience_rate = Decimal('0.05')

            quote.gst_amount = (subtotal * gst_rate).quantize(Decimal('0.01'))
            quote.convenience_fee = (subtotal * convenience_rate).quantize(Decimal('0.01'))
            quote.total_cost = (subtotal + quote.gst_amount + quote.convenience_fee).quantize(Decimal('0.01'))

            quote.save()
            return redirect('service_dashboard')
    else:
        form = QuotationForm()

    return render(request, 'CommissionZeroApp/service_provider/submit_quotation.html', {
        'form': form,
        'tender': tender,
        'avg_rating': avg_rating,
    })

@role_required(['customer'])
@login_required
def view_quotation(request, tender_id):
    quotations = Quotation.objects.filter(tender_id=tender_id)
    return render(request, 'CommissionZeroApp/customer/view_quotation.html', {
        'quotations': quotations
    })
    


@role_required(['provider'])
def earnings(request):
    provider = request.user
    earnings = Earning.objects.filter(provider=provider)

    total_earnings = sum(e.amount for e in earnings)
    this_month = sum(e.amount for e in earnings if e.date.month == datetime.now().month and e.date.year == datetime.now().year)
    completed_projects = earnings.count()
    withdrawn = 7600  # Replace with actual logic if needed

    monthly_income = defaultdict(int)
    for e in earnings:
        if e.date:
            month_name = e.date.strftime('%b')
            monthly_income[month_name] += float(e.amount)

    max_val = max(monthly_income.values(), default=1)
    for k in monthly_income:
        monthly_income[k] = int((monthly_income[k] / max_val) * 100)

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    context = {
        'total_earnings': total_earnings,
        'this_month': this_month,
        'completed_projects': completed_projects,
        'withdrawn': withdrawn,
        'earnings': earnings,
        'monthly_income': dict(monthly_income),
        'avg_rating': avg_rating,
    }

    return render(request, 'CommissionZeroApp/service_provider/earnings.html', context)



def mark_quotation_completed(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    if request.user != quotation.tender.user:
        return HttpResponseForbidden()

    quotation.status = 'completed'
    quotation.save()

    # Create earning entry
    Earning.objects.create(
        provider=quotation.provider,
        amount=quotation.total_cost,
        project_name=quotation.tender.title,
        client_name=quotation.tender.user.get_full_name() or quotation.tender.user.username,
        status='Paid'
    )

    return redirect('view_quotation', quotation.tender.id)


def earnings_view(request):
    user = request.user
    earnings = Earning.objects.filter(service_provider=user)

    # Monthly income aggregation
    monthly_income = OrderedDict((calendar.month_abbr[m], 0) for m in range(1, 13))  # {'Jan': 0, ..., 'Dec': 0}
    for e in earnings:
        if e.date:
            month_abbr = e.date.strftime('%b')
            monthly_income[month_abbr] += float(e.amount)

    # Normalize for bar height (0–100%)
    max_val = max(monthly_income.values()) or 1
    for month in monthly_income:
        monthly_income[month] = int((monthly_income[month] / max_val) * 100)

        context = {
            "earnings": earnings,
            "total_earnings": sum(e.amount for e in earnings),
            "this_month": sum(e.amount for e in earnings if e.date.month == datetime.now().month),
            "completed_projects": earnings.count(),
            "withdrawn": sum(e.withdrawn_amount for e in earnings if hasattr(e, 'withdrawn_amount')),  # adjust if needed
            
            "monthly_income": monthly_income,
        }

        return render(request, "CommissionZeroApp/service_provider/earnings.html", context)


@role_required(['provider'])
def service_cards(request):
    services = ProviderService.objects.filter(provider=request.user)
    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/service_cards.html', {
        'services': services,
        'avg_rating': avg_rating
    })

@role_required(['provider'])
def add_service(request):
    if request.method == 'POST':
        form = ProviderServiceForm(request.POST)
        if form.is_valid():
            service = form.save(commit=False)
            service.provider = request.user
            service.save()
            return redirect('service_cards')
    else:
        form = ProviderServiceForm()

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/service_form.html', {
        'form': form,
        'action': 'Add',
        'avg_rating': avg_rating
    })

@role_required(['provider'])
def edit_service(request, service_id):
    service = get_object_or_404(ProviderService, id=service_id, provider=request.user)
    if request.method == 'POST':
        form = ProviderServiceForm(request.POST, instance=service)
        if form.is_valid():
            form.save()
            return redirect('service_cards')
    else:
        form = ProviderServiceForm(instance=service)

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/service_form.html', {
        'form': form,
        'action': 'Edit',
        'avg_rating': avg_rating
    })

@role_required(['provider'])
def delete_service(request, service_id):
    service = get_object_or_404(ProviderService, id=service_id, provider=request.user)
    service.delete()
    return redirect('service_cards')



@role_required(['provider'])
def portfolio(request,):
    return render(request, 'CommissionZeroApp/service_provider/portfolio.html')

def get_avg_rating(user):
    avg_rating = Review.objects.filter(provider=user).aggregate(avg=Avg('rating'))['avg']
    return round(avg_rating or 0, 1)


@role_required(['provider'])
def reviews_service(request):
    reviews = Review.objects.filter(provider=request.user).order_by('-created_at')
    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating, 1) if avg_rating else 0
    return render(request, 'CommissionZeroApp/service_provider/reviews_service.html', {
        'reviews': reviews,
        'avg_rating': avg_rating
    })




@role_required(['provider'])
def messages_service(request,):
    return render(request, 'CommissionZeroApp/service_provider/messages_service.html')


@role_required(['provider'])
@login_required
def profile(request):
    profile, created = ProviderProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        section = request.POST.get('section')

        if section == 'basic':
            profile.phone = request.POST.get('phone')
            profile.location = request.POST.get('location')
            profile.save()

        elif section == 'business':
            profile.business_name = request.POST.get('business_name')
            profile.services_offered = request.POST.get('services_offered')
            profile.experience = request.POST.get('experience')
            profile.save()

        elif section == 'account':
            email = request.POST.get('email')
            password = request.POST.get('passwor')
            confirm_password = request.POST.get('confirm_password')
            user = request.user
            if password == confirm_password:
                user.email = email
                if password:
                    user.set_password(password)
                user.save()
                return redirect('login')

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    context = {
        'profile': profile,
        'user': request.user,
        'avg_rating': avg_rating
    }
    return render(request, 'CommissionZeroApp/service_provider/profile.html', context)

@role_required(['provider'])
@login_required
def settings_service(request):
    user = request.user
    try:
        profile = ProviderProfile.objects.get(user=user)
    except ProviderProfile.DoesNotExist:
        profile = ProviderProfile.objects.create(user=user)

    if request.method == 'POST':
        username = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_password = request.POST.get('confirm_password')

        if username:
            user.username = username
        if email:
            user.email = email
        if phone:
            profile.phone = phone

        if new_password and new_password == confirm_password and user.check_password(current_password):
            user.set_password(new_password)
            update_session_auth_hash(request, user)

        user.save()
        profile.save()
        messages.success(request, 'Settings updated successfully.')
        return redirect('settings_service')

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    context = {
        'user': user,
        'profile': profile,
        'avg_rating': avg_rating
    }
    return render(request, 'CommissionZeroApp/service_provider/settings_service.html', context)

@login_required
def chat_view(request, username):
    other_user = get_object_or_404(User, username=username)

    # Get average rating if the other user is a provider
    avg_rating = None
    if hasattr(other_user, 'role') and other_user.role == 'provider':
        avg_rating = Review.objects.filter(provider=other_user).aggregate(avg=Avg('rating'))['avg']
        avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/chat.html', {
        'other_user': other_user,
        'avg_rating': avg_rating
    })




@role_required(['provider'])
@login_required
def service_chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    recent_users = Message.objects.filter(sender=request.user).values_list('receiver', flat=True).distinct()
    recent_users = User.objects.filter(id__in=recent_users)

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/messages_service.html', {
        'other_user': other_user,
        'messages': messages,
        'recent_users': recent_users,
        'avg_rating': avg_rating
    })



@role_required(['customer'])
@login_required
def customer_chat_index(request):
    recent_user_ids = Message.objects.filter(
        sender=request.user
    ).values_list('receiver', flat=True)

    received_from_ids = Message.objects.filter(
        receiver=request.user
    ).values_list('sender', flat=True)

    combined_ids = set(recent_user_ids) | set(received_from_ids)
    recent_users = User.objects.filter(id__in=combined_ids)

    return render(request, 'CommissionZeroApp/customer/messages_customer.html', {
        'recent_users': recent_users,
        'other_user': None,
        'messages': [],
    })



@role_required(['customer'])
@login_required
def customer_chat_view(request, username):
    other_user = get_object_or_404(User, username=username)
    
    messages = Message.objects.filter(
        sender__in=[request.user, other_user],
        receiver__in=[request.user, other_user]
    ).order_by('timestamp')

    recent_user_ids = Message.objects.filter(
        sender=request.user
    ).values_list('receiver', flat=True)

    received_from_ids = Message.objects.filter(
        receiver=request.user
    ).values_list('sender', flat=True)

    combined_ids = set(recent_user_ids) | set(received_from_ids)
    recent_users = User.objects.filter(id__in=combined_ids)

    return render(request, 'CommissionZeroApp/customer/messages_customer.html', {
        'other_user': other_user,
        'messages': messages,
        'recent_users': recent_users
    })



@role_required(['provider'])
@login_required
def service_chat_index(request):
    recent_user_ids = Message.objects.filter(
        sender=request.user
    ).values_list('receiver', flat=True)

    received_from_ids = Message.objects.filter(
        receiver=request.user
    ).values_list('sender', flat=True)

    combined_ids = set(recent_user_ids) | set(received_from_ids)
    recent_users = User.objects.filter(id__in=combined_ids)

    return render(request, 'CommissionZeroApp/service_provider/messages_service.html', {
        'recent_users': recent_users,
        'other_user': None,
        'messages': [],
    })




@role_required(['admin'])
@login_required
def admin_dashboard(request):
    if not request.user.is_superuser:
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return render(request, 'CommissionZeroApp/permission_denied.html', {'back_url': referer})
        return render(request, 'CommissionZeroApp/permission_denied.html', {'back_url': '/'})

    total_users = User.objects.count()
    total_providers = ProviderProfile.objects.count()
    total_customers = CustomerProfile.objects.count()

    recent_users = User.objects.order_by('-date_joined')[:5]

    recent_data = []
    for user in recent_users:
        full_name = f"{user.first_name} {user.last_name}".strip() or user.username

        if user.is_superuser:
            role = 'Admin'
        elif hasattr(user, 'providerprofile'):
            role = 'Provider'
        elif hasattr(user, 'customerprofile'):
            role = 'Customer'
        else:
            role = 'Unknown'

        recent_data.append({
            'name': full_name,
            'email': user.email,
            'role': role,
            'joined': localtime(user.date_joined).strftime('%Y-%m-%d')
        })

    context = {
        'total_users': total_users,
        'total_providers': total_providers,
        'total_customers': total_customers,
        'recent_users': recent_data,
    }
    return render(request, 'CommissionZeroApp/admin/admin_dashboard.html', context)


@role_required(['admin'])
@login_required
def all_users(request):
    all_users = User.objects.all()

    user_data = []
    for user in all_users:
        # Try to use full name, else fallback to username
        full_name = f"{user.first_name} {user.last_name}".strip()
        if not full_name:
            full_name = user.username  # fallback if name is missing

        # Determine user role
        if user.is_superuser:
            role = 'Admin'
        elif hasattr(user, 'providerprofile'):
            role = 'Service Provider'
        elif hasattr(user, 'customerprofile'):
            role = 'Customer'
        else:
            role = 'Unknown'

        user_data.append({
            'id': user.id,
            'name': full_name,
            'email': user.email,
            'role': role,
            'status': 'Active',  # You can extend this to real status if needed
            'joined': user.date_joined.date(),
        })

    context = {'users': user_data}
    return render(request, 'CommissionZeroApp/admin/all_users.html', context)


@role_required(['admin'])
@login_required
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_superuser:
        messages.error(request, "Admins cannot be deleted.")
        return redirect('all_users')

    if hasattr(user, 'customerprofile'):
        user.customerprofile.delete()
        user.delete()
        messages.success(request, "Customer deleted successfully.")
    elif hasattr(user, 'providerprofile'):
        user.providerprofile.delete()
        user.delete()
        messages.success(request, "Provider deleted successfully.")
    else:
        messages.error(request, "This user cannot be deleted.")

    return redirect('all_users')


@role_required(['admin'])
@login_required
def service_providers_admin(request):
    providers = ProviderProfile.objects.select_related('user').order_by('-user__date_joined')
    return render(request, 'CommissionZeroApp/admin/service_providers_admin.html', {'providers': providers})


@role_required(['admin'])
@login_required
def approve_provider(request, provider_id):
    provider = get_object_or_404(ProviderProfile, id=provider_id)
    provider.status = 'approved'
    provider.save()
    messages.success(request, f'{provider.user.username} approved.')
    return redirect('service_providers_admin')


@role_required(['admin'])
@login_required
def suspend_provider(request, provider_id):
    provider = get_object_or_404(ProviderProfile, id=provider_id)
    provider.status = 'suspended'
    provider.save()
    messages.warning(request, f'{provider.user.username} suspended.')
    return redirect('service_providers_admin')


@role_required(['admin'])
@login_required
def delete_provider(request, provider_id):
    provider = get_object_or_404(ProviderProfile, id=provider_id)
    user = provider.user
    provider.delete()
    user.delete()
    messages.error(request, f'{user.username} deleted.')
    return redirect('service_providers_admin')

@role_required(['admin'])
@login_required
def view_provider_dashboard_admin(request, provider_id):
    user = get_object_or_404(User, id=provider_id)
    provider = get_object_or_404(ProviderProfile, user=user)

    user = provider.user

    active_tenders = Tender.objects.filter(
        quotation__provider=user,
        status='open'
    ).distinct().count()

    pending_quotes = Quotation.objects.filter(provider=user, status='pending').count()
    active_projects = Quotation.objects.filter(provider=user, status='accepted').count()

    monthly_earnings = Quotation.objects.filter(
        provider=user,
        status='completed',
        created_at__month=timezone.now().month
    ).aggregate(total=Sum('total_cost'))['total'] or 0

    recent_quotes = Quotation.objects.filter(provider=user).order_by('-created_at')[:5]

    # ✅ ADD this block
    projects = PortfolioProject.objects.filter(provider=user)
    
    context = {
        'provider': provider,
        'active_tenders': active_tenders,
        'pending_quotes': pending_quotes,
        'active_projects': active_projects,
        'monthly_earnings': monthly_earnings,
        'recent_quotes': recent_quotes,
        'projects': projects,  # ✅ Add projects to context
    }

    return render(request, 'CommissionZeroApp/admin/view_provider_dashboard_admin.html', context)



@role_required(['admin'])
@login_required
def customers_admin(request):
    customers = CustomerProfile.objects.select_related('user').order_by('-user__date_joined')

    context = {
        'customers': customers
    }
    return render(request, 'CommissionZeroApp/admin/customers_admin.html', context)


@role_required(['admin'])
@login_required
def view_customer_detail(request, user_id):
    customer = get_object_or_404(User, id=user_id)

    active_tenders_count = Tender.objects.filter(user=customer, status='open').count()
    pending_quotes_count = Quotation.objects.filter(tender__user=customer, status='pending').count()
    active_projects_count = Tender.objects.filter(user=customer, status='ongoing').count()

    tenders = Tender.objects.filter(user=customer).annotate(num_quotes=Count('quotation')).order_by('-created_at')[:5]

    context = {
        'tenders': tenders,
        'active_tenders_count': active_tenders_count,
        'pending_quotes_count': pending_quotes_count,
        'active_projects_count': active_projects_count,
        'customer_user': customer,
    }
    return render(request, 'CommissionZeroApp/admin/view_customer_dashboard.html', context)


@role_required(['admin'])
@login_required
def delete_customer(request, user_id):
    user = get_object_or_404(User, id=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"Customer '{username}' has been deleted.")
    return redirect('customers_admin')



@role_required(['admin'])
@login_required
def delete_customer(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if hasattr(user, 'customerprofile'):
        user.delete()
        messages.success(request, "Customer deleted successfully.")
    else:
        messages.error(request, "This user is not a customer.")
    return redirect('customers_admin')


# Admin tenders management
@role_required(['admin'])
@login_required
def admin_tenders(request):
    tenders = Tender.objects.all().order_by('-created_at')
    return render(request, 'CommissionZeroApp/admin/admin_tenders.html', {'tenders': tenders})


@login_required
@role_required(['admin'])
def quotes_admin(request):
    quotations = Quotation.objects.select_related('tender', 'provider').all().order_by('-created_at')
    return render(request, 'CommissionZeroApp/admin/quotes_admin.html', {'quotations': quotations})

# views.py
@login_required
@role_required(['admin'])
def admin_view_quotation_detail(request, quotation_id):
    quotation = get_object_or_404(Quotation, id=quotation_id)
    return render(request, 'CommissionZeroApp/admin/view_quote_detail.html', {'quotation': quotation})


@login_required
@role_required(['admin'])
def delete_quotation_admin(request, quotation_id):
    quote = get_object_or_404(Quotation, id=quotation_id)
    quote.delete()
    return redirect('quotes_admin')



@role_required(['admin'])
@login_required
def admin_earnings(request):
    earnings = Earning.objects.all().order_by('-date')
    context = {
        'earnings': earnings
    }
    return render(request, 'CommissionZeroApp/admin/admin_earnings.html', context)


@role_required(['admin'])
@login_required
def admin_earnings_detail(request, provider_id):
    today = date.today()
    week_start = today - timedelta(days=today.weekday())

    earnings = Earning.objects.filter(provider_id=provider_id)
    this_week = earnings.filter(date__gte=week_start)

    total_earnings = earnings.aggregate(Sum('amount'))['amount__sum'] or 0
    this_month = earnings.filter(date__month=today.month).aggregate(Sum('amount'))['amount__sum'] or 0
    withdrawn = 0  # You can replace this with actual withdrawn logic
    completed_projects = earnings.count()
    client_projects = earnings.values('client_name', 'project_name').distinct()

    # Monthly breakdown
    monthly_income = {}
    for month in range(1, 13):
        amount = earnings.filter(date__month=month).aggregate(Sum('amount'))['amount__sum'] or 0
        monthly_income[date(2025, month, 1).strftime('%b')] = int(amount)

    context = {
        'total_earnings': total_earnings,
        'this_month': this_month,
        'withdrawn': withdrawn,
        'completed_projects': completed_projects,
        'earnings': earnings,
        'monthly_income': monthly_income,
        'provider': earnings.first().provider if earnings else None,
        'client_projects': client_projects,
    }
    return render(request, 'CommissionZeroApp/admin/admin_earnings_detail.html', context)

@role_required(['admin'])
@login_required
def delete_earning(request, earning_id):
    earning = get_object_or_404(Earning, id=earning_id)
    if request.method == "POST":
        earning.delete()
        messages.success(request, "Earning deleted successfully.")
    return redirect('admin_earnings')


@role_required(['admin'])
@login_required
def reviews_admin(request):
    reviews = Review.objects.all().select_related('provider', 'customer')
    return render(request, 'CommissionZeroApp/admin/reviews_admin.html', {
        'reviews': reviews
    })

@role_required(['admin'])
@login_required
def view_review_admin(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'CommissionZeroApp/admin/view_review_admin.html', {
        'review': review
    })

@role_required(['admin'])
@login_required
def delete_review_admin(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == "POST":
        review.delete()
    return redirect('reviews_admin')



@role_required(['admin'])
@login_required
def platform_settings(request):
    return render(request, 'CommissionZeroApp/admin/platform_settings.html')


@role_required(['admin'])
@login_required
def admin_permissions(request):
    return render(request, 'CommissionZeroApp/admin/admin_permissions.html')


@role_required(['admin'])
@login_required
def help_center_admin(request):
    return render(request, 'CommissionZeroApp/admin/admin_help_center.html')

@role_required(['provider'])
@login_required
def portfolio(request):
    projects = PortfolioProject.objects.filter(provider=request.user)
    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/portfolio.html', {
        'projects': projects,
        'avg_rating': avg_rating
    })


@role_required(['provider'])
@login_required
def add_portfolio_project(request):
    if request.method == 'POST':
        form = PortfolioProjectForm(request.POST, request.FILES)
        if form.is_valid():
            project = form.save(commit=False)
            project.provider = request.user
            project.save()
            return redirect('portfolio')
    else:
        form = PortfolioProjectForm()

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/add_project.html', {
        'form': form,
        'avg_rating': avg_rating
    })



@role_required(['provider'])
@login_required
def edit_portfolio_project(request, project_id):
    project = get_object_or_404(PortfolioProject, id=project_id, provider=request.user)
    if request.method == 'POST':
        form = PortfolioProjectForm(request.POST, request.FILES, instance=project)
        if form.is_valid():
            form.save()
            return redirect('portfolio')
    else:
        form = PortfolioProjectForm(instance=project)

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/edit_project.html', {
        'form': form,
        'avg_rating': avg_rating
    })


@role_required(['provider'])
@login_required
def delete_portfolio_project(request, project_id):
    project = get_object_or_404(PortfolioProject, id=project_id, provider=request.user)
    if request.method == 'POST':
        project.delete()
        return redirect('portfolio')

    avg_rating = Review.objects.filter(provider=request.user).aggregate(avg=Avg('rating'))['avg']
    avg_rating = round(avg_rating or 0, 1)

    return render(request, 'CommissionZeroApp/service_provider/delete_project.html', {
        'project': project,
        'avg_rating': avg_rating
    })



@role_required(['customer'])
def view_provider_portfolio(request, provider_id):
    provider = get_object_or_404(User, id=provider_id)
    projects = PortfolioProject.objects.filter(provider=provider)
    context = {
        'provider': provider,
        'projects': projects
    }
    return render(request, 'CommissionZeroApp/customer/view_provider_portfolio.html', context)
