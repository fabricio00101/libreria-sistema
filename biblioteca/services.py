from datetime import date, timedelta
from .models import Prestamo, Libro

def crear_prestamo(miembro, libro, dias_prestamo=7):
    """
    Crea un préstamo de un libro para un miembro.
    Verifica que el libro tenga ejemplares disponibles antes de realizar el préstamo.
    """
    if libro.ejemplares_disponibles <= 0:
        raise ValueError("No hay ejemplares disponibles de este libro.")
        
    fecha_vence = date.today() + timedelta(days=dias_prestamo)
    
    prestamo = Prestamo.objects.create(
        miembro=miembro,
        libro=libro,
        fecha_vence=fecha_vence,
        estado_transaccion='Pendiente'
    )
    prestamo.calcular_costo_y_actualizar_estado()
    prestamo.save()
    return prestamo

def devolver_prestamo(prestamo):
    """
    Registra la devolución de un préstamo.
    Calcula el costo final y actualiza el estado según corresponda.
    """
    if prestamo.fecha_dev_real:
        raise ValueError("Este préstamo ya fue devuelto.")
        
    prestamo.fecha_dev_real = date.today()
    prestamo.calcular_costo_y_actualizar_estado()
    
    # Si no tiene costo asociado (gratis o devuelto de inmediato), marcar como pagado,
    # si no, queda pendiente de cobro (o vencido)
    if prestamo.costo_calculado <= 0:
        prestamo.estado_transaccion = 'Pagado'
        
    prestamo.save()
    return prestamo

def pagar_prestamo(prestamo):
    """
    Registra el pago de un préstamo.
    """
    prestamo.estado_transaccion = 'Pagado'
    prestamo.save()
    return prestamo
