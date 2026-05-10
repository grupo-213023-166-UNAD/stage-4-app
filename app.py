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

class ReservaSala(Servicio):

    def calcular_costo(self, horas):
        if horas <= 0 or horas > 12:
            raise DatosInvalidosError(f"Horas invalidas para sala: {horas} (máx. 12).")
        return round(self.precio_hora * horas, 2)

    def calcular_costo_con_opciones(self, horas, iva=False, descuento=0.0):
        costo = self.calcular_costo(horas) * (1 - descuento)
        return round(costo * 1.19 if iva else costo, 2)

    def mostrar_info(self):
        return f"[Sala]    {self.nombre} | ${self.precio_hora:,}/h | {'Disponible' if self.disponible else 'No disponible'}"


class AlquilerEquipo(Servicio):
    def calcular_costo(self, horas):
        if horas <= 0:
            raise DatosInvalidosError(f"Horas invalidas para equipo: {horas}.")
        return round(self.precio_hora * horas, 2)

    def calcular_costo_con_opciones(self, horas, iva=False, descuento=0.0):
        costo = self.calcular_costo(horas) * (1 - descuento)
        return round(costo * 1.19 if iva else costo, 2)

    def mostrar_info(self):
        return f"[Equipo]  {self.nombre} | ${self.precio_hora:,}/h | {'Disponible' if self.disponible else 'No disponible'}"


class AsesoriaEspecializada(Servicio):
    AREAS = ["tecnologia", "legal", "financiera", "marketing"]

    def __init__(self, codigo, nombre, precio_hora, area):
        super().__init__(codigo, nombre, precio_hora)
        if area.lower() not in self.AREAS:
            raise DatosInvalidosError(f"area invalida: '{area}'. Validas: {self.AREAS}")
        self.area = area.lower()

    def calcular_costo(self, horas):
        if not (1 <= horas <= 8):
            raise DatosInvalidosError(f"Horas de Asesoria fuera de rango: {horas} (1-8).")
        return round(self.precio_hora * horas, 2)

    def calcular_costo_con_opciones(self, horas, iva=False, descuento=0.0):
        costo = self.calcular_costo(horas) * (1 - descuento)
        return round(costo * 1.19 if iva else costo, 2)

    def mostrar_info(self):
        return f"[Asesoria] {self.nombre} ({self.area}) | ${self.precio_hora:,}/h | {'Disponible' if self.disponible else 'No disponible'}"

# Clase reserva
class Reserva(Entidad):
    _contador = 0

    def __init__(self, cliente, servicio, horas):
        if not isinstance(cliente, Cliente):
            raise DatosInvalidosError("Cliente no válido.")
        if not isinstance(servicio, Servicio):
            raise DatosInvalidosError("Servicio no válido.")
        if not isinstance(horas, (int, float)) or horas <= 0:
            raise DatosInvalidosError(f"Duracion invalida: {horas}.")
        Reserva._contador += 1
        self.id       = f"RES-{Reserva._contador:03d}"
        self.cliente  = cliente
        self.servicio = servicio
        self.horas    = horas
        self.estado   = "Pendiente"
        self.costo    = 0.0

    def validar(self):
        return self.estado == "Confirmada"

    def confirmar(self, iva=False, descuento=0.0):
        print(f"  Procesando {self.id} → {self.cliente.nombre} / {self.servicio.nombre}")
        try:
            self.servicio.verificar_disponibilidad()
            self.costo = self.servicio.calcular_costo_con_opciones(self.horas, iva, descuento)
        except (ServicioNoDisponibleError, DatosInvalidosError) as e:
            self.estado = "Cancelada"
            registrar("error", f"{self.id} fallida: {e}")
            # Encadenamiento de excepciones
            raise ReservaError(f"No se pudo confirmar {self.id}.") from e
        except Exception as e:
            self.estado = "Error"
            registrar("error", f"{self.id} error inesperado: {e}")
        else:
            # Solo se ejecuta si no hubo excepcion
            self.estado = "Confirmada"
            self.cliente.reservas.append(self)
            registrar("info", f"{self.id} confirmada | Costo: ${self.costo:,.2f}")
        finally:
            # Siempre se ejecuta
            print(f"  Estado: {self.estado} | Costo: ${self.costo:,.2f}")

    def cancelar(self):
        if self.estado in ("Cancelada", "Completada"):
            raise ReservaError(f"{self.id} ya esta en estado '{self.estado}'.")
        self.estado = "Cancelada"
        registrar("warning", f"{self.id} cancelada por el cliente.")

    def completar(self):
        if self.estado != "Confirmada":
            raise ReservaError(f"Solo se completan reservas confirmadas. Estado: {self.estado}")
        self.estado = "Completada"
        registrar("info", f"{self.id} completada.")

    def mostrar_info(self):
        return f"{self.id} | {self.cliente.nombre} | {self.servicio.nombre} | {self.horas}h | {self.estado} | ${self.costo:,.2f}"
    
    
