from django.db import models
from datetime import date

class Libro(models.Model):
    isbn = models.CharField(max_length=13, primary_key=True, verbose_name="ISBN")
    titulo = models.CharField(max_length=255, verbose_name="Título")
    autor = models.CharField(max_length=255, verbose_name="Autor")
    cantidad_total = models.PositiveIntegerField(default=1, verbose_name="Cantidad Total")
    tarifa_diaria = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Tarifa Diaria")

    def __str__(self):
        return f"{self.titulo} ({self.autor})"

    @property
    def ejemplares_prestados(self):
        # Cuenta los préstamos de este libro que no han sido devueltos aún
        return self.prestamo_set.filter(fecha_dev_real__isnull=True).count()

    @property
    def ejemplares_disponibles(self):
        disponibles = self.cantidad_total - self.ejemplares_prestados
        return max(0, disponibles)


class Miembro(models.Model):
    miembro_id = models.AutoField(primary_key=True, verbose_name="ID Miembro")
    nombre_completo = models.CharField(max_length=255, verbose_name="Nombre Completo")
    email = models.EmailField(unique=True, verbose_name="Email")
    telefono = models.CharField(max_length=20, blank=True, verbose_name="Teléfono")

    def __str__(self):
        return self.nombre_completo


class Prestamo(models.Model):
    ESTADOS = [
        ('Pendiente', 'Pendiente'),
        ('Pagado', 'Pagado'),
        ('Vencido', 'Vencido'),
    ]

    prestamo_id = models.AutoField(primary_key=True, verbose_name="ID Préstamo")
    miembro = models.ForeignKey(Miembro, on_delete=models.CASCADE, verbose_name="Miembro")
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE, verbose_name="Libro")
    fecha_salida = models.DateField(auto_now_add=True, verbose_name="Fecha de Salida")
    fecha_vence = models.DateField(verbose_name="Fecha de Vencimiento")
    fecha_dev_real = models.DateField(null=True, blank=True, verbose_name="Fecha de Devolución Real")
    costo_calculado = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name="Costo Calculado")
    estado_transaccion = models.CharField(max_length=20, choices=ESTADOS, default='Pendiente', verbose_name="Estado de Transacción")

    def __str__(self):
        return f"Préstamo {self.prestamo_id}: {self.libro} a {self.miembro}"

    @property
    def dias_mora(self):
        if not self.fecha_vence:
            return 0
        
        # Si ya se devolvió, comparar con la fecha de devolución real
        limite_comparacion = self.fecha_dev_real if self.fecha_dev_real else date.today()
        
        if limite_comparacion > self.fecha_vence:
            return (limite_comparacion - self.fecha_vence).days
        return 0

    def calcular_costo_y_actualizar_estado(self, multa_diaria=50.00):
        """
        Calcula el costo del préstamo.
        Costo base = días previstos * tarifa diaria del libro.
        Mora = días de retraso * multa diaria.
        """
        # Calcular días previstos del préstamo
        dias_previstos = (self.fecha_vence - self.fecha_salida).days
        if dias_previstos < 0:
            dias_previstos = 0
            
        costo_base = dias_previstos * float(self.libro.tarifa_diaria)
        
        # Calcular mora
        mora = self.dias_mora * float(multa_diaria)
        
        self.costo_calculado = costo_base + mora
        
        # Actualizar estado si ya está devuelto y tenía mora/pendiente
        if self.fecha_dev_real:
            if self.costo_calculado > 0 and self.estado_transaccion != 'Pagado':
                if self.dias_mora > 0:
                    self.estado_transaccion = 'Vencido'
                else:
                    self.estado_transaccion = 'Pendiente'
        else:
            # Aún no devuelto
            if date.today() > self.fecha_vence:
                self.estado_transaccion = 'Vencido'
            else:
                self.estado_transaccion = 'Pendiente'
