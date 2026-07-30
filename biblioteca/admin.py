from django.contrib import admin
from .models import Libro, Miembro, Prestamo

@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ('isbn', 'titulo', 'autor', 'cantidad_total', 'tarifa_diaria')
    search_fields = ('titulo', 'autor', 'isbn')

@admin.register(Miembro)
class MiembroAdmin(admin.ModelAdmin):
    list_display = ('miembro_id', 'nombre_completo', 'email', 'telefono')
    search_fields = ('nombre_completo', 'email')

@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = ('prestamo_id', 'libro', 'miembro', 'fecha_salida', 'fecha_vence', 'fecha_dev_real', 'estado_transaccion')
    list_filter = ('estado_transaccion',)
    search_fields = ('libro__titulo', 'miembro__nombre_completo')
