from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.messages.views import SuccessMessageMixin
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import ListView, CreateView, UpdateView, DeleteView, TemplateView
from django.db.models import Count, Q, F
from django.contrib.auth.models import User
from datetime import date

from .models import Libro, Miembro, Prestamo
from .forms import LibroForm, MiembroForm, PrestamoForm, RegistroForm
from .services import crear_prestamo, devolver_prestamo, pagar_prestamo

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
    
    # NOTA: Se eliminó el bucle que actualizaba el estado en cada request para optimizar rendimiento.
    # El estado real se computa en el frontend mediante properties.
    
    # Últimos préstamos registrados (optimizado con select_related)
    ultimos_prestamos = Prestamo.objects.select_related('libro', 'miembro').order_by('-fecha_salida')[:5]
    
    # Libros con stock crítico (agotados o con 1 disponible) sin bucle Python (optimizado)
    libros_criticos = Libro.objects.annotate(
        prestados=Count('prestamo', filter=Q(prestamo__fecha_dev_real__isnull=True))
    ).filter(
        prestados__gte=F('cantidad_total') - 1
    ).order_by('titulo')[:5]
    
    context = {
        'total_libros': total_libros,
        'total_miembros': total_miembros,
        'total_prestamos_activos': total_prestamos_activos,
        'total_vencidos': total_vencidos,
        'ultimos_prestamos': ultimos_prestamos,
        'libros_criticos': libros_criticos
    }
    return render(request, 'biblioteca/dashboard.html', context)


# ==================== GESTIÓN DE LIBROS ====================
class LibroListView(ListView):
    model = Libro
    template_name = 'biblioteca/libro_list.html'
    context_object_name = 'libros'
    paginate_by = 20

    def get_queryset(self):
        query = self.request.GET.get('q', '').strip()
        if query:
            return Libro.objects.filter(
                Q(titulo__icontains=query) | Q(autor__icontains=query) | Q(isbn__icontains=query)
            ).order_by('titulo')
        return Libro.objects.all().order_by('titulo')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['query'] = self.request.GET.get('q', '')
        return context


class LibroCreateView(SuccessMessageMixin, CreateView):
    model = Libro
    form_class = LibroForm
    template_name = 'biblioteca/libro_form.html'
    success_url = reverse_lazy('libro_list')
    success_message = "Libro '%(titulo)s' registrado correctamente."


class LibroUpdateView(SuccessMessageMixin, UpdateView):
    model = Libro
    form_class = LibroForm
    pk_url_kwarg = 'isbn'
    template_name = 'biblioteca/libro_form.html'
    success_url = reverse_lazy('libro_list')
    success_message = "Libro '%(titulo)s' actualizado correctamente."


class LibroDeleteView(SuccessMessageMixin, DeleteView):
    model = Libro
    pk_url_kwarg = 'isbn'
    success_url = reverse_lazy('libro_list')
    success_message = "Libro eliminado correctamente."

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Validación de negocio
        if self.object.ejemplares_prestados > 0:
            messages.error(request, f"No se puede eliminar el libro porque hay {self.object.ejemplares_prestados} copias prestadas.")
            return redirect('libro_list')
        return super().post(request, *args, **kwargs)


# ==================== GESTIÓN DE MIEMBROS ====================
class MiembroListView(ListView):
    model = Miembro
    template_name = 'biblioteca/miembro_list.html'
    context_object_name = 'miembros'
    paginate_by = 20
    queryset = Miembro.objects.all().order_by('nombre_completo')


class MiembroCreateView(SuccessMessageMixin, CreateView):
    model = Miembro
    form_class = MiembroForm
    template_name = 'biblioteca/miembro_form.html'
    success_url = reverse_lazy('miembro_list')
    success_message = "Miembro '%(nombre_completo)s' registrado correctamente."


class MiembroUpdateView(SuccessMessageMixin, UpdateView):
    model = Miembro
    form_class = MiembroForm
    template_name = 'biblioteca/miembro_form.html'
    success_url = reverse_lazy('miembro_list')
    success_message = "Miembro '%(nombre_completo)s' actualizado."


class MiembroDeleteView(SuccessMessageMixin, DeleteView):
    model = Miembro
    success_url = reverse_lazy('miembro_list')
    success_message = "Miembro eliminado correctamente."

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Verificar préstamos activos pendientes
        if Prestamo.objects.filter(miembro=self.object, fecha_dev_real__isnull=True).exists():
            messages.error(request, "No se puede eliminar el miembro porque posee préstamos activos sin devolver.")
            return redirect('miembro_list')
        return super().post(request, *args, **kwargs)


