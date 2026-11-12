# ============================================================
# UNIVERSIDAD NACIONAL ABIERTA Y A DISTANCIA - UNAD
# CURSO: PROGRAMACION - CODIGO 213023
# FASE 4 - EJERCICIO 1
# SISTEMA INTEGRAL DE GESTION DE CLIENTES, SERVICIOS Y RESERVAS
# EMPRESA: SOFTWARE FJ
# ============================================================

from abc import ABC, abstractmethod
import logging
from datetime import datetime


# ============================================================
# 1. CONFIGURACION DEL REGISTRO DE EVENTOS Y ERRORES
# ============================================================

logging.basicConfig(
    filename="software_fj.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    encoding="utf-8"
)

logger = logging.getLogger("SoftwareFJ")


# ============================================================
# 2. EXCEPCIONES PERSONALIZADAS
# ============================================================

class SistemaError(Exception):
    pass


class ValidacionError(SistemaError):
    pass


class ServicioNoDisponibleError(SistemaError):
    pass


class ReservaError(SistemaError):
    pass


# ============================================================
# 3. FUNCION AUXILIAR PARA VALIDAR NUMEROS
# ============================================================

def validar_numero(valor, nombre, minimo=0):

    if not isinstance(valor, (int, float)) or isinstance(valor, bool):
        raise ValidacionError(
            f"El valor de {nombre} debe ser numerico."
        )

    if valor <= minimo:
        raise ValidacionError(
            f"El valor de {nombre} debe ser mayor que {minimo}."
        )


# ============================================================
# 4. CLASE ABSTRACTA ENTIDAD
# ============================================================

class Entidad(ABC):

    def __init__(self, identificacion):

        if identificacion is None or not str(identificacion).strip():
            raise ValidacionError(
                "La identificacion es obligatoria."
            )

        self._identificacion = str(identificacion).strip()

    @property
    def identificacion(self):
        return self._identificacion

    @abstractmethod
    def mostrar_informacion(self):
        pass


# ============================================================
# 5. CLASE CLIENTE
# ============================================================

class Cliente(Entidad):

    def __init__(self, identificacion, nombre, correo, telefono):

        super().__init__(identificacion)

        self.nombre = nombre
        self.correo = correo
        self.telefono = telefono

    @property
    def nombre(self):
        return self._nombre

    @nombre.setter
    def nombre(self, valor):

        if not isinstance(valor, str) or len(valor.strip()) < 3:
            raise ValidacionError(
                "El nombre debe contener al menos 3 caracteres."
            )

        self._nombre = valor.strip()

    @property
    def correo(self):
        return self._correo

    @correo.setter
    def correo(self, valor):

        try:

            if not isinstance(valor, str):
                raise ValueError("El correo debe ser texto.")

            valor = valor.strip()

            if (
                "@" not in valor
                or valor.count("@") != 1
                or "." not in valor.split("@")[1]
            ):
                raise ValueError("Formato de correo incorrecto.")

            self._correo = valor

        except ValueError as error:

            raise ValidacionError(
                "No fue posible registrar el correo del cliente."
            ) from error

    @property
    def telefono(self):
        return self._telefono

    @telefono.setter
    def telefono(self, valor):

        valor = str(valor)

        if not valor.isdigit() or len(valor) < 7:
            raise ValidacionError(
                "El telefono debe contener minimo 7 digitos."
            )

        self._telefono = valor

    def mostrar_informacion(self):

        return (
            f"ID: {self.identificacion} | "
            f"Nombre: {self.nombre} | "
            f"Correo: {self.correo} | "
            f"Telefono: {self.telefono}"
        )
# ============================================================
# 6. CLASE ABSTRACTA SERVICIO
# ============================================================

class Servicio(Entidad, ABC):

    def __init__(
        self,
        identificacion,
        nombre,
        precio,
        disponible=True
    ):

        super().__init__(identificacion)

        if not isinstance(nombre, str) or not nombre.strip():
            raise ValidacionError(
                "El nombre del servicio es obligatorio."
            )

        validar_numero(precio, "precio")

        if not isinstance(disponible, bool):
            raise ValidacionError(
                "La disponibilidad debe ser verdadera o falsa."
            )

        self.nombre = nombre.strip()
        self.precio = float(precio)
        self.disponible = disponible

    @abstractmethod
    def calcular_costo(self, duracion, impuestos=0.19, descuento=0):
        pass

    @abstractmethod
    def describir_servicio(self):
        pass

    @abstractmethod
    def validar_parametros(self, duracion):
        pass

    def mostrar_informacion(self):

        return (
            f"{self.nombre} | "
            f"Precio base: ${self.precio:,.0f} | "
            f"Disponible: {self.disponible}"
        )


