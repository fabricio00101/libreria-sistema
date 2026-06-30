import os
import re
import django

# Configurar el entorno de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'biblioteca_project.settings')
django.setup()

from biblioteca.models import Libro

def import_sql_data():
    sql_path = "base dedatos.sql"
    if not os.path.exists(sql_path):
        print(f"Error: No se encontró el archivo {sql_path}")
        return

    with open(sql_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Parsear Autores
    # Ejemplo: (1,'Franz Kafka','Checo')
    autores = {}
    autores_matches = re.findall(r"INSERT INTO `autores` VALUES\s+([^;]+);", content)
    if autores_matches:
        # Dividir los tuplas individuales. Ojo con comas dentro de cadenas, pero en este SQL es sencillo
        tuples = re.findall(r"\(([^)]+)\)", autores_matches[0])
        for t in tuples:
            parts = [p.strip().strip("'") for p in t.split(",")]
            id_autor = int(parts[0])
            nombre_autor = parts[1]
            autores[id_autor] = nombre_autor

    # 2. Parsear Libros
    # Ejemplo: (1,'La metamorfosis',1915,0)
    libros = {}
    libros_matches = re.findall(r"INSERT INTO `libros` VALUES\s+([^;]+);", content)
    if libros_matches:
        tuples = re.findall(r"\(([^)]+)\)", libros_matches[0])
        for t in tuples:
            parts = [p.strip().strip("'") for p in t.split(",")]
            id_libro = int(parts[0])
            titulo = parts[1]
            libros[id_libro] = {
                'titulo': titulo,
                'autor': 'Desconocido' # por defecto si no tiene relación
            }

    # 3. Parsear Relación Libros-Autores
    # Ejemplo: (1,1),(2,1)...
    relaciones_matches = re.findall(r"INSERT INTO `libros_autores` VALUES\s+([^;]+);", content)
    if relaciones_matches:
        tuples = re.findall(r"\(([^)]+)\)", relaciones_matches[0])
        for t in tuples:
            parts = [int(p.strip()) for p in t.split(",")]
            id_libro = parts[0]
            id_autor = parts[1]
            if id_libro in libros and id_autor in autores:
                libros[id_libro]['autor'] = autores[id_autor]

    print(f"Parseados {len(libros)} libros y {len(autores)} autores.")
    
    # 4. Insertar en Django DB
    creados = 0
    actualizados = 0
    
    for idx, (id_lib, info) in enumerate(libros.items(), start=1):
        # Crear un ISBN ficticio basado en el ID para evitar colisiones
        # Formato: 9780000000000 sumando el id_lib al final
        isbn = f"978000000{id_lib:04d}"
        
        # Verificar si el libro ya existe
        libro_obj, created = Libro.objects.get_or_create(
            isbn=isbn,
            defaults={
                'titulo': info['titulo'],
                'autor': info['autor'],
                'cantidad_total': 2, # Valor por defecto
                'tarifa_diaria': 100.00 # Valor por defecto
            }
        )
        
        if created:
            creados += 1
        else:
            # Si ya existía por algún motivo, actualizar datos
            libro_obj.titulo = info['titulo']
            libro_obj.autor = info['autor']
            libro_obj.save()
            actualizados += 1

    print(f"Proceso finalizado. Creados: {creados}. Actualizados: {actualizados}.")

if __name__ == '__main__':
    import_sql_data()
