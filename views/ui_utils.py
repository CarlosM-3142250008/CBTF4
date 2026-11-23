"""Utilidades visuales y de formato compartidas por las vistas."""

import unicodedata
from datetime import date, datetime, time, timedelta

import customtkinter as ctk

from views.icons import (
    AZUL,
    BRONCE,
    GRIS_OSCURO,
    VERDE,
    icono,
)
from views.typography import fuente_etiqueta, fuente_titulo


# Paleta institucional y colores de apoyo
COLOR_PRIMARIO = "#1D6F23"
COLOR_PRIMARIO_HOVER = "#15531A"
COLOR_SECUNDARIO = "#A3723E"
COLOR_SECUNDARIO_HOVER = "#865C30"
COLOR_FONDO = "#F4F6F8"
COLOR_TARJETA = "#FFFFFF"
COLOR_INPUT_BG = "#F0F4F1"
COLOR_INPUT_BORDER = "#CCCCCC"
COLOR_NUEVO = "#1F6FEB"          # Azul profesional para la etiqueta NUEVO
COLOR_NUEVO_BORDE = "#1F6FEB"
COLOR_EDITAR = "#1D6F23"
COLOR_EDITAR_FONDO = "#EAF4EC"
COLOR_EDITAR_BORDE = "#A9D2B1"
COLOR_ELIMINAR = "#B03A2E"
COLOR_ELIMINAR_FONDO = "#FDEDEC"
COLOR_ELIMINAR_BORDE = "#E6B0AA"
COLOR_BORDE = "#E5E7EB"
COLOR_CARD = "#F9FAFB"
COLOR_TEXTO_SUAVE = "#6B7280"
COLOR_TEXTO = "#374151"
COLOR_TITULO = "#1F2937"

# Cada tipo de registro tiene su propio "cuerpo" visual: fondo tenue, borde
# y un acento que se usa en iconos, rieles y encabezados.
TONOS_TARJETA = {
    "verde": {
        "fondo": "#F6FAF7",
        "borde": "#E1EDE4",
        "acento": VERDE,
        "suave": "#EAF4EC",
    },
    "bronce": {
        "fondo": "#FBF8F3",
        "borde": "#EDE1D0",
        "acento": BRONCE,
        "suave": "#F6EEE3",
    },
    "azul": {
        "fondo": "#F5F9FC",
        "borde": "#DDE8F1",
        "acento": AZUL,
        "suave": "#EAF2F9",
    },
    "neutro": {
        "fondo": "#F8FAF9",
        "borde": "#E4E9E6",
        "acento": GRIS_OSCURO,
        "suave": "#EFF3F1",
    },
}

# Tiempo durante el cual un registro se considera "NUEVO"
HORAS_NUEVO = 24


def parse_fecha(valor):
    """Convierte datetime/date/str de PostgreSQL a datetime de Python."""
    if valor is None:
        return None
    if isinstance(valor, datetime):
        return valor
    if isinstance(valor, date):
        return datetime.combine(valor, time.min)

    texto = str(valor).strip()
    if not texto:
        return None

    try:
        return datetime.fromisoformat(texto)
    except ValueError:
        pass

    for formato in (
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d/%m/%Y",
    ):
        try:
            return datetime.strptime(texto, formato)
        except ValueError:
            continue
    return None


def formatear_fecha_hora(valor, incluir_hora=True):
    """Devuelve una fecha legible en formato mexicano (dd/mm/aaaa)."""
    fecha = parse_fecha(valor)
    if not fecha:
        return "—"
    if incluir_hora:
        return fecha.strftime("%d/%m/%Y · %H:%M")
    return fecha.strftime("%d/%m/%Y")


def es_reciente(valor, horas=HORAS_NUEVO):
    """Indica si la fecha de publicación está dentro de las últimas `horas`."""
    fecha = parse_fecha(valor)
    if not fecha:
        return False

    ahora = datetime.now(fecha.tzinfo) if fecha.tzinfo else datetime.now()
    diferencia = ahora - fecha
    return timedelta(0) <= diferencia <= timedelta(hours=horas)


def normalizar_texto(valor):
    """Convierte texto a minúsculas y elimina acentos para búsquedas amables."""
    texto = "" if valor is None else str(valor)
    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(caracter for caracter in texto if not unicodedata.combining(caracter))
    return texto.casefold().strip()


def coincide_busqueda(consulta, *valores):
    """Comprueba si la consulta aparece en cualquiera de los valores indicados."""
    consulta_normalizada = normalizar_texto(consulta)
    if not consulta_normalizada:
        return True
    return any(
        consulta_normalizada in normalizar_texto(valor)
        for valor in valores
        if valor is not None
    )


