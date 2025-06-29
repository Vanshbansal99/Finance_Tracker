from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup_view, name='signup'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('add-transaction/', views.add_transaction, name='add_transaction'),
    path('history/', views.history, name='history'),
    path('export/', views.export_csv, name='export_csv'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('report/', views.report, name='report'),

]
