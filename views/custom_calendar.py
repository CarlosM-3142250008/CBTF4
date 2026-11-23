import calendar
from datetime import datetime, date, timedelta
import customtkinter as ctk

from views.typography import (
    fuente,
    fuente_dato,
    fuente_display,
    fuente_etiqueta,
)

class CustomCalendar(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, fg_color="transparent", **kwargs)
        
        self.selected_date = datetime.now()
        
        # Contenedor principal del calendario
        self.main_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=14, border_width=0, border_color="#D0D0D0")
        self.main_frame.pack(fill="both", expand=True, padx=2, pady=2)
        
        self.render_calendar()

    def mes_anterior(self):
        """Retrocede un mes en el calendario."""
        primer_dia = self.selected_date.replace(day=1)
        mes_previo = primer_dia - timedelta(days=1)
        self.selected_date = self.selected_date.replace(year=mes_previo.year, month=mes_previo.month, day=1)
        self.render_calendar()

    def mes_siguiente(self):
        """Avanza un mes en el calendario."""
        _, dias_en_mes = calendar.monthrange(self.selected_date.year, self.selected_date.month)
        ultimo_dia = self.selected_date.replace(day=dias_en_mes)
        mes_sig = ultimo_dia + timedelta(days=1)
        self.selected_date = self.selected_date.replace(year=mes_sig.year, month=mes_sig.month, day=1)
        self.render_calendar()

    def render_calendar(self):
        # Limpiar botones anteriores
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        # Encabezado con botones de navegación (◀ Mes Año ▶)
        header_frame = ctk.CTkFrame(self.main_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=7, pady=(10, 5), sticky="ew")
        header_frame.grid_columnconfigure(1, weight=1)

        btn_prev = ctk.CTkButton(
            header_frame, text="◀", width=32, height=26,
            fg_color="#F0F0F0", text_color="#1D6F23", hover_color="#E0E0E0",
            font=fuente(12, "bold"), command=self.mes_anterior
        )
        btn_prev.grid(row=0, column=0, padx=5)

        month_name = self.selected_date.strftime("%B").capitalize()
        year_str = self.selected_date.strftime("%Y")
        lbl_header = ctk.CTkLabel(
            header_frame, text=f"{month_name} {year_str}",
            font=fuente_display(15, "bold"), text_color="#333333"
        )
        lbl_header.grid(row=0, column=1)

        btn_next = ctk.CTkButton(
            header_frame, text="▶", width=32, height=26,
            fg_color="#F0F0F0", text_color="#1D6F23", hover_color="#E0E0E0",
            font=fuente(12, "bold"), command=self.mes_siguiente
        )
        btn_next.grid(row=0, column=2, padx=5)

        # Encabezado de los días de la semana
        days = ["Lu", "Ma", "Mi", "Ju", "Vi", "Sá", "Do"]
        for i, day in enumerate(days):
            lbl_day = ctk.CTkLabel(self.main_frame, text=day.upper(), font=fuente_etiqueta(8), text_color="#888888")
            lbl_day.grid(row=1, column=i, pady=5)

        # Matriz de días del mes
        first_day_of_month = self.selected_date.replace(day=1)
        start_weekday = first_day_of_month.weekday()
        _, days_in_month = calendar.monthrange(self.selected_date.year, self.selected_date.month)

        for row in range(6):
            for col in range(7):
                day_num = (row * 7) + col - start_weekday + 1
                if 1 <= day_num <= days_in_month:
                    is_today = (day_num == datetime.now().day and 
                                self.selected_date.month == datetime.now().month and 
                                self.selected_date.year == datetime.now().year)
                    is_selected = (day_num == self.selected_date.day)

                    if is_selected:
                        color_fondo, color_hover, color_texto = "#1D6F23", "#15531A", "white"
                    elif is_today:
                        color_fondo, color_hover, color_texto = "#E0E0E0", "#CFD8D2", "#1D6F23"
                    else:
                        color_fondo, color_hover, color_texto = "white", "#EEF4F0", "black"

                    btn = ctk.CTkButton(
                        self.main_frame,
                        text=str(day_num),
                        width=34,
                        height=32,
                        corner_radius=8,
                        border_width=0,
                        fg_color=color_fondo,
                        hover_color=color_hover,
                        text_color=color_texto,
                        font=fuente_dato(11, "bold") if (is_today or is_selected) else fuente_dato(11)
                    )
                    btn.grid(row=row+2, column=col, padx=2, pady=2)
                    btn.bind("<Button-1>", lambda e, d=day_num: self.select_date(d))

    def select_date(self, value):
        if isinstance(value, date) and not isinstance(value, datetime):
            self.selected_date = datetime.combine(value, datetime.min.time())
        elif isinstance(value, int):
            try:
                self.selected_date = self.selected_date.replace(day=value)
            except ValueError:
                _, last_day = calendar.monthrange(self.selected_date.year, self.selected_date.month)
                self.selected_date = self.selected_date.replace(day=last_day)
        else:
            if isinstance(value, datetime):
                self.selected_date = value
            else:
                self.selected_date = datetime.now()
                    
        self.render_calendar()

    def get_date_str(self):
        return self.selected_date.strftime("%Y-%m-%d")

    def get_date(self):
        return self.selected_date