def fecha_coincide(valor_registro, filtro):
    """Compara la fecha de un registro con el texto escrito en un filtro.

    - Un filtro vacío acepta cualquier fecha.
    - Un filtro con formato inválido no coincide con ningún registro.
    """
    filtro = (filtro or "").strip()
    if not filtro:
        return True

    fecha_filtro = parse_fecha(filtro)
    fecha_registro = parse_fecha(valor_registro)
    if not fecha_filtro or not fecha_registro:
        return False
    return fecha_filtro.date() == fecha_registro.date()


def limpiar_entry(entry):
    """Vacía un CTkEntry y reactiva su placeholder si tiene uno.

    `CTkEntry.delete()` no siempre restaura el texto de ayuda cuando el campo
    conserva el foco; reconfigurar el mismo placeholder fuerza su reactivación.
    """
    entry.delete(0, "end")
    placeholder = entry.cget("placeholder_text")
    if placeholder:
        entry.configure(placeholder_text=placeholder)


def crear_badge(parent, texto, color=COLOR_NUEVO, text_color="white", ancho=None):
    """Etiqueta compacta y consistente para estados (NUEVO, tipo, categoría)."""
    if ancho is None:
        ancho = max(54, min(240, 20 + len(str(texto)) * 7))
    return ctk.CTkLabel(
        parent,
        text=texto,
        width=ancho,
        height=22,
        corner_radius=8,
        fg_color=color,
        text_color=text_color,
        font=fuente_etiqueta(9),
    )


def crear_boton_eliminar(parent, command):
    """Botón de eliminación discreto, solo visible para administradores."""
    return ctk.CTkButton(
        parent,
        text=" Eliminar",
        image=icono("trash-2", 14, COLOR_ELIMINAR),
        compound="left",
        width=100,
        height=28,
        corner_radius=8,
        fg_color="transparent",
        hover_color=COLOR_ELIMINAR_FONDO,
        border_width=0,
        border_color=COLOR_ELIMINAR_BORDE,
        text_color=COLOR_ELIMINAR,
        font=fuente_titulo(10),
        command=command,
    )


def crear_boton_editar(parent, command):
    """Botón de edición discreto, exclusivo del administrador."""
    return ctk.CTkButton(
        parent,
        text=" Editar",
        image=icono("square-pen", 14, COLOR_EDITAR),
        compound="left",
        width=100,
        height=28,
        corner_radius=8,
        fg_color="transparent",
        hover_color=COLOR_EDITAR_FONDO,
        border_width=0,
        border_color=COLOR_EDITAR_BORDE,
        text_color=COLOR_EDITAR,
        font=fuente_titulo(10),
        command=command,
    )


def crear_tarjeta_tinte(parent, tono="neutro", **kwargs):
    """Tarjeta con fondo tenue y borde propio según el tipo de registro."""
    paleta = TONOS_TARJETA.get(tono, TONOS_TARJETA["neutro"])
    kwargs.setdefault("fg_color", paleta["fondo"])
    kwargs.setdefault("corner_radius", 14)
    kwargs.setdefault("border_width", 1)
    kwargs.setdefault("border_color", paleta["borde"])
    return ctk.CTkFrame(parent, **kwargs)


def paleta_tarjeta(tono="neutro"):
    """Devuelve los colores de un tipo de tarjeta (fondo, borde, acento)."""
    return TONOS_TARJETA.get(tono, TONOS_TARJETA["neutro"])


def crear_riel_acento(parent, tono="verde", **kwargs):
    """Riel vertical de 3 px que identifica el tipo de registro."""
    paleta = paleta_tarjeta(tono)
    kwargs.setdefault("width", 3)
    kwargs.setdefault("height", 1)
    kwargs.setdefault("corner_radius", 2)
    kwargs.setdefault("fg_color", paleta["acento"])
    return ctk.CTkFrame(parent, **kwargs)


def crear_encabezado_icono(parent, nombre_icono, titulo, subtitulo=None, tono="verde"):
    """Encabezado con icono tintado, título y subtítulo opcional."""
    paleta = paleta_tarjeta(tono)
    contenedor = ctk.CTkFrame(parent, fg_color="transparent")

    fila = ctk.CTkFrame(contenedor, fg_color="transparent")
    fila.pack(fill="x")

    ctk.CTkLabel(
        fila,
        text="",
        image=icono(nombre_icono, 20, paleta["acento"]),
        width=24,
    ).pack(side="left", padx=(0, 8))

    ctk.CTkLabel(
        fila,
        text=titulo,
        font=fuente_titulo(16),
        text_color=COLOR_TITULO,
        anchor="w",
    ).pack(side="left")

    if subtitulo:
        ctk.CTkLabel(
            contenedor,
            text=subtitulo,
            font=fuente_etiqueta(10),
            text_color=COLOR_TEXTO_SUAVE,
            anchor="w",
        ).pack(fill="x", padx=(32, 0), pady=(1, 0))

    return contenedor
