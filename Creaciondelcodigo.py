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
