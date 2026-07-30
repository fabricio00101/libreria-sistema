from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Autenticación
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('registro/', views.RegistroView.as_view(), name='registro'),
    
    # Búsqueda Global
    path('buscar/', views.BusquedaGlobalView.as_view(), name='busqueda_global'),
    
    # Libros
    path('libros/', views.LibroListView.as_view(), name='libro_list'),
    path('libros/nuevo/', views.LibroCreateView.as_view(), name='libro_create'),
    path('libros/editar/<str:isbn>/', views.LibroUpdateView.as_view(), name='libro_update'),
    path('libros/eliminar/<str:isbn>/', views.LibroDeleteView.as_view(), name='libro_delete'),
    
    # Miembros
    path('miembros/', views.MiembroListView.as_view(), name='miembro_list'),
    path('miembros/nuevo/', views.MiembroCreateView.as_view(), name='miembro_create'),
    path('miembros/editar/<int:pk>/', views.MiembroUpdateView.as_view(), name='miembro_update'),
    path('miembros/eliminar/<int:pk>/', views.MiembroDeleteView.as_view(), name='miembro_delete'),
    
    # Préstamos
    path('prestamos/', views.PrestamoListView.as_view(), name='prestamo_list'),
    path('prestamos/nuevo/', views.PrestamoCreateView.as_view(), name='prestamo_create'),
    path('prestamos/devolver/<int:pk>/', views.PrestamoReturnView.as_view(), name='prestamo_return'),
    path('prestamos/pagar/<int:pk>/', views.PrestamoPayView.as_view(), name='prestamo_pay'),
]