# ============================================================
# 7. SERVICIO: RESERVA DE SALAS
# ============================================================

class ReservaSala(Servicio):

    def __init__(self, identificacion, precio_hora, capacidad):

        super().__init__(
            identificacion,
            "Reserva de salas",
            precio_hora
        )

        if not isinstance(capacidad, int) or isinstance(capacidad, bool) or capacidad <= 0:
            raise ValidacionError(
                "La capacidad debe ser un numero entero positivo."
            )

        self.capacidad = capacidad

    def validar_parametros(self, duracion):

        validar_numero(duracion, "duracion")
        return True

    def calcular_costo(self, duracion, impuestos=0.19, descuento=0):

        self.validar_parametros(duracion)

        if not 0 <= impuestos <= 1:
            raise ValidacionError("Impuestos fuera del rango permitido.")

        if not 0 <= descuento <= 1:
            raise ValidacionError("Descuento fuera del rango permitido.")

        subtotal = self.precio * duracion
        subtotal_descuento = subtotal * (1 - descuento)

        return subtotal_descuento * (1 + impuestos)

    def describir_servicio(self):

        return (
            f"Reserva de salas | "
            f"Capacidad: {self.capacidad} personas | "
            f"Precio por hora: ${self.precio:,.0f}"
        )


# ============================================================
# 8. SERVICIO: ALQUILER DE EQUIPOS
# ============================================================

class AlquilerEquipos(Servicio):

    def __init__(self, identificacion, precio_hora, tipo_equipo):

        super().__init__(
            identificacion,
            "Alquiler de equipos",
            precio_hora
        )

        if not isinstance(tipo_equipo, str) or not tipo_equipo.strip():
            raise ValidacionError(
                "Debe especificar el tipo de equipo."
            )

        self.tipo_equipo = tipo_equipo.strip()

    def validar_parametros(self, duracion):

        validar_numero(duracion, "duracion")
        return True

    def calcular_costo(self, duracion, impuestos=0.19, descuento=0):

        self.validar_parametros(duracion)

        if not 0 <= impuestos <= 1 or not 0 <= descuento <= 1:
            raise ValidacionError(
                "Los impuestos y descuentos deben estar entre 0 y 1."
            )

        subtotal = self.precio * duracion
        subtotal_descuento = subtotal * (1 - descuento)

        return subtotal_descuento * (1 + impuestos)

    def describir_servicio(self):

        return (
            f"Alquiler de equipos | "
            f"Tipo: {self.tipo_equipo} | "
            f"Precio por hora: ${self.precio:,.0f}"
        )


# ============================================================
# 9. SERVICIO: ASESORIAS ESPECIALIZADAS
# ============================================================

class AsesoriaEspecializada(Servicio):

    def __init__(self, identificacion, precio_hora, especialidad):

        super().__init__(
            identificacion,
            "Asesorias especializadas",
            precio_hora
        )

        if not isinstance(especialidad, str) or not especialidad.strip():
            raise ValidacionError(
                "La especialidad es obligatoria."
            )

        self.especialidad = especialidad.strip()

    def validar_parametros(self, duracion):

        validar_numero(duracion, "duracion")
        return True

    def calcular_costo(self, duracion, impuestos=0.19, descuento=0):

        self.validar_parametros(duracion)

        if not 0 <= impuestos <= 1 or not 0 <= descuento <= 1:
            raise ValidacionError(
                "Los impuestos y descuentos deben estar entre 0 y 1."
            )

        subtotal = self.precio * duracion
        subtotal_descuento = subtotal * (1 - descuento)

        return subtotal_descuento * (1 + impuestos)

    def describir_servicio(self):

        return (
            f"Asesoria especializada | "
            f"Especialidad: {self.especialidad} | "
            f"Precio por hora: ${self.precio:,.0f}"
        )


# ============================================================
# 10. CLASE RESERVA
# ============================================================

