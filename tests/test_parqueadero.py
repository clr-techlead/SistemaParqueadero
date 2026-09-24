"""
Pruebas unitarias para la lógica de negocio de Sistema de Control de Parqueadero.

No se prueba la interfaz gráfica (Tkinter) — solo las clases de dominio
Vehiculo y Parqueadero, que son las que concentran las reglas de negocio
(cálculo de tarifas, tiempos, filtros y estadísticas).
"""
from datetime import datetime, timedelta

import pytest

from parqueadero import Vehiculo, Parqueadero


# ---------------------------------------------------------------------
# Vehiculo
# ---------------------------------------------------------------------

class TestVehiculo:

    def test_calcular_tiempo_sin_salida_es_cero(self):
        entrada = datetime(2026, 1, 1, 10, 0, 0)
        v = Vehiculo("ABC123", "carro", entrada)
        assert v.calcular_tiempo() == 0

    def test_calcular_tiempo_en_minutos(self):
        entrada = datetime(2026, 1, 1, 10, 0, 0)
        salida = entrada + timedelta(minutes=45)
        v = Vehiculo("ABC123", "carro", entrada, salida)
        assert v.calcular_tiempo() == pytest.approx(45.0)

    @pytest.mark.parametrize("tipo,tarifa_minuto", [("carro", 120), ("moto", 70)])
    def test_calcular_pago_segun_tarifa_por_tipo(self, tipo, tarifa_minuto):
        entrada = datetime(2026, 1, 1, 10, 0, 0)
        salida = entrada + timedelta(minutes=10)
        v = Vehiculo("XYZ789", tipo, entrada, salida)
        assert v.calcular_pago() == round(10 * tarifa_minuto)

    def test_calcular_pago_tipo_desconocido_usa_tarifa_por_defecto(self):
        entrada = datetime(2026, 1, 1, 10, 0, 0)
        salida = entrada + timedelta(minutes=5)
        v = Vehiculo("BUS001", "bus", entrada, salida)
        assert v.calcular_pago() == round(5 * 100)

    def test_to_dict_incluye_placa_y_tipo(self):
        entrada = datetime(2026, 1, 1, 10, 0, 0)
        v = Vehiculo("ABC123", "carro", entrada)
        data = v.to_dict()
        assert data["placa"] == "ABC123"
        assert data["tipo"] == "carro"
        assert data["hora_salida"] is None

    def test_encapsulamiento_hora_entrada_es_privada(self):
        """El atributo de hora de entrada no debe ser accesible directamente
        con su nombre simple, solo a través del getter (name mangling)."""
        entrada = datetime(2026, 1, 1, 10, 0, 0)
        v = Vehiculo("ABC123", "carro", entrada)
        assert not hasattr(v, "__hora_entrada")
        assert v.get_hora_entrada() == entrada


# ---------------------------------------------------------------------
# Parqueadero
# ---------------------------------------------------------------------

class TestParqueadero:

    @pytest.fixture
    def parqueadero(self, tmp_path, monkeypatch):
        """Parqueadero aislado: guarda su JSON en un directorio temporal
        para no tocar los archivos reales del proyecto durante las pruebas."""
        monkeypatch.chdir(tmp_path)
        p = Parqueadero()
        return p

    def test_parqueadero_inicia_vacio(self, parqueadero):
        assert parqueadero.lista_vehiculos == []
        assert parqueadero.historico == []

    def test_validar_tipo_acepta_carro_y_moto(self, parqueadero):
        parqueadero.validar_tipo("carro")
        parqueadero.validar_tipo("moto")

    def test_validar_tipo_rechaza_tipo_invalido(self, parqueadero):
        with pytest.raises(ValueError):
            parqueadero.validar_tipo("bicicleta")

    def test_buscar_por_placa_encuentra_vehiculo_activo(self, parqueadero):
        v = Vehiculo("ABC123", "carro", datetime.now())
        parqueadero.lista_vehiculos.append(v)
        idx, encontrado = parqueadero._buscar_por_placa("ABC123")
        assert idx == 0
        assert encontrado is v

    def test_buscar_por_placa_no_encontrada_retorna_none(self, parqueadero):
        idx, encontrado = parqueadero._buscar_por_placa("NOEXISTE")
        assert idx is None
        assert encontrado is None

    def test_filtrar_por_tipo(self, parqueadero):
        parqueadero.lista_vehiculos.append(Vehiculo("A1", "carro", datetime.now()))
        parqueadero.lista_vehiculos.append(Vehiculo("A2", "moto", datetime.now()))
        parqueadero.lista_vehiculos.append(Vehiculo("A3", "carro", datetime.now()))
        carros = parqueadero.filtrar_por_tipo("carro")
        assert len(carros) == 2
        assert all(v.tipo == "carro" for v in carros)

    def test_obtener_estadisticas_cuenta_activos_por_tipo(self, parqueadero):
        parqueadero.lista_vehiculos.append(Vehiculo("A1", "carro", datetime.now()))
        parqueadero.lista_vehiculos.append(Vehiculo("A2", "moto", datetime.now()))
        stats = parqueadero.obtener_estadisticas()
        assert stats["total_activos"] == 2
        assert stats["carros_activos"] == 1
        assert stats["motos_activas"] == 1
