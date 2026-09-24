# Sistema de Control de Parqueadero

**Autor:** Camilo Andrés León Rubriche
**Institución:** Universidad Nacional Abierta y a Distancia — UNAD
**Curso:** Programación

## Descripción

Sistema de gestión de parqueadero desarrollado en Python con Programación Orientada a Objetos. Registra el ingreso y salida de vehículos (carros y motos), calcula el tiempo de estancia y el valor a pagar según tarifa, y mantiene un histórico persistente en archivos JSON. Cuenta con interfaz gráfica construida en Tkinter, con pestañas para operaciones, vehículos activos, búsqueda/filtros, estadísticas e histórico de reportes.

## Ejecución

```bash
python parqueadero.py
```

## Características

- Encapsulamiento de atributos privados en la clase `Vehiculo`
- Persistencia de datos activos e históricos en JSON (`vehiculos.json`, `historico.json`)
- Cálculo automático de tiempo de estancia y tarifa (carro/moto)
- Búsqueda por placa y filtrado por tipo de vehículo
- Panel de estadísticas (activos, históricos, ingresos totales y promedio)
- Generación de reportes del día
- Interfaz gráfica con tema claro/oscuro alternable
