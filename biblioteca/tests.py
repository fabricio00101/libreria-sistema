from django.test import TestCase
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from .models import Libro, Miembro, Prestamo

class BibliotecaLógicaTestCase(TestCase):
    def setUp(self):
        # Crear datos de prueba
        self.libro = Libro.objects.create(
            isbn="1234567890123",
            titulo="Libro de Prueba",
            autor="Autor de Prueba",
            cantidad_total=2,
            tarifa_diaria=Decimal("10.00")
        )
        self.miembro = Miembro.objects.create(
            nombre_completo="Juan Pérez",
            email="juan@perez.com"
        )

    def test_ejemplares_disponibles(self):
        # Inicialmente 2 disponibles
        self.assertEqual(self.libro.ejemplares_disponibles, 2)
        
        # Crear un préstamo activo (sin devolver)
        prestamo = Prestamo.objects.create(
            miembro=self.miembro,
            libro=self.libro,
            fecha_vence=date.today() + timedelta(days=5),
            estado_transaccion='Pendiente'
        )
        
        # Debe haber 1 disponible
        self.assertEqual(self.libro.ejemplares_disponibles, 1)
        self.assertEqual(self.libro.ejemplares_prestados, 1)
        
        # Devolver el libro
        prestamo.fecha_dev_real = date.today()
        prestamo.save()
        
        # Vuelve a haber 2 disponibles
        self.assertEqual(self.libro.ejemplares_disponibles, 2)

    def test_calculo_costo_y_mora(self):
        # 1. Préstamo a tiempo
        # Salida: hace 5 días, Vence: hoy.
        # Días previstos = 5. Tarifa = $10.00. Costo = $50.00. Mora = 0.
        prestamo = Prestamo.objects.create(
            miembro=self.miembro,
            libro=self.libro,
            fecha_vence=date.today(),
            estado_transaccion='Pendiente'
        )
        # Forzar manualmente la fecha de salida al pasado
        prestamo.fecha_salida = date.today() - timedelta(days=5)
        prestamo.save()
        
        prestamo.calcular_costo_y_actualizar_estado(multa_diaria=50.00)
        self.assertEqual(prestamo.dias_mora, 0)
        self.assertEqual(prestamo.costo_calculado, Decimal("50.00"))
        
        # 2. Préstamo con mora
        # Salida: hace 8 días, Vence: hace 3 días.
        # Días previstos = 5. Tarifa = $10.00. Costo base = $50.00.
        # Mora = 3 días retraso * $50.00 multa = $150.00. Costo Total = $200.00.
        prestamo_mora = Prestamo.objects.create(
            miembro=self.miembro,
            libro=self.libro,
            fecha_vence=date.today() - timedelta(days=3),
            estado_transaccion='Pendiente'
        )
        prestamo_mora.fecha_salida = date.today() - timedelta(days=8)
        prestamo_mora.save()
        
        prestamo_mora.calcular_costo_y_actualizar_estado(multa_diaria=50.00)
        self.assertEqual(prestamo_mora.dias_mora, 3)
        self.assertEqual(prestamo_mora.costo_calculado, Decimal("200.00"))
        self.assertEqual(prestamo_mora.estado_transaccion, 'Vencido')
