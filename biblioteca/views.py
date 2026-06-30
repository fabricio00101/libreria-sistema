from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.db.models import Count, Q
from .models import Libro, Miembro, Prestamo
from datetime import date, timedelta

# ==================== DASHBOARD ====================
def dashboard(request):
    total_libros = Libro.objects.count()
    total_miembros = Miembro.objects.count()
    
    # Préstamos activos (no devueltos)
    prestamos_activos = Prestamo.objects.filter(fecha_dev_real__isnull=True)
    total_prestamos_activos = prestamos_activos.count()
    
    # Préstamos vencidos
    total_vencidos = Prestamo.objects.filter(
        fecha_dev_real__isnull=True, 
        fecha_vence__lt=date.today()
    ).count()
    
    # Actualizar estado de préstamos activos al vuelo para mostrar alertas actualizadas
    for p in prestamos_activos:
        p.calcular_costo_y_actualizar_estado()
        p.save()
        
    # Últimos préstamos realizados
    ultimos_prestamos = Prestamo.objects.order_by('-fecha_salida')[:5]
    
    # Libros con stock crítico (agotados o 1 disponible)
    libros_criticos = []
    for libro in Libro.objects.all():
        if libro.ejemplares_disponibles <= 1:
            libros_criticos.append(libro)
            
    context = {
        'total_libros': total_libros,
        'total_miembros': total_miembros,
        'total_prestamos_activos': total_prestamos_activos,
        'total_vencidos': total_vencidos,
        'ultimos_prestamos': ultimos_prestamos,
        'libros_criticos': libros_criticos[:5]
    }
    return render(request, 'biblioteca/dashboard.html', context)


# ==================== GESTIÓN DE LIBROS ====================
def libro_list(request):
    query = request.GET.get('q', '')
    if query:
        libros = Libro.objects.filter(
            Q(titulo__icontains=query) | Q(autor__icontains=query)
        )
    else:
        libros = Libro.objects.all()
    return render(request, 'biblioteca/libro_list.html', {'libros': libros, 'query': query})

def libro_create(request):
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        titulo = request.POST.get('titulo')
        autor = request.POST.get('autor')
        cantidad_total = request.POST.get('cantidad_total')
        tarifa_diaria = request.POST.get('tarifa_diaria')
        
        if Libro.objects.filter(isbn=isbn).exists():
            messages.error(request, "Ya existe un libro registrado con este ISBN.")
            return render(request, 'biblioteca/libro_form.html', request.POST)
            
        Libro.objects.create(
            isbn=isbn,
            titulo=titulo,
            autor=autor,
            cantidad_total=int(cantidad_total),
            tarifa_diaria=float(tarifa_diaria)
        )
        messages.success(request, f"Libro '{titulo}' registrado correctamente.")
        return redirect('libro_list')
        
    return render(request, 'biblioteca/libro_form.html')

def libro_update(request, isbn):
    libro = get_object_or_404(Libro, isbn=isbn)
    if request.method == 'POST':
        libro.titulo = request.POST.get('titulo')
        libro.autor = request.POST.get('autor')
        libro.cantidad_total = int(request.POST.get('cantidad_total'))
        libro.tarifa_diaria = float(request.POST.get('tarifa_diaria'))
        libro.save()
        messages.success(request, f"Libro '{libro.titulo}' actualizado correctamente.")
        return redirect('libro_list')
        
    return render(request, 'biblioteca/libro_form.html', {'libro': libro})

def libro_delete(request, isbn):
    libro = get_object_or_404(Libro, isbn=isbn)
    if libro.ejemplares_prestados > 0:
        messages.error(request, f"No se puede eliminar el libro porque hay {libro.ejemplares_prestados} copias prestadas.")
        return redirect('libro_list')
        
    libro.delete()
    messages.success(request, "Libro eliminado correctamente.")
    return redirect('libro_list')


# ==================== GESTIÓN DE MIEMBROS ====================
def miembro_list(request):
    miembros = Miembro.objects.all()
    return render(request, 'biblioteca/miembro_list.html', {'miembros': miembros})

