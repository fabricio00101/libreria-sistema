# BiblioTech - Sistema de Gestión de Biblioteca

Sistema web para la gestión integral de una biblioteca. Permite administrar el catálogo de libros, el registro de miembros y el seguimiento de préstamos con cálculo automático de costos y mora.

---

## Tabla de contenidos

- [Características principales](#características-principales)
- [Stack tecnológico](#stack-tecnológico)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Modelos de datos](#modelos-de-datos)
- [Instalación y ejecución](#instalación-y-ejecución)
- [Uso de la aplicación](#uso-de-la-aplicación)
- [Lógica de negocio](#lógica-de-negocio)
- [Diseño de la interfaz](#diseño-de-la-interfaz)

---

## Características principales

- **Dashboard** con métricas en tiempo real: total de libros, miembros activos, préstamos en curso y vencidos.
- **Gestión de libros**: alta, baja, edición y búsqueda por título, autor o ISBN.
- **Gestión de miembros**: registro con validación de email único, edición y baja.
- **Sistema de préstamos**: creación con selección de período (3, 7, 14 o 30 días), devolución y registro de pagos.
- **Cálculo automático de costos**: tarifa base por días + multa por mora ($50/día de retraso).
- **Detección de vencimiento**: los préstamos se marcan automáticamente como vencidos cuando superan la fecha de vencimiento.
- **Búsqueda global**: buscador unificado que consulta libros, miembros y préstamos.
- **Stock en alerta**: el dashboard muestra libros con stock crítico (agotados o con 1 ejemplar disponible).
- **Control de integridad**: no se puede eliminar un libro con préstamos activos, ni un miembro con préstamos pendientes.
- **Autenticación**: login, logout y registro de usuarios con Django Auth.
- **Interfaz responsiva**: diseño adaptivo con Tailwind CSS y sidebar colapsable en móvil.

---

## Stack tecnológico

| Componente      | Tecnología                  |
|-----------------|-----------------------------|
| Backend         | Django 6.0 (Python)         |
| Base de datos   | SQLite3 (desarrollo)        |
| Frontend        | Tailwind CSS (CDN)          |
| Componentes     | Flowbite 2.5                |
| Iconografía     | Google Material Symbols     |
| Fuentes         | Inter (Google Fonts)        |

---

## Estructura del proyecto

```
libreria-sistema/
├── manage.py                     # CLI de Django
├── requirements.txt              # Dependencias (Django>=6.0,<6.1)
├── db.sqlite3                    # Base de datos SQLite
├── seed_data.py                  # Script de datos de prueba
├── import_sql.py                 # Script de importación SQL
│
├── biblioteca_project/           # Configuración del proyecto
│   ├── settings.py               # Ajustes generales
│   ├── urls.py                   # URLs raíz
│   ├── wsgi.py                   # Punto de entrada WSGI
│   └── asgi.py                   # Punto de entrada ASGI
│
└── biblioteca/                   # Aplicación principal
    ├── models.py                 # Modelos: Libro, Miembro, Prestamo
    ├── views.py                  # Vistas (Class-Based y Function-Based)
    ├── forms.py                  # Formularios con clases Tailwind automáticas
    ├── urls.py                   # Rutas de la aplicación
    ├── services.py               # Lógica de negocio (crear, devolver, pagar)
    ├── admin.py                  # Registro en admin de Django
    ├── apps.py                   # Configuración de la app
    ├── tests.py                  # Tests
    ├── migrations/               # Migraciones de BD
    ├── static/biblioteca/        # Archivos estáticos (CSS)
    └── templates/
        ├── biblioteca/           # Templates de la app
        │   ├── base.html         # Layout base con sidebar y header
        │   ├── dashboard.html    # Panel principal con métricas
        │   ├── libro_list.html   # Listado de libros
        │   ├── libro_form.html   # Formulario de libro
        │   ├── miembro_list.html # Listado de miembros
        │   ├── miembro_form.html # Formulario de miembro
        │   ├── prestamo_list.html# Listado de préstamos con filtros
        │   ├── prestamo_form.html# Formulario de nuevo préstamo
        │   └── busqueda_global.html # Búsqueda unificada
        └── registration/
            ├── login.html        # Inicio de sesión
            └── registro.html     # Registro de usuario
```

---

## Modelos de datos

### Libro

| Campo            | Tipo              | Descripción                        |
|------------------|-------------------|------------------------------------|
| `isbn`           | CharField (PK)    | ISBN de 13 caracteres, clave primaria |
| `titulo`         | CharField(255)    | Título del libro                   |
| `autor`          | CharField(255)    | Nombre del autor                   |
| `cantidad_total` | PositiveIntegerField | Número total de ejemplares       |
| `tarifa_diaria`  | DecimalField(10,2)| Costo diario de préstamo           |

**Propiedades calculadas:**
- `ejemplares_prestados`: cantidad de copias actualmente prestadas.
- `ejemplares_disponibles`: `cantidad_total - ejemplares_prestados`.

### Miembro

| Campo             | Tipo              | Descripción               |
|-------------------|-------------------|---------------------------|
| `miembro_id`      | AutoField (PK)    | Identificador único       |
| `nombre_completo` | CharField(255)    | Nombre completo           |
| `email`           | EmailField (único)| Correo electrónico único  |
| `telefono`        | CharField(20)     | Teléfono (opcional)       |

### Prestamo

| Campo                  | Tipo               | Descripción                          |
|------------------------|--------------------|--------------------------------------|
| `prestamo_id`          | AutoField (PK)     | Identificador único                  |
| `miembro`              | FK → Miembro       | Miembro que realiza el préstamo      |
| `libro`                | FK → Libro         | Libro prestado                       |
| `fecha_salida`         | DateField (auto)   | Fecha de creación del préstamo       |
| `fecha_vence`          | DateField          | Fecha límite de devolución           |
| `fecha_dev_real`       | DateField (null)   | Fecha real de devolución             |
| `costo_calculado`      | DecimalField(10,2) | Costo total calculado                |
| `estado_transaccion`   | CharField          | `Pendiente`, `Pagado` o `Vencido`   |

**Propiedades calculadas:**
- `dias_mora`: días de retraso (0 si no hay).
- `esta_vencido`: `True` si la fecha actual supera la de vencimiento y no fue devuelto a tiempo.
- `esta_activo`: `True` si no ha sido devuelto.
- `estado_display`: estado visual considerando devolución, mora y pago.

---

## Instalación y ejecución

### Requisitos

- Python 3.10+
- pip

### Pasos

```bash
# 1. Clonar el repositorio
git clone <url-del-repositorio>
cd libreria-sistema

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Aplicar migraciones
python manage.py migrate

# 6. (Opcional) Cargar datos de prueba
python seed_data.py

# 7. Crear superusuario (para acceder al admin)
python manage.py createsuperuser

# 8. Ejecutar el servidor
python manage.py runserver
```

La aplicación estará disponible en `http://127.0.0.1:8000/`.

---

## Uso de la aplicación

### Navegación

| Ruta                          | Descripción                        |
|-------------------------------|------------------------------------|
| `/`                           | Dashboard principal                |
| `/libros/`                    | Listado y búsqueda de libros       |
| `/libros/nuevo/`              | Agregar un libro                   |
| `/libros/editar/<isbn>/`      | Editar un libro                    |
| `/miembros/`                  | Listado de miembros                |
| `/miembros/nuevo/`            | Registrar un miembro               |
| `/prestamos/`                 | Listado con filtros de préstamos   |
| `/prestamos/nuevo/`           | Crear un nuevo préstamo            |
| `/prestamos/devolver/<id>/`   | Registrar devolución               |
| `/prestamos/pagar/<id>/`      | Registrar pago                     |
| `/buscar/`                    | Búsqueda global                    |
| `/login/`                     | Inicio de sesión                   |
| `/registro/`                  | Crear cuenta de usuario            |

### Flujo típico

1. Registrar libros en el catálogo con su tarifa diaria.
2. Registrar miembros de la biblioteca.
3. Crear un préstamo seleccionando miembro, libro y período.
4. Al vencimiento, registrar la devolución (calcula costo automáticamente).
5. Registrar el pago del préstamo.

---

## Lógica de negocio

### Cálculo de costos

```
Costo base = días del período × tarifa diaria del libro
Mora = días de retraso × $50.00
Costo total = Costo base + Mora
```

### Estados de préstamo

| Estado       | Condición                                              |
|--------------|--------------------------------------------------------|
| `Pendiente`  | Préstamo activo dentro del plazo, sin pagar            |
| `Vencido`    | Superó la fecha de vencimiento sin devolución o con mora |
| `Pagado`     | Devuelto y pago registrado, o devuelto sin costo       |
| `Devuelto`   | Devuelto a tiempo sin pendiente de pago                |

### Validaciones

- ISBN debe tener exactamente 13 caracteres y ser único.
- No se puede crear un préstamo si no hay ejemplares disponibles.
- No se puede eliminar un libro que tenga préstamos activos.
- No se puede eliminar un miembro que tenga préstamos sin devolver.
- La tarifa diaria no puede ser negativa.
- La cantidad total de ejemplares debe ser al menos 1.

---

## Diseño de la interfaz

- **Framework CSS**: Tailwind CSS vía CDN con configuración personalizada de colores (`primary: #004cc7`).
- **Componentes**: Flowbite para elementos interactivos (drawers, alerts).
- **Iconografía**: Google Material Symbols Outlined.
- **Tipografía**: Inter (Google Fonts).
- **Layout**: Sidebar fijo en desktop, colapsable en móvil con botón hamburguesa.
- **Formularios**: clase base `BaseTailwindForm` que aplica estilos automáticamente a todos los campos.
- **Mensajes**: notificaciones de éxito, advertencia y error con colores semánticos.
- **Responsividad**: grid adaptivo con `sm:`, `md:` y `lg:` breakpoints.
