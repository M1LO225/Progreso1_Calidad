import tkinter as tk
from tkinter import messagebox, scrolledtext
import pandas as pd
from typing import Union

class MenuInterface:
    def __init__(self, root, manager_callback):
        self.root = root
        self.manager = manager_callback
        self.root.title("Quality Devs UDLA - Gestión de Clientes")
        self.root.geometry("800x600")
        self.root.configure(bg="#f0f0f0")
        
        self._setup_ui()

    def _setup_ui(self):
        # Título Principal
        header = tk.Label(self.root, text="SISTEMA DE GESTIÓN DE CLIENTES", 
                         font=("Arial", 18, "bold"), bg="#2c3e50", fg="white", pady=10)
        header.pack(fill="x")

        # Frame de Entrada de Datos
        input_frame = tk.Frame(self.root, bg="#f0f0f0", pady=10)
        input_frame.pack()

        tk.Label(input_frame, text="Valor de búsqueda:", font=("Arial", 10), bg="#f0f0f0").grid(row=0, column=0, padx=5)
        self.entry_busqueda = tk.Entry(input_frame, width=40, font=("Arial", 10))
        self.entry_busqueda.grid(row=0, column=1, padx=5)

        # Frame de Botones (Requerimientos RF-02 a RF-05)
        btn_frame = tk.Frame(self.root, bg="#f0f0f0")
        btn_frame.pack(pady=10)

        style = {"width": 20, "font": ("Arial", 9, "bold"), "cursor": "hand2"}
        
        tk.Button(btn_frame, text="Buscar por ID (RF-02)", command=self._buscar_id, **style).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Listar por Ciudad (RF-03)", command=self._buscar_ciudad, **style).grid(row=0, column=1, padx=5, pady=5)
        tk.Button(btn_frame, text="Ordenar por Edad (RF-04)", command=self._ordenar_edad, **style).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Buscar Email (RF-05)", command=self._buscar_email, **style).grid(row=1, column=1, padx=5, pady=5)

        # Área de Resultados (ScrolledText para soportar muchos datos)
        tk.Label(self.root, text="Resultados de la consulta:", font=("Arial", 10, "italic"), bg="#f0f0f0").pack(anchor="w", padx=25)
        self.txt_output = scrolledtext.ScrolledText(self.root, width=90, height=20, font=("Courier New", 10))
        self.txt_output.pack(pady=5, padx=20)

    def mostrar_reporte_inicial(self, validos: int, invalidos: int):
        """Cumple con RF-06: Reporte de carga al arrancar."""
        messagebox.showinfo("Reporte de Carga CSV", 
                            f"Carga finalizada con éxito:\n\n"
                            f"Registros Válidos: {validos}\n"
                            f"Registros Inválidos: {invalidos}")

    def _renderizar_tabla(self, df: Union[pd.DataFrame, None]):
        """Limpia el área de texto y muestra el DataFrame de forma legible."""
        self.txt_output.delete("1.0", tk.END)
        if df is None or df.empty:
            self.txt_output.insert(tk.END, ">>> No se encontraron resultados para la consulta.")
        else:
            self.txt_output.insert(tk.END, df.to_string(index=False))

    # --- Handlers de Eventos ---

    def _buscar_id(self):
        try:
            val = int(self.entry_busqueda.get().strip())
            res = self.manager.buscar_por_id(val)
            self._renderizar_tabla(res)
        except ValueError:
            messagebox.showerror("Error de Tipo", "El ID debe ser un número entero (RF-02).")

    def _buscar_ciudad(self):
        val = self.entry_busqueda.get().strip()
        if not val:
            messagebox.showwarning("Atención", "Por favor ingrese una ciudad.")
            return
        res = self.manager.listar_por_ciudad(val)
        self._renderizar_tabla(res)

    def _ordenar_edad(self):
        res = self.manager.ordenar_por_edad()
        self._renderizar_tabla(res)

    def _buscar_email(self):
        val = self.entry_busqueda.get().strip()
        res = self.manager.buscar_por_email(val)
        self._renderizar_tabla(res )
        