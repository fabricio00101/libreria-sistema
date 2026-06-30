import os
import sys
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca_project.settings')
django.setup()

from biblioteca.models import Libro, Miembro, Prestamo
from datetime import date, timedelta

def seed():
    print("Sembrando datos de prueba...")
    
    # Limpiar base de datos
    Prestamo.objects.all().delete()
    Libro.objects.all().delete()
    Miembro.objects.all().delete()
    
    # Crear Libros
    l1 = Libro.objects.create(
        isbn="9780142437230",
        titulo="Don Quijote de la Mancha",
        autor="Miguel de Cervantes",
        cantidad_total=3,
        tarifa_diaria=100.00
    )
    l2 = Libro.objects.create(
        isbn="9788420659329",
        titulo="Ficciones",
        autor="Jorge Luis Borges",
        cantidad_total=1,
        tarifa_diaria=150.00
    )
    l3 = Libro.objects.create(
        isbn="9780307474728",
        titulo="Cien años de soledad",
        autor="Gabriel García Márquez",
        cantidad_total=2,
        tarifa_diaria=120.00
    )
    l4 = Libro.objects.create(
        isbn="9789507318856",
        titulo="Rayuela",
        autor="Julio Cortázar",
        cantidad_total=2,
        tarifa_diaria=130.00
    )
    
    print(f"Creados {Libro.objects.count()} libros.")
    
    # Crear Miembros
    m1 = Miembro.objects.create(
        nombre_completo="Juan Pérez",
        email="juan.perez@example.com",
        telefono="1122334455"
    )
    m2 = Miembro.objects.create(
        nombre_completo="María Rodríguez",
        email="maria.rod@example.com",
        telefono="1166778899"
    )
    m3 = Miembro.objects.create(
        nombre_completo="Carlos Tévez",
        email="carlitos@example.com",
        telefono="1155443322"
    )
    
    print(f"Creados {Miembro.objects.count()} miembros.")
    
    # Crear algunos préstamos
    # 1. Préstamo activo (dentro del plazo)
    p1 = Prestamo.objects.create(
        miembro=m1,
        libro=l1,
        fecha_vence=date.today() + timedelta(days=5),
        estado_transaccion='Pendiente'
    )
    p1.calcular_costo_y_actualizar_estado()
    p1.save()
    
    # 2. Préstamo activo vencido (sin devolver, fecha_vence en el pasado)
    # Nota: Usamos una fecha manual para simular retraso.
    p2 = Prestamo.objects.create(
        miembro=m2,
        libro=l2, # l2 solo tiene cantidad_total=1, por lo que ahora está agotado
        fecha_vence=date.today() - timedelta(days=3),
        estado_transaccion='Pendiente'
    )
    p2.calcular_costo_y_actualizar_estado()
    p2.save()
    
    # 3. Préstamo devuelto a tiempo
    p3 = Prestamo.objects.create(
        miembro=m3,
        libro=l3,
        fecha_vence=date.today() - timedelta(days=2),
        fecha_dev_real=date.today() - timedelta(days=2),
        estado_transaccion='Pagado'
    )
    p3.calcular_costo_y_actualizar_estado()
    p3.save()
    
    print("Datos sembrados con éxito!")

if __name__ == '__main__':
    seed()
