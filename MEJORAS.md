# Plan: Quitar login obligatorio + Agregar registro

> Objetivo: El sistema debe abrirse directamente sin login. Debe existir una sección para registrarse.

---

## Estado actual

- `RegistroForm` ya fue agregada en `biblioteca/forms.py`.
- Las vistas en `biblioteca/views.py` aún tienen `LoginRequiredMixin` y `@login_required`.
- Falta la vista de registro, las URLs y los templates.

---

## Tareas pendientes

### 1. `biblioteca/views.py`
- [ ] Quitar `@login_required` de `dashboard` (línea 17).
- [ ] Quitar `LoginRequiredMixin` de todas las CBVs: `LibroListView`, `LibroCreateView`, `LibroUpdateView`, `LibroDeleteView`, `MiembroListView`, `MiembroCreateView`, `MiembroUpdateView`, `MiembroDeleteView`, `PrestamoListView`, `PrestamoCreateView`, `PrestamoReturnView`, `PrestamoPayView`, `BusquedaGlobalView`.
- [ ] Eliminar imports sin usar: `login_required`, `LoginRequiredMixin`.
- [ ] Agregar `RegistroView`:

```python
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.views.generic import CreateView

class RegistroView(CreateView):
    model = User
    form_class = RegistroForm
    template_name = 'registration/registro.html'
    success_url = reverse_lazy('login')
```

### 2. `biblioteca_project/settings.py`
- [ ] Cambiar `LOGOUT_REDIRECT_URL = 'login'` → `LOGOUT_REDIRECT_URL = 'dashboard'`.

### 3. `biblioteca/urls.py`
- [ ] Agregar: `path('registro/', views.RegistroView.as_view(), name='registro')`.

### 4. `biblioteca/templates/registration/login.html`
- [ ] Agregar link al final del formulario:
```html
<p class="text-center text-sm text-gray-500 mt-4">
  ¿No tenés cuenta? <a href="{% url 'registro' %}" class="text-primary hover:underline font-semibold">Registrate</a>
</p>
```

### 5. Nuevo: `biblioteca/templates/registration/registro.html`
- [ ] Crear template basado en `login.html` con campos: username, password1, password2.
- [ ] Link "Ya tengo cuenta" apuntando a `{% url 'login' %}`.

---

## Orden de ejecución

1. Crear template `registro.html`.
2. Agregar `RegistroView` en `views.py` + quitar todos los `LoginRequiredMixin`.
3. Agregar ruta en `urls.py`.
4. Actualizar `settings.py` (`LOGOUT_REDIRECT_URL`).
5. Agregar link de registro en `login.html`.
