"""
=================================================================
  SISTEMA DE GESTION DE CLIENTES — Quality Devs UDLA
  Fase 5: Pruebas del Sistema
  Ejecutar con: pytest test_sistema.py -v -s
=================================================================
"""

import os
import tempfile
import time

import pandas as pd
import pytest

from core import ClienteManager, DataLoader

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────

CSV_REAL = os.path.join(os.path.dirname(os.path.abspath(__file__)), "clientes.csv")
TOTAL_VALIDOS   = 17
TOTAL_INVALIDOS = 3   # 2 filas marcadas "invalido" + 1 fila con email nulo
TIEMPO_MAX_MS   = 500


# ─────────────────────────────────────────────────────────────
# FIXTURES
# ─────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sistema():
    """Carga el CSV una sola vez y comparte loader, df y manager."""
    loader  = DataLoader(CSV_REAL)
    df      = loader.cargar_datos()
    manager = ClienteManager(df)
    return loader, df, manager


# ─────────────────────────────────────────────────────────────
# UTILIDADES DE SALIDA
# ─────────────────────────────────────────────────────────────

BAR = "=" * 68
SEP = "-" * 68


def encabezado(pr_id: str, funcionalidad: str, entrada: str) -> None:
    print(f"\n{BAR}")
    print(f"  {pr_id}  |  {funcionalidad}")
    print(SEP)
    print(f"  Entrada            : {entrada}")


def pie(esperado: str, obtenido: str, ok: bool) -> None:
    estado = "[APROBADO]" if ok else "[FALLIDO] ***"
    print(f"  Resultado esperado : {esperado}")
    print(f"  Resultado obtenido : {obtenido}")
    print(f"  Estado             : {estado}")
    print(BAR)


# =================================================================
# BLOQUE 1 — CARGA Y VALIDACION DE DATOS
# =================================================================

class TestCargaYValidacion:
    """PR-01 a PR-03: verifica lectura, limpieza y tolerancia a fallos."""

    def test_PR01_carga_exitosa_csv_valido(self, sistema):
        loader, df, _ = sistema
        encabezado(
            "PR-01",
            "Carga exitosa del CSV y limpieza de datos",
            CSV_REAL,
        )

        ok = (not df.empty
              and loader.total_validos   == TOTAL_VALIDOS
              and loader.total_invalidos == TOTAL_INVALIDOS)

        pie(
            f"DataFrame no vacio | validos={TOTAL_VALIDOS} | ignorados={TOTAL_INVALIDOS}",
            f"filas={len(df)} | validos={loader.total_validos} | ignorados={loader.total_invalidos}",
            ok,
        )

        assert not df.empty
        assert loader.total_validos   == TOTAL_VALIDOS
        assert loader.total_invalidos == TOTAL_INVALIDOS

    def test_PR02_archivo_csv_no_existe(self):
        ruta = "archivo_que_no_existe.csv"
        encabezado(
            "PR-02",
            "Manejo de error — archivo CSV inexistente",
            ruta,
        )

        loader = DataLoader(ruta)
        df     = loader.cargar_datos()

        ok = df.empty
        pie(
            "DataFrame vacio (sin excepcion no capturada)",
            f"vacio={df.empty}",
            ok,
        )
        assert df.empty

    def test_PR03_linea_con_edad_invalida(self):
        """Edad 'abc' no es numerica; el sistema no debe colapsar."""
        contenido_csv = (
            "id,nombre,email,ciudad,edad,estado\n"
            "1,Test Roto,roto@mail.com,Quito,abc,valido\n"
            "2,Test Valido,bien@mail.com,Quito,25,valido\n"
        )
        encabezado(
            "PR-03",
            "Manejo de error — edad invalida ('abc') en CSV",
            "CSV temporal con edad='abc' en fila 1",
        )

        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write(contenido_csv)
            tmp_path = tmp.name

        try:
            loader = DataLoader(tmp_path)
            df     = loader.cargar_datos()

            ok = not df.empty
            pie(
                "Sistema carga sin colapso; filas procesadas >= 1",
                f"vacio={df.empty} | filas={len(df)}",
                ok,
            )
            assert not df.empty
        finally:
            os.unlink(tmp_path)


# =================================================================
# BLOQUE 2 — BUSQUEDA POR ID  (RF-02)
# =================================================================

class TestBusquedaPorID:
    """PR-04 a PR-05: busqueda exacta numerica por ID."""

    def test_PR04_buscar_id_existente(self, sistema):
        _, _, manager = sistema
        encabezado("PR-04", "Busqueda por ID — ID existente", "cliente_id=1")

        resultado = manager.buscar_por_id(1)
        nombre    = resultado.iloc[0]["nombre"] if not resultado.empty else "N/A"
        ok        = len(resultado) == 1 and nombre == "Ana García"

        pie(
            "1 registro | nombre='Ana García'",
            f"registros={len(resultado)} | nombre={nombre}",
            ok,
        )
        assert len(resultado) == 1
        assert resultado.iloc[0]["nombre"] == "Ana García"

    def test_PR05_buscar_id_inexistente(self, sistema):
        _, _, manager = sistema
        encabezado("PR-05", "Busqueda por ID — ID que no existe", "cliente_id=9999")

        resultado = manager.buscar_por_id(9999)
        ok        = resultado.empty

        pie(
            "DataFrame vacio (0 resultados)",
            f"vacio={resultado.empty} | registros={len(resultado)}",
            ok,
        )
        assert resultado.empty


# =================================================================
# BLOQUE 3 — FILTRO POR CIUDAD  (RF-03)
# =================================================================