# Proceso de simulacion — 10 operaciones
def simular():
    print("=" * 55)
    print("  SOFTWARE FJ — Sistema de Gestion")
    print("=" * 55)
    logging.info("--- NUEVO PROCESO DE GESTION ---")

    clientes, servicios, reservas = [], [], []

    # Op 1: Cliente válido
    print("[Op 1] Registrar cliente válido")
    try:
        c1 = Cliente("C01", "Kike Martinez", "kike@mail.com", "3001234567")
        clientes.append(c1)
        registrar("info", c1.mostrar_info())
    except DatosInvalidosError as e:
        registrar("error", str(e))

    # Op 2: Cliente con email invalido
    print("[Op 2] Cliente con email invalido")
    try:
        c2 = Cliente("C02", "Ana Torres", "torresGmail", "3109876543")
    except DatosInvalidosError as e:
        registrar("error", str(e))

    # Op 3: Cliente con teléfono invalido
    print("[Op 3] Cliente con teléfono invalido")
    try:
        c3 = Cliente("C03", "Luis Gómez", "luis@mail.com", "abc")
    except DatosInvalidosError as e:
        registrar("error", str(e))

    # Op 4: Segundo cliente válido
    print("[Op 4] Segundo cliente válido")
    try:
        c4 = Cliente("C04", "Carlos Ruiz", "carlos@empresa.co", "6012345678")
        clientes.append(c4)
        registrar("info", c4.mostrar_info())
    except DatosInvalidosError as e:
        registrar("error", str(e))

    # Op 5: Crear servicios válidos
    print("[Op 5] Crear servicios")
    sala    = ReservaSala("S01", "Sala de Juntas VIP", 100_000)
    equipo  = AlquilerEquipo("E01", "Proyector 4K", 80_000)
    asesoria = AsesoriaEspecializada("A01", "Auditoria Contable", 250_000, area="financiera")
    for s in [sala, equipo, asesoria]:
        servicios.append(s)
        registrar("info", s.mostrar_info())

    # Op 6: Servicio con precio negativo
    print("[Op 6] Servicio con precio negativo")
    try:
        s_malo = ReservaSala("S99", "Sala invalida", -500)
    except DatosInvalidosError as e:
        registrar("error", str(e))

    # Op 7: Asesoria con area invalida
    print("[Op 7] Asesoria con area invalida")
    try:
        a_mala = AsesoriaEspecializada("A99", "Asesoria Cocina", 150_000, area="cocina")
    except DatosInvalidosError as e:
        registrar("error", str(e))

    # Op 8: Reserva con duracion negativa
    print("[Op 8] Reserva con duracion negativa")
    try:
        r_mala = Reserva(c1, sala, -3)
    except DatosInvalidosError as e:
        registrar("error", str(e))

        
    # Op 9: Reserva exitosa
    print("[Op 9] Reserva exitosa (Asesoria, 2h, IVA + 10% descuento)")
    try:
        r1 = Reserva(c1, asesoria, 2)
        reservas.append(r1)
        r1.confirmar(iva=True, descuento=0.10)
    except ReservaError as e:
        registrar("error", str(e))

    # Op 10: Reserva fallida (servicio no disponible)
    print("[Op 10] Reserva fallida — servicio no disponible")
    sala.disponible = False
    try:
        r2 = Reserva(c4, sala, 3)
        reservas.append(r2)
        r2.confirmar()
    except ReservaError as e:
        registrar("error", f"Encadenada → {e}")
    finally:
        sala.disponible = True  # restaurar

    # Op 11: Reserva y cancelacion
    print("[Op 11] Reserva de equipo + cancelacion")
    try:
        r3 = Reserva(c4, equipo, 4)
        reservas.append(r3)
        r3.confirmar()
        r3.cancelar()
    except ReservaError as e:
        registrar("error", str(e))

    # Op 12: Cancelar reserva ya cancelada 
    print("[Op 12] Cancelar reserva ya cancelada")
    try:
        r3.cancelar()
    except ReservaError as e:
        registrar("error", str(e))

    # Resumen
    print("" + "=" * 55)
    print("  RESUMEN FINAL")
    print("=" * 55)
    print(f"  Clientes  : {len(clientes)}")
    print(f"  Servicios : {len(servicios)}")
    print(f"  Reservas  : {len(reservas)}")
    print("  Detalle reservas:")
    for r in reservas:
        print(f"    {r.mostrar_info()}")
    print("  Log guardado en: sistema_errores.log")
    print("=" * 55)

if __name__ == "__main__":
    simular()
