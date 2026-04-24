import sys
import tkinter as tk
from tkinter import messagebox
from core import DataLoader, ClienteManager
from interface import MenuInterface

def main():
    ruta_archivo = "clientes.csv"

    loader = DataLoader(ruta_archivo)
    df_clientes = loader.cargar_datos()

    if df_clientes.empty and loader.total_validos == 0:
        root_err = tk.Tk()
        root_err.withdraw()
        messagebox.showerror(
            "Error Crítico",
            "No se pudo iniciar el sistema. "
            "Verifique la existencia e integridad del archivo CSV."
        )
        root_err.destroy()
        sys.exit(0)

    manager = ClienteManager(df_clientes)

    root = tk.Tk()
    app = MenuInterface(root, manager)
    app.mostrar_reporte_inicial(loader.total_validos, loader.total_invalidos)
    root.mainloop()

if __name__ == "__main__":
    main()