class TestListarPorCiudad:
    """PR-06 a PR-07: filtrado case-insensitive por ciudad."""

    def test_PR06_ciudad_existente_case_insensitive(self, sistema):
        _, _, manager = sistema
        encabezado(
            "PR-06",
            "Filtro por ciudad — case-insensitive",
            "ciudad='QUITO' (mayusculas)",
        )

        resultado = manager.listar_por_ciudad("QUITO")
        ciudades  = list(resultado["ciudad"].unique()) if not resultado.empty else []
        ok        = len(resultado) == 5

        pie(
            "5 registros validos de Quito",
            f"registros={len(resultado)} | ciudades encontradas={ciudades}",
            ok,
        )
        assert len(resultado) == 5
        assert all(c.lower() == "quito" for c in resultado["ciudad"])

    def test_PR07_ciudad_sin_coincidencias(self, sistema):
        _, _, manager = sistema
        encabezado("PR-07", "Filtro por ciudad — sin coincidencias", "ciudad='Loja'")

        resultado = manager.listar_por_ciudad("Loja")
        ok        = resultado.empty

        pie(
            "DataFrame vacio (0 registros)",
            f"vacio={resultado.empty} | registros={len(resultado)}",
            ok,
        )
        assert resultado.empty


# =================================================================
# BLOQUE 4 — ORDENAMIENTO POR EDAD Y NOMBRE  (RF-04)
# =================================================================

class TestOrdenamiento:
    """PR-08: ordenamiento compuesto ascendente edad+nombre."""

    def test_PR08_orden_ascendente_edad_y_nombre(self, sistema):
        _, _, manager = sistema
        encabezado(
            "PR-08",
            "Ordenamiento por edad (asc) y nombre (asc)",
            "todos los registros validos",
        )

        resultado = manager.ordenar_por_edad_y_nombre()
        edades    = list(resultado["edad"])
        en_orden  = edades == sorted(edades)
        primer_nombre = resultado.iloc[0]["nombre"]
        primer_edad   = resultado.iloc[0]["edad"]
        ok = en_orden and primer_edad == 19

        pie(
            "Edades ascendentes | primero: Sofia Torres (19)",
            f"orden_correcto={en_orden} | primer registro: {primer_nombre} edad={primer_edad}",
            ok,
        )
        assert en_orden
        assert primer_edad   == 19
        assert primer_nombre == "Sofía Torres"


# =================================================================
# BLOQUE 5 — BUSQUEDA POR EMAIL PARCIAL  (RF-05)
# =================================================================

class TestBusquedaPorEmail:
    """PR-09 a PR-10: busqueda parcial case-insensitive por email."""

    def test_PR09_email_parcial_existente(self, sistema):
        _, _, manager = sistema
        encabezado("PR-09", "Busqueda por email parcial — fragmento existente", "email='gmail'")

        resultado    = manager.buscar_por_email_parcial("gmail")
        todos_gmail  = all("gmail" in e.lower() for e in resultado["email"]) if not resultado.empty else False
        ok           = len(resultado) == 8 and todos_gmail

        pie(
            "8 registros con 'gmail' en email | todos contienen 'gmail'",
            f"registros={len(resultado)} | todos_gmail={todos_gmail}",
            ok,
        )
        assert not resultado.empty
        assert len(resultado) == 8
        assert todos_gmail

    def test_PR10_email_parcial_sin_coincidencias(self, sistema):
        _, _, manager = sistema
        encabezado("PR-10", "Busqueda por email parcial — sin coincidencias", "email='zzzzzz'")

        resultado = manager.buscar_por_email_parcial("zzzzzz")
        ok        = resultado.empty

        pie(
            "DataFrame vacio (0 registros)",
            f"vacio={resultado.empty} | registros={len(resultado)}",
            ok,
        )
        assert resultado.empty


# =================================================================
# BLOQUE 6 — RENDIMIENTO
# =================================================================

class TestRendimiento:
    """PR-11 a PR-12: tiempo de respuesta < 500 ms."""

    def test_PR11_tiempo_busqueda_por_id(self, sistema):
        _, _, manager = sistema
        encabezado(
            "PR-11",
            "Tiempo de respuesta — busqueda por ID",
            f"cliente_id=1 | umbral <= {TIEMPO_MAX_MS} ms",
        )

        inicio = time.perf_counter()
        manager.buscar_por_id(1)
        ms = (time.perf_counter() - inicio) * 1000

        ok = ms < TIEMPO_MAX_MS
        pie(
            f"Tiempo < {TIEMPO_MAX_MS} ms",
            f"Tiempo medido = {ms:.4f} ms",
            ok,
        )
        assert ms < TIEMPO_MAX_MS, f"Tiempo excedido: {ms:.4f} ms"

    def test_PR12_tiempo_ordenamiento_completo(self, sistema):
        _, _, manager = sistema
        encabezado(
            "PR-12",
            "Tiempo de respuesta — ordenamiento completo",
            f"todos los registros | umbral <= {TIEMPO_MAX_MS} ms",
        )

        inicio = time.perf_counter()
        manager.ordenar_por_edad_y_nombre()
        ms = (time.perf_counter() - inicio) * 1000

        ok = ms < TIEMPO_MAX_MS
        pie(
            f"Tiempo < {TIEMPO_MAX_MS} ms",
            f"Tiempo medido = {ms:.4f} ms",
            ok,
        )
        assert ms < TIEMPO_MAX_MS, f"Tiempo excedido: {ms:.4f} ms"
