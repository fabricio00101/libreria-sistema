from django import forms
from django.db.models import Count, F, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Libro, Miembro, Prestamo

class BaseTailwindForm(forms.ModelForm):
    """
    Formulario base que inyecta automáticamente clases de estilo de Tailwind CSS
    a todos los campos.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            tailwind_classes = "w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary"
            
            # Evitar duplicar clases si ya existen
            if tailwind_classes not in existing_classes:
                if existing_classes:
                    field.widget.attrs['class'] = f"{existing_classes} {tailwind_classes}"
                else:
                    field.widget.attrs['class'] = tailwind_classes


class LibroForm(BaseTailwindForm):
    class Meta:
        model = Libro
        fields = ['isbn', 'titulo', 'autor', 'cantidad_total', 'tarifa_diaria']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Si se está editando un libro existente, el ISBN es de solo lectura y deshabilitado
        if self.instance and self.instance.pk:
            self.fields['isbn'].disabled = True
            self.fields['isbn'].required = False
            self.fields['isbn'].widget.attrs['class'] += " bg-gray-150 cursor-not-allowed"

    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn')
        # Si estamos creando un libro nuevo, validar que el ISBN no exista y tenga 13 caracteres
        if not self.instance.pk:
            if Libro.objects.filter(isbn=isbn).exists():
                raise forms.ValidationError("Ya existe un libro registrado con este ISBN.")
            if not isbn or len(isbn) != 13:
                raise forms.ValidationError("El ISBN debe tener exactamente 13 caracteres.")
        return isbn

    def clean_cantidad_total(self):
        cantidad_total = self.cleaned_data.get('cantidad_total')
        if cantidad_total is None or cantidad_total < 1:
            raise forms.ValidationError("La cantidad total de ejemplares debe ser al menos 1.")
        return cantidad_total

    def clean_tarifa_diaria(self):
        tarifa_diaria = self.cleaned_data.get('tarifa_diaria')
        if tarifa_diaria is None or tarifa_diaria < 0:
            raise forms.ValidationError("La tarifa diaria no puede ser negativa.")
        return tarifa_diaria


class MiembroForm(BaseTailwindForm):
    class Meta:
        model = Miembro
        fields = ['nombre_completo', 'email', 'telefono']


class PrestamoForm(BaseTailwindForm):
    dias_prestamo = forms.ChoiceField(
        choices=[
            (3, '3 días (Corto plazo)'),
            (7, '7 días (Estándar)'),
            (14, '14 días (Largo plazo)'),
            (30, '30 días (Mes completo)')
        ],
        initial=7,
        label="Período del Préstamo",
        widget=forms.Select(attrs={'class': 'w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary'})
    )

    class Meta:
        model = Prestamo
        fields = ['miembro', 'libro']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Filtrar el select de libros para mostrar solo los que tienen stock disponible
        # Usando subquery para contar prestados
        self.fields['libro'].queryset = Libro.objects.annotate(
            prestados=Count('prestamo', filter=Q(prestamo__fecha_dev_real__isnull=True))
        ).filter(prestados__lt=F('cantidad_total'))

    def clean_libro(self):
        libro = self.cleaned_data.get('libro')
        if libro and libro.ejemplares_disponibles <= 0:
            raise forms.ValidationError("No hay ejemplares disponibles de este libro.")
        return libro


class RegistroForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tailwind_classes = "w-full px-4 py-2 border border-gray-200 rounded-lg text-sm focus:ring-2 focus:ring-primary focus:border-primary"
        for field in self.fields.values():
            field.widget.attrs['class'] = tailwind_classes
