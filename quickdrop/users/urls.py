from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Root URL
    path('', views.home, name='home'),
    
    # Authentication Routes
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),

    # Protected Routes
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.user_profile, name='profile'),
    path('profile/update/', views.update_profile, name='update_profile'),

    # Public Pages
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),  
    path('resources/', views.resources, name='resources'),
    path('careers/', views.careers, name='careers'),
    path('terms/', views.terms, name='terms'),
    path('privacy/', views.privacy, name='privacy'),

    # Delivery Routes
    path('new-delivery/', views.new_delivery, name='new_delivery'),
    path('my-deliveries/', views.my_deliveries, name='my_deliveries'),
    path('delivery/<uuid:tracking_id>/cancel/', views.cancel_delivery, name='cancel_delivery'),
    path('delivery/<uuid:tracking_id>/track/', views.delivery_tracking, name='delivery_tracking'),
    path('delivery/<int:delivery_id>/', views.delivery_detail, name='delivery_detail'),
    path('delivery/<int:delivery_id>/rate/', views.rate_worker, name='rate_worker'),

    # Job Actions
    path('my-jobs/', views.my_jobs, name='my_jobs'),
    path('jobs/<int:job_id>/accept/', views.accept_job, name='accept_job'),
    path('jobs/<int:job_id>/update-status/', views.update_job_status, name='update_job_status'),

    # Contact and Careers
    path('careers/', views.careers, name='careers'),
    path('careers/apply/<int:job_id>/', views.job_application, name='job_application'),

    # Django Built-in Auth Views (Optional)
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset_done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password_reset_confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password_reset_complete/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
]
