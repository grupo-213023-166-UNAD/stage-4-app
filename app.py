# UNAD
# CURSO: PROGRAMACIÓN
# TUTOR: JHON HAROLD PATIñO PANTOJA
# GRUPO: 213023_166
# INTEGRANTES: MARIA STEFFANY ORTEGA CORTES Y YANNICK JOSE ACOSTA PRADO

import logging
from abc import ABC, abstractmethod

# Archivo de logs
logging.basicConfig(
    filename='sistema_errores.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def registrar(nivel, mensaje):
# Carga del log y muestra en consola
    getattr(logging, nivel)(mensaje)
    print(f"  [{nivel.upper()}] {mensaje}")

# Manejo de errores personalizados
class SistemaError(Exception):
    pass

class DatosInvalidosError(SistemaError):
    pass

class ServicioNoDisponibleError(SistemaError):
    pass

class ReservaError(SistemaError):
    pass


# Clase abstracta
class Entidad(ABC):
    @abstractmethod
    def mostrar_info(self):
        pass

    @abstractmethod
    def validar(self):
        pass


# Clase abstracta de cliente
class Cliente(Entidad):
    def __init__(self, id_cliente, nombre, email, telefono):
        self.id_cliente = id_cliente
        # Validaciones
        if not nombre or len(nombre.strip()) < 3:
            raise DatosInvalidosError(f"Nombre invalido: '{nombre}'.")
        if "@" not in email or "." not in email.split("@")[-1]:
            raise DatosInvalidosError(f"Email invalido: '{email}'.")
        if not str(telefono).replace("-", "").isdigit() or len(str(telefono)) < 7:
            raise DatosInvalidosError(f"Teléfono invalido: '{telefono}'.")
        self.nombre   = nombre.strip()
        self.email    = email.strip().lower()
        self.telefono = str(telefono)
        self.reservas = []

    def validar(self):
        return bool(self.nombre and self.email and self.telefono)

    def mostrar_info(self):
        return f"Cliente [{self.id_cliente}] {self.nombre} | {self.email} | {self.telefono}"
    
    # Clase abstracta de servicio con las clases derivadas a continuación
class Servicio(Entidad, ABC):
    def __init__(self, codigo, nombre, precio_hora):
        if not isinstance(precio_hora, (int, float)) or precio_hora <= 0:
            raise DatosInvalidosError(f"Precio invalido: '{precio_hora}'.")
        self.codigo     = codigo
        self.nombre     = nombre
        self.precio_hora = precio_hora
        self.disponible  = True

    def validar(self):
        return self.precio_hora > 0

    def verificar_disponibilidad(self):
        if not self.disponible:
            raise ServicioNoDisponibleError(f"'{self.nombre}' no esta disponible.")

    # Costo base (sin extras)
    @abstractmethod
    def calcular_costo(self, horas):
        pass

    # Costo con opciones: IVA y descuento (sobrecarga simulada con parámetros opcionales)
    @abstractmethod
    def calcular_costo_con_opciones(self, horas, iva=False, descuento=0.0):
        pass

    @abstractmethod
    def mostrar_info(self):
        pass