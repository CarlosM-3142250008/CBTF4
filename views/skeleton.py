"""Esqueletos de carga animados para listas y tablas.

CustomTkinter no incluye un componente de skeleton, así que se construyen
con frames redondeados que laten entre un tono base y uno más claro. La
animación se detiene y se destruye en cuanto llegan los datos reales.
"""

import math
import time

import customtkinter as ctk


TONOS = {
    "verde": ("#F7FAF8", "#E4ECE6", "#F1F6F2", "#E1EAE3"),
    "bronce": ("#FBF8F4", "#EEE3D6", "#F8F1E8", "#EADCCB"),
    "neutro": ("#F8FAF9", "#E8ECEA", "#F4F7F5", "#E2E7E4"),
    "azul": ("#F7FAFD", "#E2EAF2", "#F0F6FC", "#DCE7F2"),
}


def _hex_a_rgb(color):
    color = color.lstrip("#")
    return tuple(int(color[indice:indice + 2], 16) for indice in (0, 2, 4))


def _rgb_a_hex(rgb):
    return "#{:02X}{:02X}{:02X}".format(
        *(max(0, min(255, int(round(canal)))) for canal in rgb)
    )


def _mezclar(color_a, color_b, t):
    a = _hex_a_rgb(color_a)
    b = _hex_a_rgb(color_b)
    return _rgb_a_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


class _AnimacionEsqueleto:
    """Cronómetro compartido por todos los bloques de un esqueleto."""

    def __init__(self, propietario):
        self._propietario = propietario
        self._id = None
        self._activo = False
        self._inicio = 0.0

    def iniciar(self):
        if self._activo:
            return
        self._activo = True
        self._inicio = time.perf_counter()
        self._paso()

    def detener(self):
        self._activo = False
        if self._id is not None:
            try:
                self._propietario.after_cancel(self._id)
            except Exception:
                pass
            self._id = None

    def _paso(self):
        self._id = None
        if not self._activo:
            return
        try:
            if not self._propietario.winfo_exists():
                return
        except Exception:
            return
        self._propietario._animar_esqueleto(time.perf_counter() - self._inicio)
        self._id = self._propietario.after(55, self._paso)


class _BaseEsqueleto(ctk.CTkFrame):
    def __init__(self, parent, tono="neutro", **kwargs):
        kwargs.setdefault("fg_color", "transparent")
        super().__init__(parent, **kwargs)
        self._fondo, self._base, self._brillo, self._borde = TONOS.get(
            tono, TONOS["neutro"]
        )
        self._barras = []
        self._animacion = _AnimacionEsqueleto(self)

    def _barra(self, parent, **kwargs):
        kwargs.setdefault("corner_radius", 6)
        kwargs.setdefault("fg_color", self._base)
        barra = ctk.CTkFrame(parent, **kwargs)
        self._barras.append(barra)
        return barra

    def iniciar(self):
        self._animacion.iniciar()

    def detener(self):
        self._animacion.detener()

    def destroy(self):
        self.detener()
        super().destroy()

    def _animar_esqueleto(self, transcurrido):
        if not self._barras:
            return
        for indice, barra in enumerate(self._barras):
            fase = indice * 0.42
            pulso = (math.sin(transcurrido * 3.1 + fase) + 1.0) / 2.0
            color = _mezclar(self._base, self._brillo, 0.25 + pulso * 0.75)
            try:
                barra.configure(fg_color=color)
            except Exception:
                continue


class SkeletonLista(_BaseEsqueleto):
    """Varias tarjetas fantasma con la silueta de un aviso o material."""

    def __init__(self, parent, filas=3, tono="neutro", compacto=False, **kwargs):
        super().__init__(parent, tono=tono, **kwargs)
        self.pack(fill="x", padx=1, pady=(2, 6))

        alto = 88 if compacto else 112
        for indice in range(max(1, filas)):
            tarjeta = ctk.CTkFrame(
                self,
                height=alto,
                corner_radius=14,
                fg_color=self._fondo,
                border_width=1,
                border_color=self._borde,
            )
            tarjeta.pack(fill="x", pady=5)
            tarjeta.pack_propagate(False)

            self._barra(
                tarjeta, width=34, height=34, corner_radius=12
            ).place(x=14, y=14)
            self._barra(tarjeta, height=11).place(x=58, y=19, relwidth=0.46)
            self._barra(
                tarjeta, width=52, height=18, corner_radius=8
            ).place(relx=0.88, y=16)
            self._barra(tarjeta, height=8).place(x=58, y=42, relwidth=0.62)
            self._barra(tarjeta, height=8).place(x=58, y=58, relwidth=0.46)

            if not compacto:
                self._barra(tarjeta, height=8).place(
                    x=14, y=80, relwidth=0.84
                )
                self._barra(tarjeta, height=8).place(
                    x=14, y=94, relwidth=0.63
                )

        self.iniciar()


class SkeletonTabla(_BaseEsqueleto):
    """Filas fantasma para el pase de lista de asistencia."""

    def __init__(self, parent, filas=5, tono="azul", **kwargs):
        super().__init__(parent, tono=tono, **kwargs)
        self.pack(fill="x", padx=10, pady=8)

        for indice in range(max(1, filas)):
            fila = ctk.CTkFrame(
                self,
                height=54,
                corner_radius=12,
                fg_color=self._fondo,
                border_width=1,
                border_color=self._borde,
            )
            fila.pack(fill="x", pady=4)
            fila.pack_propagate(False)

            self._barra(
                fila, width=30, height=30, corner_radius=15
            ).place(x=14, y=12)
            self._barra(fila, height=10).place(x=54, y=22, relwidth=0.28)
            self._barra(
                fila, height=28, corner_radius=10
            ).place(relx=0.52, y=13, relwidth=0.44)

        self.iniciar()


class SkeletonBloque(_BaseEsqueleto):
    """Bloque suelto para valores que todavía no han llegado."""

    def __init__(self, parent, ancho=90, alto=14, tono="neutro", **kwargs):
        super().__init__(parent, tono=tono, **kwargs)
        self._barra(self, width=ancho, height=alto, corner_radius=alto // 2).pack()
        self.iniciar()
