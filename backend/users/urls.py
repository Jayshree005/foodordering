from django.urls import path
from .views import login_user, profile, signup_user, submit_contact_message
from .admin_views import admin_overview, admin_user_details, admin_users

urlpatterns = [

    path('login/', login_user, name='login'),

    path('signup/', signup_user, name='signup'),
    path('contact/', submit_contact_message, name='contact'),
    path('profile/', profile, name='profile'),
    path('admin/overview/', admin_overview, name='admin-overview'),
    path('admin/users/', admin_users, name='admin-users'),
    path('admin/users/<int:user_id>/', admin_user_details, name='admin-user-details'),

]