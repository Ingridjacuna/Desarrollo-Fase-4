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
