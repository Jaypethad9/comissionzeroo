from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import path
from . import views

urlpatterns = [
    path('messages_customer/<str:username>/', views.customer_chat_view, name='customer_chat'),
    path('messages_customer/', views.customer_chat_index,name='messages_customer'), 
    path('messages_service/<str:username>/', views.service_chat_view, name='service_chat'),
    path('messages_service/', views.service_chat_index,name='messages_service'), 
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('home/', views.home, name='home'),
    
    path('login/', views.user_login, name='login'),
     path('password-reset/', 
         auth_views.PasswordResetView.as_view(template_name='password_reset.html'), 
         name='password_reset'),

    path('password-reset/done/', 
         auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), 
         name='password_reset_done'),

    path('password-reset-confirm/<uidb64>/<token>/', 
         auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), 
         name='password_reset_confirm'),

    path('password-reset-complete/', 
         auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), 
         name='password_reset_complete'),

    path('register/', views.register_customer, name='register'),
    path('register-provider/', views.register_provider, name='register_provider'),
    path('verify-provider-otp/', views.register_provider_otp, name='verify_provider_otp'),
    path('verify-customer-otp/', views.verify_customer_otp, name='verify_customer_otp'),
    path('logout/', views.logout_view, name='logout'),
    path('waiting_approval/', views.waiting_approval, name='waiting_approval'),
    path('tender_creation/', views.tender_creation, name='tender_creation'),
    path('my_tenders/', views.my_tenders, name='my_tenders'),
    path('tenders/', views.tenders, name='tenders'),
    path('my_tenders/<int:tender_id>/', views.tender_detail_customer, name='tender_detail_customer'),
    path('service_tenders/<int:tender_id>/', views.tender_detail_service, name='service_tenders'),


    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('service/', views.service, name='service'),
    path('customer_dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('reviews/', views.reviews, name='reviews'),
    path('settings/', views.settings, name='settings'),
    path('change-password/', views.change_password, name='change_password'),  # ✅
    path('help_center/', views.help_center, name='help_center'),
    path('find_professionals/', views.find_professionals, name='find_professionals'),
    path('portfolio/view/<int:provider_id>/', views.view_provider_portfolio, name='view_provider_portfolio'),

    path('verify-password/', views.verify_password, name='verify_password'),
    path('quotation/<int:quotation_id>/accept/', views.accept_quotation, name='accept_quotation'),
    path('quotation/<int:quotation_id>/reject/', views.reject_quotation, name='reject_quotation'),
    path('quotation/<int:quotation_id>/complete/', views.mark_quotation_completed, name='mark_quotation_completed'),
    path('review/<int:tender_id>/', views.submit_review, name='submit_review'),
    path('reviews/<int:tender_id>/', views.view_reviews, name='view_reviews'),
    path('delete_review/<int:review_id>/', views.delete_review, name='delete_review'),
    path('track_tender/<int:tender_id>/', views.track_tender, name='track_tender'),
    



    # service provider pages
    path('service_dashboard/', views.service_dashboard, name='service_dashboard'), 
    path('quotes/', views.quotes, name='quotes'),
    path('earnings/', views.earnings, name='earnings'),
    path('service_cards/', views.service_cards, name='service_cards'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('portfolio/add/', views.add_portfolio_project, name='add_portfolio_project'),
    path('portfolio/edit/<int:project_id>/', views.edit_portfolio_project, name='edit_portfolio_project'),
    path('portfolio/delete/<int:project_id>/', views.delete_portfolio_project, name='delete_portfolio_project'),
    path('reviews_service/', views.reviews_service, name='reviews_service'),
    path('profile/', views.profile, name='profile'),
    path('settings_service/', views.settings_service, name='settings_service'),
    path('chat/<str:username>/', views.chat_view, name='chat_view'),
    path('service_cards/', views.service_cards, name='service_cards'),
    path('service/add/', views.add_service, name='add_service'),
    path('service/edit/<int:service_id>/', views.edit_service, name='edit_service'),
    path('service/delete/<int:service_id>/', views.delete_service, name='delete_service'),
    path('submit-quote/<int:tender_id>/', views.submit_quotation, name='submit_quotation'),
    path('quotation/<int:tender_id>/', views.view_quotation, name='view_quotation'),
    path('quotation/<int:quotation_id>/progress/', views.update_progress, name='update_progress'),
    path('request-otp/', views.request_otp_view, name='request_otp'),
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    

    
    
    #admin
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('all_users/', views.all_users, name='all_users'),
    path('admin_dashboard/view_provider/<int:provider_id>/', views.view_provider_dashboard_admin, name='view_provider_dashboard_admin'),
    path('view_customer/<int:user_id>/', views.view_customer_detail, name='view_customer_detail'),

    path('service_providers_admin/', views.service_providers_admin, name='service_providers_admin'),
    path('service_providers_admin/<int:provider_id>/approve/', views.approve_provider, name='approve_provider'),
    path('service_providers_admin/<int:provider_id>/suspend/', views.suspend_provider, name='suspend_provider'),
    path('service_providers_admin/<int:provider_id>/delete/', views.delete_provider, name='delete_provider'),
    path('admin_dashboard/view_provider/<int:provider_id>/', views.view_provider_dashboard_admin, name='view_provider_dashboard_admin'),

    path('customers_admin/', views.customers_admin, name='customers_admin'),
    path('view_customer/<int:user_id>/', views.view_customer_detail, name='view_customer_detail'),

    path('delete_customer/<int:user_id>/', views.delete_customer, name='delete_customer'),
    path('customers_admin/', views.customers_admin, name='customers_admin'),
    path('admin_tenders/', views.admin_tenders, name='admin_tenders'),
    path('quotes_admin/', views.quotes_admin, name='quotes_admin'),
    path('quotes_admin/view/<int:quotation_id>/', views.admin_view_quotation_detail, name='admin_view_quotation_detail'),
    path('quotes_admin/delete/<int:quotation_id>/', views.delete_quotation_admin, name='delete_quotation_admin'),

    # path('delete_quotation_admin/<int:quotation_id>/', views.delete_quotation_admin, name='delete_quotation_admin'),
    
    path('admin_earnings/', views.admin_earnings, name='admin_earnings'),
    path('admin_earnings/view/<int:provider_id>/', views.admin_earnings_detail, name='admin_earnings_detail'),
    path('admin_earnings/delete/<int:earning_id>/', views.delete_earning, name='delete_earning'),


    path('delete_user/<int:user_id>/', views.delete_user, name='user_delete'),
    path('reviews_admin/', views.reviews_admin, name='reviews_admin'),
    path('platform_settings/', views.platform_settings, name='platform_settings'),
    path('admin_permissions/', views.admin_permissions, name='admin_permissions'),
    path('help_center_admin/', views.help_center_admin, name='help_center_admin'),
    path('review_admin/<int:review_id>/', views.view_review_admin, name='view_review_admin'),
    path('review_admin/delete/<int:review_id>/', views.delete_review_admin, name='delete_review_admin'),


]

