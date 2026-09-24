# 🅿️ Sistema de Control de Parqueadero

**Autor:** Camilo Andrés León Rubriche
**Institución:** Universidad Nacional Abierta y a Distancia — UNAD
**Curso:** Programación

> Sistema de gestión de parqueadero con interfaz gráfica, construido en Python con Programación Orientada a Objetos.

## Descripción

Sistema de gestión de parqueadero desarrollado en Python con Programación Orientada a Objetos. Registra el ingreso y salida de vehículos (carros y motos), calcula el tiempo de estancia y el valor a pagar según tarifa, y mantiene un histórico persistente en archivos JSON. Cuenta con interfaz gráfica construida en Tkinter, con pestañas para operaciones, vehículos activos, búsqueda/filtros, estadísticas e histórico de reportes.

## Capturas de pantalla

| Registrar ingreso / salida | Vehículos activos |
|---|---|
| ![Registrar ingreso y salida](docs/screenshots/01_registrar_ingreso.png) | ![Tabla de vehículos activos](docs/screenshots/02_vehiculos_activos.png) |

| Panel de estadísticas |
|---|
| ![Métricas del parqueadero](docs/screenshots/03_estadisticas.png) |

## Ejecución

```bash
python parqueadero.py
```

Requisitos: Python 3.10+ (usa únicamente la librería estándar — `tkinter`, `json`, `datetime`, `os`).

## Características

- Encapsulamiento de atributos privados en la clase `Vehiculo`
- Persistencia de datos activos e históricos en JSON (`vehiculos.json`, `historico.json`)
- Cálculo automático de tiempo de estancia y tarifa (carro/moto)
- Búsqueda por placa y filtrado por tipo de vehículo
- Panel de estadísticas (activos, históricos, ingresos totales y promedio)
- Generación de reportes del día
- Interfaz gráfica con tema claro/oscuro alternable

## Arquitectura

```
SistemaParqueadero/
│
├── parqueadero.py     # Aplicación completa: modelo, lógica y UI (Tkinter)
├── vehiculos.json      # Persistencia de vehículos activos (se genera en ejecución)
└── historico.json       # Histórico de ingresos/salidas (se genera en ejecución)
```

## Problema conocido

- El botón **"Tema Oscuro"** muestra el mensaje de confirmación "Tema oscuro activado", pero los widgets `ttk` (encabezados de tabla, pestañas) no cambian de color — solo se ve el efecto en algunos elementos. Es una limitación típica de mezclar `ttk` con estilos personalizados en Tkinter; vale la pena revisarlo si se quiere un tema oscuro completo y consistente.

## Tecnologías

- Python 3
- tkinter / ttk — interfaz gráfica
- json — persistencia de datos
- datetime — cálculo de tiempos de estancia