# ==================== GESTIÓN DE PRÉSTAMOS ====================
class PrestamoListView(ListView):
    model = Prestamo
    template_name = 'biblioteca/prestamo_list.html'
    context_object_name = 'prestamos'
    paginate_by = 20

    def get_queryset(self):
        # Evitar problema N+1 con select_related
        queryset = Prestamo.objects.select_related('libro', 'miembro')
        
        estado = self.request.GET.get('estado')
        miembro_id = self.request.GET.get('miembro')
        desde = self.request.GET.get('desde')
        hasta = self.request.GET.get('hasta')
        
        if estado:
            queryset = queryset.filter(estado_transaccion=estado)
        if miembro_id:
            queryset = queryset.filter(miembro_id=miembro_id)
        if desde:
            queryset = queryset.filter(fecha_salida__gte=desde)
        if hasta:
            queryset = queryset.filter(fecha_salida__lte=hasta)
            
        return queryset.order_by('-fecha_salida')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['miembros'] = Miembro.objects.all().order_by('nombre_completo')
        
        # Filtros aplicados para mantener selección en formulario
        context['estado_filter'] = self.request.GET.get('estado', '')
        context['miembro_filter'] = self.request.GET.get('miembro', '')
        context['desde_filter'] = self.request.GET.get('desde', '')
        context['hasta_filter'] = self.request.GET.get('hasta', '')
        return context


class PrestamoCreateView(SuccessMessageMixin, CreateView):
    model = Prestamo
    form_class = PrestamoForm
    template_name = 'biblioteca/prestamo_form.html'
    success_url = reverse_lazy('prestamo_list')

    def form_valid(self, form):
        miembro = form.cleaned_data['miembro']
        libro = form.cleaned_data['libro']
        dias_prestamo = int(form.cleaned_data['dias_prestamo'])
        
        try:
            self.object = crear_prestamo(miembro, libro, dias_prestamo)
            messages.success(
                self.request, 
                f"Préstamo del libro '{libro.titulo}' registrado con éxito. Vence el {self.object.fecha_vence|date:'d/m/Y' if hasattr(self.object.fecha_vence, 'strftime') else self.object.fecha_vence}."
            )
            return redirect(self.get_success_url())
        except ValueError as e:
            form.add_error(None, str(e))
            return self.form_invalid(form)


class PrestamoReturnView(View):
    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        try:
            devolver_prestamo(prestamo)
            messages.success(
                request, 
                f"Devolución registrada correctamente. Costo total calculado: ${prestamo.costo_calculado:.2f}."
            )
        except ValueError as e:
            messages.warning(request, str(e))
        return redirect('prestamo_list')


class PrestamoPayView(View):
    def post(self, request, pk):
        prestamo = get_object_or_404(Prestamo, pk=pk)
        pagar_prestamo(prestamo)
        messages.success(request, f"Pago del préstamo #{prestamo.prestamo_id} registrado con éxito.")
        return redirect('prestamo_list')


# ==================== BÚSQUEDA GLOBAL ====================
class BusquedaGlobalView(TemplateView):
    template_name = 'biblioteca/busqueda_global.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        query = self.request.GET.get('q', '').strip()
        context['query'] = query
        
        if query:
            context['libros'] = Libro.objects.filter(
                Q(isbn__icontains=query) | Q(titulo__icontains=query) | Q(autor__icontains=query)
            ).order_by('titulo')[:10]
            
            context['miembros'] = Miembro.objects.filter(
                Q(nombre_completo__icontains=query) | Q(email__icontains=query) | Q(telefono__icontains=query)
            ).order_by('nombre_completo')[:10]
            
            context['prestamos'] = Prestamo.objects.select_related('libro', 'miembro').filter(
                Q(libro__titulo__icontains=query) | Q(miembro__nombre_completo__icontains=query)
            ).order_by('-fecha_salida')[:10]
        else:
            context['libros'] = []
            context['miembros'] = []
            context['prestamos'] = []
            
        return context


# ==================== REGISTRO DE USUARIOS ====================
class RegistroView(CreateView):
    model = User
    form_class = RegistroForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('login')
