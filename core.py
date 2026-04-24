import pandas as pd
import os

class DataLoader:
    """
    Responsable de la persistencia volátil y gestión de archivos (RF-01, RF-06).
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.total_validos = 0
        self.total_invalidos = 0

    def cargar_datos(self) -> pd.DataFrame:
        """
        Lee el CSV, filtra datos inválidos y genera el reporte de carga.
        Implementa tolerancia a fallos (RNF-02).
        """
        try:
            if not os.path.exists(self.file_path):
                raise FileNotFoundError(f"El archivo {self.file_path} no existe.")

            # Lectura del CSV con Pandas
            df = pd.read_csv(self.file_path)
            
            # Conteo inicial para el reporte (RF-06)
            total_filas = len(df)

            # Limpieza de datos (RF-01):
            # 1. Eliminar filas con valores nulos (dropna)
            # 2. Filtrar la "columna extra" eliminando los que digan "invalido"
            # Se asume que la última columna es la "columna extra" según el cliente
            columna_extra = df.columns[-1]
            
            # Filtramos: mantenemos lo que NO es nulo y NO dice "invalido"
            df_limpio = df.dropna().copy()
            df_limpio = df_limpio[df_limpio[columna_extra].astype(str).str.lower() != "invalido"]

            self.total_validos = len(df_limpio)
            self.total_invalidos = total_filas - self.total_validos

            # Imprimir reporte inmediato (RF-06 / Criterio de Aceptación)
            print("-" * 30)
            print("REPORTE DE ESTADO DE CARGA")
            print(f"Total Válidos: {self.total_validos}")
            print(f"Total con Errores/Ignorados: {self.total_invalidos}")
            print("-" * 30)

            return df_limpio

        except FileNotFoundError as e:
            print(f"Error Crítico: {e}")
            return pd.DataFrame() # Retorna DF vacío para evitar crash
        except Exception as e:
            print(f"Error inesperado al cargar el CSV: {e}")
            return pd.DataFrame()

class ClienteManager:
    """
    Núcleo de la lógica de negocio (RF-02 al RF-05).
    Opera sobre DataFrames para garantizar alto rendimiento.
    """
    def __init__(self, dataframe: pd.DataFrame):
        self.df = dataframe

    def buscar_por_id(self, cliente_id: int) -> pd.DataFrame:
        """Búsqueda exacta numérica por ID (RF-02)."""
        # Aseguramos búsqueda exacta tras limpiar espacios (trim implícito en cast a int)
        resultado = self.df[self.df['id'] == cliente_id]
        return resultado

    def listar_por_ciudad(self, ciudad: str) -> pd.DataFrame:
        """Filtrado case-insensitive por ciudad (RF-03)."""
        # str.lower() permite que "quito" == "Quito"
        resultado = self.df[self.df['ciudad'].str.lower() == ciudad.lower().strip()]
        return resultado

    def ordenar_por_edad_y_nombre(self) -> pd.DataFrame:
        """
        Ordenamiento compuesto: Edad (asc) y Nombre (asc) como desempate (RF-04).
        """
        # El cliente solicitó orden alfabético por nombre en caso de empate de edad
        return self.df.sort_values(by=['edad', 'nombre'], ascending=[True, True])

    def buscar_por_email_parcial(self, email_busqueda: str) -> pd.DataFrame:
        """Búsqueda parcial por email usando coincidencia de cadena (RF-05)."""
        # Se eliminan espacios accidentales (trim) antes de la búsqueda
        busqueda = email_busqueda.strip()
        resultado = self.df[self.df['email'].str.contains(busqueda, case=False, na=False)]
        return resultado