class Reserva(Entidad):

    def __init__(self, identificacion, cliente, servicio, duracion):

        super().__init__(identificacion)

        if not isinstance(cliente, Cliente):
            raise ValidacionError(
                "Debe ingresar un cliente valido."
            )

        if not isinstance(servicio, Servicio):
            raise ValidacionError(
                "Debe ingresar un servicio valido."
            )

        validar_numero(duracion, "duracion")

        self.cliente = cliente
        self.servicio = servicio
        self.duracion = duracion
        self.estado = "Pendiente"
        self.fecha = datetime.now().strftime("%d/%m/%Y %H:%M")

    def confirmar(self):

        if self.estado != "Pendiente":
            raise ReservaError(
                "Solo se pueden confirmar reservas pendientes."
            )

        if not self.servicio.disponible:
            raise ServicioNoDisponibleError(
                "El servicio seleccionado no esta disponible."
            )

        self.servicio.validar_parametros(self.duracion)

        self.estado = "Confirmada"

        logger.info(
            f"Reserva {self.identificacion} confirmada."
        )

        return True

    def cancelar(self):

        if self.estado not in ("Pendiente", "Confirmada"):
            raise ReservaError(
                "La reserva no puede cancelarse en su estado actual."
            )

        self.estado = "Cancelada"

        logger.info(
            f"Reserva {self.identificacion} cancelada."
        )

        return True

    def procesar(self, impuestos=0.19, descuento=0):

        try:

            if self.estado != "Pendiente":
                raise ReservaError(
                    "La reserva no se encuentra pendiente."
                )

            if not self.servicio.disponible:
                raise ServicioNoDisponibleError(
                    "El servicio no esta disponible."
                )

            costo = self.servicio.calcular_costo(
                self.duracion,
                impuestos,
                descuento
            )

        except SistemaError as error:

            logger.exception(
                f"Error procesando reserva {self.identificacion}"
            )

            raise

        else:

            logger.info(
                f"Reserva {self.identificacion} procesada. "
                f"Costo: ${costo:,.0f}"
            )

            return costo

        finally:

            print(
                f"Proceso de reserva {self.identificacion} finalizado."
            )

    def mostrar_informacion(self):

        return (
            f"Reserva: {self.identificacion} | "
            f"Cliente: {self.cliente.nombre} | "
            f"Servicio: {self.servicio.nombre} | "
            f"Duracion: {self.duracion} horas | "
            f"Estado: {self.estado}"
        )
# ============================================================
# 11. CLASE PRINCIPAL DEL SISTEMA SOFTWARE FJ
# ============================================================

class SistemaSoftwareFJ:

    def __init__(self):

        self.clientes = []
        self.servicios = []
        self.reservas = []

        logger.info("Sistema Software FJ iniciado correctamente.")

    # REGISTRO DE CLIENTES

    def registrar_cliente(self, cliente):

        if not isinstance(cliente, Cliente):
            raise ValidacionError(
                "El objeto ingresado no es un cliente."
            )

        if any(
            c.identificacion == cliente.identificacion
            for c in self.clientes
        ):
            raise ValidacionError(
                "El cliente ya se encuentra registrado."
            )

        self.clientes.append(cliente)

        logger.info(
            f"Cliente registrado: {cliente.nombre}"
        )

        return True

    # REGISTRO DE SERVICIOS

    def registrar_servicio(self, servicio):

        if not isinstance(servicio, Servicio):
            raise ValidacionError(
                "El objeto no corresponde a un servicio valido."
            )

        if any(
            s.identificacion == servicio.identificacion
            for s in self.servicios
        ):
            raise ValidacionError(
                "El servicio ya se encuentra registrado."
            )

        self.servicios.append(servicio)

        logger.info(
            f"Servicio registrado: {servicio.nombre}"
        )

        return True

    # CREACION DE RESERVAS

    def crear_reserva(self, identificacion, cliente, servicio, duracion):

        if not isinstance(cliente, Cliente) or cliente not in self.clientes:
            raise ReservaError(
                "El cliente no esta registrado."
            )

        if not isinstance(servicio, Servicio) or servicio not in self.servicios:
            raise ReservaError(
                "El servicio no esta registrado."
            )

        identificacion = str(identificacion)

        if any(
            r.identificacion == identificacion
            for r in self.reservas
        ):
            raise ReservaError(
                "El identificador de reserva ya existe."
            )

        reserva = Reserva(
            identificacion,
            cliente,
            servicio,
            duracion
        )

        self.reservas.append(reserva)

        logger.info(
            f"Reserva {identificacion} creada correctamente."
        )

        return reserva

    # LISTADO DE CLIENTES

    def listar_clientes(self):

        print("\n========== LISTADO DE CLIENTES ==========")

        if not self.clientes:
            print("No hay clientes registrados.")
            return

        for cliente in self.clientes:
            print(cliente.mostrar_informacion())

    # LISTADO DE SERVICIOS

    def listar_servicios(self):

        print("\n========== LISTADO DE SERVICIOS ==========")

        if not self.servicios:
            print("No hay servicios registrados.")
            return

        for servicio in self.servicios:
            print(servicio.describir_servicio())

    # LISTADO DE RESERVAS

    def listar_reservas(self):

        print("\n========== LISTADO DE RESERVAS ==========")

        if not self.reservas:
            print("No hay reservas registradas.")
            return

        for reserva in self.reservas:
            print(reserva.mostrar_informacion())
