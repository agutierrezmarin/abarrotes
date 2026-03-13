"""
Script para crear usuarios y grupos iniciales.
Ejecutar con: python manage.py shell < setup_inicial.py
"""

from django.contrib.auth.models import User, Group

# Crear grupos
grupos = ["Vendedor", "Administrador", "Gerente"]
for nombre in grupos:
    g, created = Group.objects.get_or_create(name=nombre)
    print(f"Grupo '{nombre}': {'creado' if created else 'ya existe'}")

# Crear superusuario admin
if not User.objects.filter(username="admin").exists():
    admin = User.objects.create_superuser("admin", "admin@tienda.com", "admin123")
    print("Superusuario 'admin' creado (pass: admin123)")

# Crear usuario vendedor de prueba
if not User.objects.filter(username="vendedor1").exists():
    v = User.objects.create_user(
        "vendedor1", "", "vendedor123", first_name="Juan", last_name="Lopez"
    )
    v.groups.add(Group.objects.get(name="Vendedor"))
    print("Usuario 'vendedor1' creado (pass: vendedor123)")

# Crear usuario administrador
if not User.objects.filter(username="supervisor").exists():
    s = User.objects.create_user(
        "supervisor", "", "super123", first_name="Maria", last_name="Garcia"
    )
    s.groups.add(Group.objects.get(name="Administrador"))
    print("Usuario 'supervisor' creado (pass: super123)")

# Crear usuario gerente
if not User.objects.filter(username="gerente").exists():
    ge = User.objects.create_user(
        "gerente", "", "gerente123", first_name="Carlos", last_name="Mendoza"
    )
    ge.groups.add(Group.objects.get(name="Gerente"))
    print("Usuario 'gerente' creado (pass: gerente123)")

# Crear categorias de prueba
from inventario.models import Categoria, Proveedor

categorias = [
    "Abarrotes",
    "Bebidas",
    "Lacteos",
    "Enlatados",
    "Embutidos",
    "Limpieza",
    "Higiene Personal",
    "Botanas",
    "Pan y Masitas",
]
for nombre in categorias:
    c, created = Categoria.objects.get_or_create(nombre=nombre)
    if created:
        print(f"Categoria '{nombre}' creada")

print("\n=== Setup completado ===")
print("Usuarios creados:")
print("  admin / admin123 (superusuario)")
print("  vendedor1 / vendedor123 (vendedor)")
print("  supervisor / super123 (administrador)")
print("  gerente / gerente123 (gerente)")