def miembro_create(request):
    if request.method == 'POST':
        nombre_completo = request.POST.get('nombre_completo')
        email = request.POST.get('email')
        telefono = request.POST.get('telefono')
        
        if Miembro.objects.filter(email=email).exists():
            messages.error(request, "Este correo electrónico ya está registrado.")
            return render(request, 'biblioteca/miembro_form.html', request.POST)
            
        Miembro.objects.create(
            nombre_completo=nombre_completo,
            email=email,
            telefono=telefono
        )
        messages.success(request, f"Miembro '{nombre_completo}' registrado correctamente.")
        return redirect('miembro_list')
        
    return render(request, 'biblioteca/miembro_form.html')

def miembro_update(request, pk):
    miembro = get_object_or_404(Miembro, pk=pk)
    if request.method == 'POST':
        miembro.nombre_completo = request.POST.get('nombre_completo')
        miembro.email = request.POST.get('email')
        miembro.telefono = request.POST.get('telefono')
        miembro.save()
        messages.success(request, f"Miembro '{miembro.nombre_completo}' actualizado.")
        return redirect('miembro_list')
        
    return render(request, 'biblioteca/miembro_form.html', {'miembro': miembro})

def miembro_delete(request, pk):
    miembro = get_object_or_404(Miembro, pk=pk)
    # Verificar préstamos pendientes
    if Prestamo.objects.filter(miembro=miembro, fecha_dev_real__isnull=True).exists():
        messages.error(request, "No se puede eliminar el miembro porque posee préstamos activos sin devolver.")
        return redirect('miembro_list')
        
    miembro.delete()
    messages.success(request, "Miembro eliminado correctamente.")
    return redirect('miembro_list')


# ==================== GESTIÓN DE PRÉSTAMOS ====================
def prestamo_list(request):
    prestamos = Prestamo.objects.all().order_by('-fecha_salida')
    # Actualizar estado de los activos al visualizar
    for p in prestamos:
        if not p.fecha_dev_real:
            p.calcular_costo_y_actualizar_estado()
            p.save()
    return render(request, 'biblioteca/prestamo_list.html', {'prestamos': prestamos})

def prestamo_create(request):
    if request.method == 'POST':
        miembro_id = request.POST.get('miembro')
        isbn = request.POST.get('libro')
        dias_prestamo = int(request.POST.get('dias_prestamo', 7))
        
        miembro = get_object_or_404(Miembro, pk=miembro_id)
        libro = get_object_or_404(Libro, isbn=isbn)
        
        # Validación crítica de disponibilidad (stock físico)
        if libro.ejemplares_disponibles <= 0:
            messages.error(request, f"No hay ejemplares disponibles de '{libro.titulo}'.")
            return redirect('prestamo_list')
            
        fecha_vence = date.today() + timedelta(days=dias_prestamo)
        
        prestamo = Prestamo.objects.create(
            miembro=miembro,
            libro=libro,
            fecha_vence=fecha_vence,
            estado_transaccion='Pendiente'
        )
        # Calcular el costo base inicial
        prestamo.calcular_costo_y_actualizar_estado()
        prestamo.save()
        
        messages.success(request, f"Préstamo del libro '{libro.titulo}' registrado con éxito. Vence el {fecha_vence}.")
        return redirect('prestamo_list')
        
    libros = [l for l in Libro.objects.all() if l.ejemplares_disponibles > 0]
    miembros = Miembro.objects.all()
    return render(request, 'biblioteca/prestamo_form.html', {
        'libros': libros,
        'miembros': miembros
    })

def prestamo_return(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    if prestamo.fecha_dev_real:
        messages.warning(request, "Este préstamo ya fue devuelto.")
        return redirect('prestamo_list')
        
    # Registrar devolución hoy
    prestamo.fecha_dev_real = date.today()
    prestamo.calcular_costo_y_actualizar_estado()
    
    # Si no tiene costo asociado (gratis o devuelto de inmediato), marcar como pagado, si no, pendiente de cobro
    if prestamo.costo_calculado <= 0:
        prestamo.estado_transaccion = 'Pagado'
        
    prestamo.save()
    messages.success(
        request, 
        f"Devolución registrada correctamente. Costo total calculado: ${prestamo.costo_calculado:.2f}."
    )
    return redirect('prestamo_list')

def prestamo_pay(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk)
    prestamo.estado_transaccion = 'Pagado'
    prestamo.save()
    messages.success(request, f"Pago del préstamo #{prestamo.prestamo_id} registrado con éxito.")
    return redirect('prestamo_list')