# ============================================================
# 12. FUNCION PARA EJECUTAR OPERACIONES Y CONTROLAR ERRORES
# ============================================================

def ejecutar_operacion(descripcion, funcion):

    print("\n" + "=" * 65)
    print(descripcion)
    print("=" * 65)

    try:

        resultado = funcion()

    except SistemaError as error:

        print(f"ERROR CONTROLADO: {error}")

        logger.exception(
            f"Error controlado: {descripcion}"
        )

    except Exception as error:

        print(f"ERROR INESPERADO: {error}")

        logger.exception(
            f"Error inesperado: {descripcion}"
        )

    else:

        print("Operacion realizada correctamente.")

        if resultado is not None:
            print(resultado)

    finally:

        print("Operacion finalizada. El sistema continua funcionando.")


# ============================================================
# 13. FUNCION PRINCIPAL Y SIMULACION DE OPERACIONES
# ============================================================

def main():

    print("\n")
    print("*" * 65)
    print("       SISTEMA INTEGRAL DE GESTION SOFTWARE FJ")
    print("*" * 65)

    sistema = SistemaSoftwareFJ()

    # OPERACION 1: REGISTRO DE CLIENTE VALIDO

    cliente1 = Cliente(
        "1001",
        "Carlos Ramirez",
        "carlos@gmail.com",
        "3001234567"
    )

    ejecutar_operacion(
        "OPERACION 1: REGISTRO DE CLIENTE VALIDO",
        lambda: sistema.registrar_cliente(cliente1)
    )

    # OPERACION 2: CLIENTE CON CORREO INVALIDO

    def registrar_cliente_invalido():

        cliente = Cliente(
            "1002",
            "Maria Lopez",
            "mariahotmail.com",
            "3014567890"
        )

        return sistema.registrar_cliente(cliente)

    ejecutar_operacion(
        "OPERACION 2: REGISTRO DE CLIENTE CON CORREO INVALIDO",
        registrar_cliente_invalido
    )

    # OPERACION 3: REGISTRO DE SEGUNDO CLIENTE

    cliente2 = Cliente(
        "1003",
        "Andrea Torres",
        "andrea@gmail.com",
        "3025678910"
    )

    ejecutar_operacion(
        "OPERACION 3: REGISTRO DE SEGUNDO CLIENTE",
        lambda: sistema.registrar_cliente(cliente2)
    )

    # OPERACION 4: REGISTRO DE SALA

    sala = ReservaSala(
        "S001",
        50000,
        20
    )

    ejecutar_operacion(
        "OPERACION 4: REGISTRO DE SERVICIO DE SALAS",
        lambda: sistema.registrar_servicio(sala)
    )

    # OPERACION 5: REGISTRO DE EQUIPOS

    equipo = AlquilerEquipos(
        "S002",
        30000,
        "Computadores portatiles"
    )

    ejecutar_operacion(
        "OPERACION 5: REGISTRO DE ALQUILER DE EQUIPOS",
        lambda: sistema.registrar_servicio(equipo)
    )

    # OPERACION 6: REGISTRO DE ASESORIAS

    asesoria = AsesoriaEspecializada(
        "S003",
        80000,
        "Administracion de sistemas"
    )

    ejecutar_operacion(
        "OPERACION 6: REGISTRO DE ASESORIAS",
        lambda: sistema.registrar_servicio(asesoria)
    )

    # OPERACION 7: SERVICIO CON PRECIO INVALIDO

    def crear_servicio_invalido():

        servicio = ReservaSala(
            "S004",
            -50000,
            15
        )

        return sistema.registrar_servicio(servicio)

    ejecutar_operacion(
        "OPERACION 7: CREACION DE SERVICIO CON PRECIO INVALIDO",
        crear_servicio_invalido
    )

    # OPERACION 8: CREACION DE RESERVA

    reserva1 = None

    def crear_reserva_correcta():

        nonlocal reserva1

        reserva1 = sistema.crear_reserva(
            "R001",
            cliente1,
            sala,
            3
        )

        return reserva1.mostrar_informacion()

    ejecutar_operacion(
        "OPERACION 8: CREACION DE RESERVA CORRECTA",
        crear_reserva_correcta
    )

    # OPERACION 9: CONFIRMACION DE RESERVA

    ejecutar_operacion(
        "OPERACION 9: CONFIRMACION DE RESERVA",
        reserva1.confirmar
    )

    # OPERACION 10: CALCULO DE COSTO CON IMPUESTOS

    ejecutar_operacion(
        "OPERACION 10: CALCULO DE COSTO CON IMPUESTOS",
        lambda: f"Costo total: ${sala.calcular_costo(3):,.0f}"
    )

    # OPERACION 11: CALCULO CON DESCUENTO

    ejecutar_operacion(
        "OPERACION 11: CALCULO CON DESCUENTO DEL 10%",
        lambda: (
            f"Costo con descuento e impuestos: "
            f"${sala.calcular_costo(3, 0.19, 0.10):,.0f}"
        )
    )

    # OPERACION 12: SERVICIO NO DISPONIBLE

    equipo.disponible = False

    def reservar_servicio_no_disponible():

        reserva2 = sistema.crear_reserva(
            "R002",
            cliente2,
            equipo,
            2
        )

        return reserva2.confirmar()

    ejecutar_operacion(
        "OPERACION 12: RESERVA DE SERVICIO NO DISPONIBLE",
        reservar_servicio_no_disponible
    )

    # OPERACION 13: CANCELACION DE RESERVA

    reserva3 = sistema.crear_reserva(
        "R003",
        cliente2,
        asesoria,
        2
    )

    ejecutar_operacion(
        "OPERACION 13: CANCELACION DE RESERVA",
        reserva3.cancelar
    )

    # OPERACION 14: CANCELACION NO PERMITIDA

    ejecutar_operacion(
        "OPERACION 14: INTENTO DE CANCELACION NO PERMITIDA",
        reserva3.cancelar
    )

    # OPERACION 15: DURACION INVALIDA

    ejecutar_operacion(
        "OPERACION 15: RESERVA CON DURACION INVALIDA",
        lambda: sistema.crear_reserva(
            "R004",
            cliente1,
            sala,
            -2
        )
    )

    # OPERACION 16: CONFIRMACION DUPLICADA

    ejecutar_operacion(
        "OPERACION 16: CONFIRMACION DE RESERVA YA CONFIRMADA",
        reserva1.confirmar
    )

    # OPERACION 17: CLIENTE DUPLICADO

    ejecutar_operacion(
        "OPERACION 17: REGISTRO DE CLIENTE DUPLICADO",
        lambda: sistema.registrar_cliente(cliente1)
    )

    # OPERACION 18: PROCESAMIENTO DE RESERVA

    reserva4 = sistema.crear_reserva(
        "R005",
        cliente2,
        asesoria,
        2
    )

    ejecutar_operacion(
        "OPERACION 18: PROCESAMIENTO DE RESERVA DE ASESORIA",
        lambda: (
            f"Costo de asesoria: ${reserva4.procesar():,.0f}"
        )
    )

    # OPERACION 19: PROCESAMIENTO CON DESCUENTO

    ejecutar_operacion(
        "OPERACION 19: PROCESAMIENTO CON DESCUENTO DEL 15%",
        lambda: (
            f"Costo final: "
            f"${reserva4.procesar(0.19, 0.15):,.0f}"
        )
    )

    # OPERACION 20: IMPUESTO INVALIDO

    ejecutar_operacion(
        "OPERACION 20: CALCULO DE COSTO CON IMPUESTO INVALIDO",
        lambda: sala.calcular_costo(2, 1.5, 0)
    )
