from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.views.decorators.http import require_http_methods
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.db.models import Q, Avg, Sum
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from deliveries.models import Delivery
from .forms import UserRegisterForm, UserLoginForm
from .models import UserProfile, Earnings
import json
from django.core.mail import send_mail
import googlemaps
from datetime import timedelta
from decimal import Decimal

@csrf_protect
def register(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            form = UserRegisterForm(data)
            if form.is_valid():
                try:
                    with transaction.atomic():
                        # Create User instance
                        user = form.save()
                        user.email = form.cleaned_data['email']
                        user.first_name = form.cleaned_data['first_name']
                        user.last_name = form.cleaned_data['last_name']
                        user.save()

                        # Update or create UserProfile
                        profile = user.userprofile
                        profile.first_name = form.cleaned_data['first_name']
                        profile.last_name = form.cleaned_data['last_name']
                        profile.phone_number = form.cleaned_data['phone_number']
                        profile.address = form.cleaned_data['address']
                        profile.user_type = form.cleaned_data['user_type']
                        if form.cleaned_data['user_type'] == 'worker':
                            profile.vehicle_type = form.cleaned_data['vehicle_type']
                        profile.save()

                        # Log the user in
                        login(request, user)
                        if request.content_type == 'application/json':
                            return JsonResponse({"message": "Registration successful", "redirect": "dashboard"})
                        else:
                            messages.success(request, "Account created successfully!")
                            return redirect('dashboard')

                except Exception as e:
                    if request.content_type == 'application/json':
                        return JsonResponse({"error": str(e)}, status=500)
                    else:
                        messages.error(request, f"Error: {str(e)}")
                        return redirect('register')
            else:
                if request.content_type == 'application/json':
                    errors = {field: error[0] for field, error in form.errors.items()}
                    return JsonResponse({"error": "Validation failed", "errors": errors}, status=400)
                else:
                    messages.error(request, "Please correct the errors below.")
                    return render(request, 'users/register.html', {'form': form})
        except json.JSONDecodeError:
            messages.error(request, "Invalid request format")
            return redirect('register')
    else:
        form = UserRegisterForm()
    return render(request, 'users/register.html', {'form': form})

@csrf_protect
def user_login(request):
    if request.method == 'POST':
        try:
            # Get data from either JSON or form data
            data = json.loads(request.body) if request.content_type == 'application/json' else request.POST
            username = data.get('username', '')
            password = data.get('password', '')
            remember_me = data.get('remember_me', False)

            if not username or not password:
                if request.content_type == 'application/json':
                    return JsonResponse({"error": "Username and password are required."}, status=400)
                messages.error(request, "Username and password are required.")
                return redirect('login')

            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                # For AJAX requests, return 200 OK
                if request.content_type == 'application/json':
                    return JsonResponse({}, status=200)
                # For form submissions, redirect directly
                return redirect('dashboard')
            else:
                if request.content_type == 'application/json':
                    return JsonResponse({"error": "Invalid credentials"}, status=401)
                messages.error(request, "Invalid credentials")
                return redirect('login')

        except json.JSONDecodeError:
            if request.content_type == 'application/json':
                return JsonResponse({"error": "Invalid JSON data"}, status=400)
            messages.error(request, "Invalid request format")
            return redirect('login')
        except Exception as e:
            if request.content_type == 'application/json':
                return JsonResponse({"error": str(e)}, status=500)
            messages.error(request, str(e))
            return redirect('login')

    return render(request, 'users/login.html')

@login_required
def user_logout(request):
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return redirect('home')

# Public Pages
def home(request):
    return render(request, 'users/home.html')

def about(request):
    return render(request, 'users/about.html')

def contact(request):
    if request.method == 'POST':
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Basic validation
        if not all([name, email, subject, message]):
            messages.error(request, "All fields are required.")
            return redirect('contact')
        
        try:
            # Send email
            send_mail(
                f'Contact Form: {subject}',
                f'From: {name} <{email}>\n\n{message}',
                settings.DEFAULT_FROM_EMAIL,
                [settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(request, "Your message has been sent. We'll get back to you soon!")
            return redirect('contact')
        except Exception as e:
            messages.error(request, f"There was an error sending your message: {str(e)}")
            return redirect('contact')
    
    return render(request, 'users/contact.html')

def resources(request):
    return render(request, 'users/resources.html')

def careers(request):
    return render(request, 'users/careers.html')

def terms(request):
    return render(request, 'users/terms.html')

def privacy(request):
    return render(request, 'users/privacy.html')

@login_required(login_url='login')
def dashboard(request):
    user_type = request.user.userprofile.user_type
    
    if user_type == 'customer':
        # Customer Dashboard - updated to include completed and cancelled orders
        active_deliveries = Delivery.objects.filter(
            customer=request.user,
            status__in=['PENDING', 'ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
        ).order_by('-created_at')
        
        # Get completed and cancelled deliveries
        completed_deliveries = Delivery.objects.filter(
            customer=request.user,
            status='DELIVERED'
        ).order_by('-delivery_time')[:10]  # Last 10 completed deliveries
        
        cancelled_deliveries = Delivery.objects.filter(
            customer=request.user,
            status='CANCELLED'
        ).order_by('-updated_at')[:10]  # Last 10 cancelled deliveries

        context = {
            'active_deliveries': active_deliveries,
            'completed_deliveries': completed_deliveries,
            'cancelled_deliveries': cancelled_deliveries,
            'pending_deliveries': Delivery.objects.filter(
                customer=request.user,
                status='PENDING'
            ),
            'in_transit_deliveries': Delivery.objects.filter(
                customer=request.user,
                status='IN_TRANSIT'
            ),
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            'active_tab': 'overview'
        }
        return render(request, 'users/customer_dashboard.html', context)
    
    else:
        # Worker Dashboard - updated to use Earnings model
        current_job = Delivery.objects.filter(
            assigned_driver=request.user,
            status__in=['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
        ).first()

        # Get today's date range
        today_start = timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = today_start + timedelta(days=1)
        
        # Get daily earnings
        daily_earnings = Earnings.objects.filter(
            worker=request.user,
            timestamp__gte=today_start,
            timestamp__lt=today_end
        ).order_by('-timestamp')
        
        daily_total = daily_earnings.aggregate(total=Sum('amount'))['total'] or 0
        
        # Get weekly earnings (last 7 days)
        week_start = today_start - timedelta(days=6)  # Last 7 days including today
        weekly_earnings = Earnings.objects.filter(
            worker=request.user,
            timestamp__gte=week_start,
            timestamp__lt=today_end
        )
        
        weekly_total = weekly_earnings.aggregate(total=Sum('amount'))['total'] or 0
        
        # Prepare weekly chart data
        weekly_data = []
        weekly_labels = []
        
        for i in range(7):
            day = week_start + timedelta(days=i)
            day_end = day + timedelta(days=1)
            day_earnings = Earnings.objects.filter(
                worker=request.user,
                timestamp__gte=day,
                timestamp__lt=day_end
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            weekly_data.append(float(day_earnings))
            weekly_labels.append(day.strftime('%a'))
        
        # Get monthly earnings (last 30 days)
        month_start = today_start - timedelta(days=29)  # Last 30 days including today
        monthly_earnings = Earnings.objects.filter(
            worker=request.user,
            timestamp__gte=month_start,
            timestamp__lt=today_end
        )
        
        monthly_total = monthly_earnings.aggregate(total=Sum('amount'))['total'] or 0
        
        # Prepare monthly chart data
        monthly_data = []
        monthly_labels = []
        
        # Group by week for the monthly chart
        for i in range(0, 30, 7):
            week_start_date = month_start + timedelta(days=i)
            week_end_date = min(week_start_date + timedelta(days=7), today_end)
            week_earnings = Earnings.objects.filter(
                worker=request.user,
                timestamp__gte=week_start_date,
                timestamp__lt=week_end_date
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            monthly_data.append(float(week_earnings))
            monthly_labels.append(f"{week_start_date.strftime('%d %b')}-{(week_end_date - timedelta(days=1)).strftime('%d %b')}")
        
        # Calculate average completion time for delivered jobs
        delivered_jobs = Delivery.objects.filter(
            assigned_driver=request.user,
            status='DELIVERED',
            delivery_time__isnull=False
        )
        
        avg_completion_time = None
        if delivered_jobs.exists():
            total_time = timezone.timedelta()
            count = 0
            for job in delivered_jobs:
                if job.delivery_time and job.created_at:
                    total_time += job.delivery_time - job.created_at
                    count += 1
            if count > 0:
                avg_completion_time = total_time / count

        # Get available jobs
        available_jobs = Delivery.objects.filter(
            status='PENDING',
            assigned_driver__isnull=True
        ).order_by('-created_at')

        # Get job statistics
        job_stats = {
            'total_completed': delivered_jobs.count(),
            'total_cancelled': Delivery.objects.filter(
                assigned_driver=request.user,
                status='CANCELLED'
            ).count(),
            'avg_completion_time': avg_completion_time
        }

        # Get cancelled jobs
        cancelled_jobs = Delivery.objects.filter(
            assigned_driver=request.user,
            status='CANCELLED'
        ).order_by('-updated_at')[:10]  # Last 10 cancelled jobs
        
        context = {
            'current_job': current_job,
            'active_jobs': Delivery.objects.filter(
                assigned_driver=request.user,
                status__in=['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
            ),
            'completed_jobs': delivered_jobs.order_by('-delivery_time')[:10],  # Last 10 completed jobs
            'cancelled_jobs': cancelled_jobs,  # Added cancelled jobs to context
            'available_jobs': available_jobs,
            'job_stats': job_stats,
            'earnings': daily_total,  # Today's earnings for the stats card
            'active_tab': 'overview',
            'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY,
            # New earnings data for the earnings tab
            'daily_earnings': daily_earnings,
            'daily_total': daily_total,
            'weekly_earnings': weekly_earnings,
            'weekly_total': weekly_total,
            'monthly_earnings': monthly_earnings,
            'monthly_total': monthly_total,
            'weekly_labels': json.dumps(weekly_labels),
            'weekly_data': json.dumps(weekly_data),
            'monthly_labels': json.dumps(monthly_labels),
            'monthly_data': json.dumps(monthly_data),
            'today_date': timezone.now(),
        }
        return render(request, 'users/worker_dashboard.html', context)

@login_required
def user_profile(request):
    context = {
        'user': request.user,
        'total_deliveries': Delivery.objects.filter(
            Q(sender_name=request.user.username) | Q(recipient_name=request.user.username)
        ).count(),
        'completed_deliveries': Delivery.objects.filter(
            Q(sender_name=request.user.username) | Q(recipient_name=request.user.username),
            status='DELIVERED'
        ).count()
    }
    return render(request, 'users/profile.html', context)

@login_required
@require_http_methods(["POST"])
@csrf_protect
def update_profile(request):
    try:
        data = json.loads(request.body)
        user = request.user

        # Update basic info
        if 'email' in data:
            try:
                validate_email(data['email'])
                if User.objects.exclude(pk=user.pk).filter(email=data['email']).exists():
                    return JsonResponse({'error': 'Email already in use'}, status=400)
                user.email = data['email']
            except ValidationError:
                return JsonResponse({'error': 'Invalid email format'}, status=400)

        if 'first_name' in data:
            user.first_name = data['first_name']
            user.userprofile.first_name = data['first_name']

        if 'last_name' in data:
            user.last_name = data['last_name']
            user.userprofile.last_name = data['last_name']

        # Update profile info
        profile = user.userprofile
        if 'phone_number' in data:
            profile.phone_number = data['phone_number']

        if 'address' in data:
            profile.address = data['address']

        if 'vehicle_type' in data and profile.user_type == 'worker':
            profile.vehicle_type = data['vehicle_type']

        # Save changes
        user.save()
        profile.save()

        return JsonResponse({'success': 'Profile updated successfully'})
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

@login_required
def new_delivery(request):
    if request.method == 'POST':
        # Process form data to create a new delivery
        try:
            from deliveries.models import Delivery
            import uuid
            from decimal import Decimal
            
            # Generate a unique order ID
            order_id = f"QD-{uuid.uuid4().hex[:8].upper()}"
            
            # Create the delivery object
            delivery = Delivery(
                order_id=order_id,
                customer=request.user,
                
                # Package details
                package_description=request.POST.get('package_description', ''),
                package_type=request.POST.get('package_type', 'parcel'),
                weight=Decimal(request.POST.get('weight', '1.0')),
                
                # Pickup location details
                pickup_street=request.POST.get('pickup_street', ''),
                pickup_building=request.POST.get('pickup_building', ''),
                pickup_city=request.POST.get('pickup_city', ''),
                pickup_area=request.POST.get('pickup_area', ''),
                pickup_landmark=request.POST.get('pickup_landmark', ''),
                
                # Delivery location details
                delivery_street=request.POST.get('delivery_street', ''),
                delivery_building=request.POST.get('delivery_building', ''),
                delivery_city=request.POST.get('delivery_city', ''),
                delivery_area=request.POST.get('delivery_area', ''),
                delivery_landmark=request.POST.get('delivery_landmark', ''),
                
                # Contact information
                sender_name=request.POST.get('sender_name', request.user.get_full_name()),
                sender_phone=request.POST.get('sender_phone', ''),
                recipient_name=request.POST.get('recipient_name', ''),
                recipient_phone=request.POST.get('recipient_phone', ''),
                delivery_notes=request.POST.get('delivery_notes', ''),
                
                # Payment information
                payment_method=request.POST.get('payment_method', 'MPESA'),
                payment_status='PENDING',
                
                # Calculate amount based on weight
                amount=Decimal('200.00') + (Decimal(request.POST.get('weight', '1.0')) * Decimal('100.00')),
                
                # Set initial status
                status='PENDING'
            )
            
            # Save the delivery
            delivery.save()
            
            messages.success(request, f"Delivery created successfully! Your tracking ID is {delivery.tracking_id}")
            return redirect('dashboard')
            
        except Exception as e:
            messages.error(request, f"Error creating delivery: {str(e)}")
            return render(request, 'users/new_delivery.html')
            
    return render(request, 'users/new_delivery.html')

@login_required
def my_deliveries(request):
    # Get all deliveries categorized by status
    active_deliveries = Delivery.objects.filter(
        customer=request.user,
        status__in=['PENDING', 'PICKED_UP', 'IN_TRANSIT', 'ASSIGNED']
    ).order_by('-created_at')
    
    completed_deliveries = Delivery.objects.filter(
        customer=request.user,
        status='DELIVERED'
    ).order_by('-delivery_time')[:20]  # Last 20 completed deliveries
    
    cancelled_deliveries = Delivery.objects.filter(
        customer=request.user,
        status='CANCELLED'
    ).order_by('-updated_at')[:20]  # Last 20 cancelled deliveries
    
    context = {
        'active_deliveries': active_deliveries,
        'completed_deliveries': completed_deliveries,
        'cancelled_deliveries': cancelled_deliveries,
        'google_maps_api_key': settings.GOOGLE_MAPS_API_KEY
    }
    
    return render(request, 'users/my_deliveries.html', context)

@login_required
def delivery_detail(request, delivery_id):
    delivery = get_object_or_404(Delivery, id=delivery_id)
    return render(request, 'users/delivery_detail.html', {'delivery': delivery})

@login_required
def delivery_tracking(request, tracking_id):
    delivery = get_object_or_404(Delivery, tracking_id=tracking_id)
    return render(request, 'users/delivery_tracking.html', {'delivery': delivery})

@login_required
def my_jobs(request):
    # Get all jobs categorized by status
    active_jobs = Delivery.objects.filter(
        assigned_driver=request.user,
        status__in=['ASSIGNED', 'PICKED_UP', 'IN_TRANSIT']
    ).order_by('-created_at')
    
    completed_jobs = Delivery.objects.filter(
        assigned_driver=request.user,
        status='DELIVERED'
    ).order_by('-delivery_time')[:20]  # Last 20 completed jobs
    
    cancelled_jobs = Delivery.objects.filter(
        assigned_driver=request.user,
        status='CANCELLED'
    ).order_by('-updated_at')[:20]  # Last 20 cancelled jobs
    
    context = {
        'active_jobs': active_jobs,
        'completed_jobs': completed_jobs,
        'cancelled_jobs': cancelled_jobs,
    }
    
    return render(request, 'users/my_jobs.html', context)

@login_required
def accept_job(request, job_id):
    job = get_object_or_404(Delivery, id=job_id)
    job.assigned_driver = request.user
    job.status = 'ASSIGNED'
    job.save()
    return redirect('dashboard')

@login_required
def update_job_status(request, job_id):
    if request.method == 'POST':
        job = get_object_or_404(Delivery, id=job_id)
        status = request.POST.get('status')
        job.status = status
        
        # If delivery is marked as delivered, record the delivery time
        if status == 'DELIVERED':
            job.delivery_time = timezone.now()
            
            try:
                # Calculate earnings amount (80% of delivery fee)
                # Ensure amount is a valid decimal value
                delivery_amount = job.amount if job.amount is not None else Decimal('0.00')
                earnings_amount = delivery_amount * Decimal('0.8')
                
                # Create an earnings record for this delivery
                Earnings.objects.create(
                    worker=request.user,
                    delivery=job,
                    amount=earnings_amount,
                    earning_type='DELIVERY',
                    description=f"Delivery completion: {job.tracking_id}"
                )
                
                messages.success(request, f"Delivery marked as complete. You earned ${earnings_amount:.2f}")
            except Exception as e:
                # Log the error but don't prevent the delivery from being marked as complete
                print(f"Error creating earnings record: {str(e)}")
                messages.warning(request, "Delivery marked as complete, but there was an issue recording your earnings.")
        
        job.save()
        return redirect('dashboard')
    return redirect('dashboard')

@login_required
def cancel_delivery(request, tracking_id):
    delivery = get_object_or_404(Delivery, tracking_id=tracking_id)
    delivery.status = 'CANCELLED'
    delivery.save()
    return redirect('my_deliveries')

def job_application(request, job_id):
    # Process job application
    return render(request, 'users/job_application.html')

@login_required
def rate_worker(request, delivery_id):
    """Handle rating submission for workers"""
    from django.db.models import Avg
    from django.views.decorators.http import require_http_methods
    
    delivery = get_object_or_404(Delivery, id=delivery_id, customer=request.user)
    
    if not delivery.assigned_driver:
        messages.error(request, "This delivery doesn't have an assigned worker to rate.")
        return redirect('dashboard')
    
    if delivery.worker_rating:
        messages.info(request, "You have already rated this worker.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        try:
            rating = int(request.POST.get('rating'))
            if rating < 1 or rating > 5:
                raise ValueError("Rating must be between 1 and 5")
                
            comment = request.POST.get('comment', '')
            
            # Save the rating to the delivery
            delivery.worker_rating = rating
            delivery.worker_rating_comment = comment
            delivery.save()
            
            # Update worker's average rating
            worker_profile = delivery.assigned_driver.userprofile
            worker_deliveries = Delivery.objects.filter(assigned_driver=delivery.assigned_driver, worker_rating__isnull=False)
            worker_profile.average_rating = worker_deliveries.aggregate(Avg('worker_rating'))['worker_rating__avg']
            worker_profile.save()
            
            messages.success(request, f"Thank you for rating {delivery.assigned_driver.get_full_name()}!")
        except (ValueError, TypeError) as e:
            messages.error(request, f"Error submitting rating: {str(e)}")
    
    return redirect('dashboard')
