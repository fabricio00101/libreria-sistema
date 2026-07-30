from django.test import TestCase
from django.utils import timezone
from django.contrib.auth.models import User
from django.urls import reverse
from datetime import date, timedelta
from decimal import Decimal
from .models import Libro, Miembro, Prestamo
from .services import crear_prestamo, devolver_prestamo, pagar_prestamo

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
        prestamo = crear_prestamo(self.miembro, self.libro, 5)
        
        # Debe haber 1 disponible
        self.assertEqual(self.libro.ejemplares_disponibles, 1)
        self.assertEqual(self.libro.ejemplares_prestados, 1)
        
        # Devolver el libro
        devolver_prestamo(prestamo)
        
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

    def test_prestamo_vencido_sin_devolucion(self):
        # Vence hace 2 días, devuelto real es None
        prestamo = Prestamo.objects.create(
            miembro=self.miembro,
            libro=self.libro,
            fecha_vence=date.today() - timedelta(days=2),
            estado_transaccion='Pendiente'
        )
        self.assertTrue(prestamo.esta_vencido)
        self.assertEqual(prestamo.dias_mora, 2)
        self.assertEqual(prestamo.estado_display, 'Vencido')

    def test_prestamo_devuelto_a_tiempo(self):
        # Vence hoy, devuelto hoy (a tiempo)
        prestamo = Prestamo.objects.create(
            miembro=self.miembro,
            libro=self.libro,
            fecha_vence=date.today(),
            fecha_dev_real=date.today(),
            estado_transaccion='Pagado' # ya se pagó
        )
        self.assertFalse(prestamo.esta_vencido)
        self.assertEqual(prestamo.dias_mora, 0)
        self.assertEqual(prestamo.estado_display, 'Pagado')

    def test_prestamo_devuelto_tarde(self):
        # Vence hace 5 días, devuelto hoy (5 días de mora)
        prestamo = Prestamo.objects.create(
            miembro=self.miembro,
            libro=self.libro,
            fecha_vence=date.today() - timedelta(days=5),
            fecha_dev_real=date.today(),
            estado_transaccion='Pendiente'
        )
        self.assertTrue(prestamo.esta_vencido)
        self.assertEqual(prestamo.dias_mora, 5)
        self.assertEqual(prestamo.estado_display, 'Vencido')

    def test_multiples_prestamos_mismo_libro(self):
        # Libro tiene stock 2
        miembro2 = Miembro.objects.create(
            nombre_completo="María López",
            email="maria@lopez.com"
        )
        # Prestar primera copia
        crear_prestamo(self.miembro, self.libro, 7)
        self.assertEqual(self.libro.ejemplares_disponibles, 1)
        
        # Prestar segunda copia
        crear_prestamo(miembro2, self.libro, 7)
        self.assertEqual(self.libro.ejemplares_disponibles, 0)

    def test_libro_sin_stock_no_puede_prestarse(self):
        # Consumir el stock (2 ejemplares)
        crear_prestamo(self.miembro, self.libro, 7)
        miembro2 = Miembro.objects.create(nombre_completo="M2", email="m2@m2.com")
        crear_prestamo(miembro2, self.libro, 7)
        
        miembro3 = Miembro.objects.create(nombre_completo="M3", email="m3@m3.com")
        
        # Intentar prestar sin stock usando la capa de servicios debe lanzar ValueError
        with self.assertRaises(ValueError):
            crear_prestamo(miembro3, self.libro, 7)

    def test_miembro_con_prestamo_activo_no_se_puede_eliminar(self):
        # Crear préstamo activo
        crear_prestamo(self.miembro, self.libro, 7)
        
        # Al intentar eliminar vía vista o lógica, verificamos que la validación lo impida.
        # Esto lo validamos en los tests de vistas a continuación.


class BibliotecaViewsTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='admin', password='password')
        self.client.login(username='admin', password='password')
        
        self.libro = Libro.objects.create(
            isbn="1234567890123",
            titulo="Libro de Prueba",
            autor="Autor de Prueba",
            cantidad_total=1,
            tarifa_diaria=Decimal("10.00")
        )
        self.miembro = Miembro.objects.create(
            nombre_completo="Juan Pérez",
            email="juan@perez.com"
        )

    def test_libro_create_view_GET(self):
        response = self.client.get(reverse('libro_create'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'biblioteca/libro_form.html')

    def test_libro_create_view_POST_valido(self):
        data = {
            'isbn': '9780142437230',
            'titulo': 'Don Quijote',
            'autor': 'Miguel de Cervantes',
            'cantidad_total': 5,
            'tarifa_diaria': '150.00'
        }
        response = self.client.post(reverse('libro_create'), data)
        self.assertRedirects(response, reverse('libro_list'))
        self.assertTrue(Libro.objects.filter(isbn='9780142437230').exists())

    def test_libro_create_view_POST_isbn_duplicado(self):
        # Intentar crear un libro con el mismo ISBN que self.libro
        data = {
            'isbn': self.libro.isbn,
            'titulo': 'Otro Título',
            'autor': 'Otro Autor',
            'cantidad_total': 3,
            'tarifa_diaria': '50.00'
        }
        response = self.client.post(reverse('libro_create'), data)
        # Debe recargar la página mostrando error
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Libro.objects.filter(titulo='Otro Título').exists())

    def test_libro_delete_view(self):
        # Eliminar libro sin préstamos activos
        response = self.client.post(reverse('libro_delete', kwargs={'isbn': self.libro.isbn}))
        self.assertRedirects(response, reverse('libro_list'))
        self.assertFalse(Libro.objects.filter(isbn=self.libro.isbn).exists())

    def test_libro_delete_view_con_prestamo_activo(self):
        # Crear préstamo activo
        crear_prestamo(self.miembro, self.libro, 7)
        
        # Intentar eliminar debe fallar y redirigir
        response = self.client.post(reverse('libro_delete', kwargs={'isbn': self.libro.isbn}))
        self.assertRedirects(response, reverse('libro_list'))
        self.assertTrue(Libro.objects.filter(isbn=self.libro.isbn).exists())

    def test_miembro_con_prestamo_activo_no_se_puede_eliminar(self):
        # Crear préstamo activo
        crear_prestamo(self.miembro, self.libro, 7)
        
        # Intentar eliminar al miembro debe ser rechazado
        response = self.client.post(reverse('miembro_delete', kwargs={'pk': self.miembro.miembro_id}))
        self.assertRedirects(response, reverse('miembro_list'))
        self.assertTrue(Miembro.objects.filter(pk=self.miembro.miembro_id).exists())

    def test_prestamo_create_view_stock_insuficiente(self):
        # Agotar el stock del libro
        crear_prestamo(self.miembro, self.libro, 7)
        
        # Intentar crear otro préstamo del mismo libro
        miembro2 = Miembro.objects.create(nombre_completo="M2", email="m2@m2.com")
        data = {
            'miembro': miembro2.miembro_id,
            'libro': self.libro.isbn,
            'dias_prestamo': 7
        }
        response = self.client.post(reverse('prestamo_create'), data)
        # El formulario debería ser inválido ya que el queryset de libros no incluye libros sin stock,
        # o lanzar ValidationError en el clean
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Prestamo.objects.filter(miembro=miembro2).count(), 0)

    def test_dashboard_carga_correctamente(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'biblioteca/dashboard.html')

    def test_registro_view_GET(self):
        response = self.client.get(reverse('registro'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'registration/registro.html')

    def test_registro_view_POST_valido(self):
        data = {
            'username': 'nuevousuario',
            'password1': 'ContraSenaSegura123',
            'password2': 'ContraSenaSegura123'
        }
        response = self.client.post(reverse('registro'), data)
        self.assertRedirects(response, reverse('login'))
        self.assertTrue(User.objects.filter(username='nuevousuario').exists())
