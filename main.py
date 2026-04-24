import time
import sys
from core import DataLoader, ClienteManager
from interface import MenuInterface

def main():
    # 1. Instanciamos la Interfaz
    ui = MenuInterface()
    ruta_archivo = "clientes.csv"
    
    # 2. Inicialización Automática y Reporte de Carga (Tu código en core.py)
    loader = DataLoader(ruta_archivo)
    df_clientes = loader.cargar_datos()

    # Manejo de fallos: Si el DataFrame viene vacío y no hay válidos, abortamos limpio.
    if df_clientes.empty and loader.total_validos == 0:
        ui.mostrar_error("No se pudo iniciar el sistema. Verifique la existencia e integridad del archivo CSV.")
        sys.exit(0)

    # 3. Instanciamos tu lógica de negocio con los datos ya limpios
    manager = ClienteManager(df_clientes)

    # 4. Bucle Principal
    while True:
        opcion = ui.mostrar_menu()

        # Medición de latencia (Métrica de calidad: <= 500ms)
        inicio_consulta = time.time()

        try:
            if opcion == '1':
                cliente_id = ui.solicitar_id()
                resultado = manager.buscar_por_id(cliente_id)
                ui.mostrar_resultados(resultado)

            elif opcion == '2':
                ciudad = ui.solicitar_ciudad()
                resultado = manager.listar_por_ciudad(ciudad)
                ui.mostrar_resultados(resultado)

            elif opcion == '3':
                resultado = manager.ordenar_por_edad_y_nombre()
                ui.mostrar_resultados(resultado)

            elif opcion == '4':
                email = ui.solicitar_email()
                resultado = manager.buscar_por_email_parcial(email)
                ui.mostrar_resultados(resultado)

            elif opcion == '5':
                ui.mostrar_mensaje("Saliendo del sistema... ¡Buen trabajo, Quality Devs!")
                break
            else:
                ui.mostrar_error("Opción inválida. Por favor, seleccione un número del 1 al 5.")
                continue # Saltar la medición de tiempo si la opción es inválida
                
        except Exception as e:
            # Tolerancia a Fallos Global (RNF-02)
            ui.mostrar_error(f"Excepción no controlada durante la consulta: {e}")

        fin_consulta = time.time()
        latencia_ms = (fin_consulta - inicio_consulta) * 1000
        
        # Imprime la métrica de rendimiento directamente en consola
        if opcion in ['1', '2', '3', '4']:
            print(f"> Latencia de respuesta de la consulta: {latencia_ms:.2f} ms")

if __name__ == "__main__":
    main()