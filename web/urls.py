from django.urls import path
from . import views

urlpatterns = [
        path('submit/expense/', views.submit_expense, name='submit_expense'),
        path('submit/income/', views.submit_income, name='submit_income'),
        path('accounts/register/',views.register, name='register'),
        path('',views.index, name='index'),
        path('accounts/login/',views.user_login, name='user_login'),
        path('accounts/logout/',views.user_logout, name='user_logout'),


]
