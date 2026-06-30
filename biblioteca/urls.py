from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Libros
    path('libros/', views.libro_list, name='libro_list'),
    path('libros/nuevo/', views.libro_create, name='libro_create'),
    path('libros/editar/<str:isbn>/', views.libro_update, name='libro_update'),
    path('libros/eliminar/<str:isbn>/', views.libro_delete, name='libro_delete'),
    
    # Miembros
    path('miembros/', views.miembro_list, name='miembro_list'),
    path('miembros/nuevo/', views.miembro_create, name='miembro_create'),
    path('miembros/editar/<int:pk>/', views.miembro_update, name='miembro_update'),
    path('miembros/eliminar/<int:pk>/', views.miembro_delete, name='miembro_delete'),
    
    # Préstamos
    path('prestamos/', views.prestamo_list, name='prestamo_list'),
    path('prestamos/nuevo/', views.prestamo_create, name='prestamo_create'),
    path('prestamos/devolver/<int:pk>/', views.prestamo_return, name='prestamo_return'),
    path('prestamos/pagar/<int:pk>/', views.prestamo_pay, name='prestamo_pay'),
]
