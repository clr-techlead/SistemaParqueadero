🌐 English | [Versión en español](README.es.md)

# 🅿️ Parking Lot Management System

![Tests](https://github.com/clr-techlead/SistemaParqueadero/actions/workflows/tests.yml/badge.svg)
![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)

**Author:** Camilo Andrés León Rubriche
**Institution:** Universidad Nacional Abierta y a Distancia — UNAD
**Course:** Programming

> Parking lot management system with a graphical interface, built in Python with Object-Oriented Programming.

## Overview

A parking lot management system developed in Python with Object-Oriented Programming. It logs vehicle check-in/check-out (cars and motorcycles), calculates the time parked and the fee owed, and keeps a persistent history in JSON files. It includes a Tkinter GUI with tabs for operations, active vehicles, search/filters, statistics, and report history.

## Screenshots

| Check-in / check-out | Active vehicles |
|---|---|
| ![Check-in and check-out](docs/screenshots/01_registrar_ingreso.png) | ![Active vehicles table](docs/screenshots/02_vehiculos_activos.png) |

| Statistics panel |
|---|
| ![Parking lot metrics](docs/screenshots/03_estadisticas.png) |

## Running it

```bash
python parqueadero.py
```

Requirements: Python 3.10+ (uses only the standard library — `tkinter`, `json`, `datetime`, `os`).

## Tests

```bash
pip install -r requirements.txt
pytest tests/ -v
```

14 unit tests cover the business logic (time and fee calculation, encapsulation, search/filtering, and statistics) of the `Vehiculo` and `Parqueadero` classes. They run automatically on every push via GitHub Actions (see badge above).

## Features

- Encapsulated private attributes in the `Vehiculo` class
- Persistence of active and historical data in JSON (`vehiculos.json`, `historico.json`)
- Automatic calculation of parking time and fee (car/motorcycle)
- Search by plate and filtering by vehicle type
- Statistics panel (active, historical, total and average revenue)
- Daily report generation
- GUI with a switchable light/dark theme

## Architecture

```
SistemaParqueadero/
│
├── parqueadero.py            # Full application: model, logic, and UI (Tkinter)
├── tests/
│   └── test_parqueadero.py    # Unit tests (pytest)
├── .github/workflows/
│   └── tests.yml               # CI: runs the tests on every push
├── requirements.txt
├── LICENSE
├── vehiculos.json              # Active vehicles persistence (generated at runtime)
└── historico.json              # Check-in/check-out history (generated at runtime)
```

## Known Issue

- The **"Tema Oscuro" (Dark Theme)** button shows the confirmation message "Tema oscuro activado" ("Dark theme enabled"), but the `ttk` widgets (table headers, tabs) don't actually change color — the effect is only visible on some elements. This is a typical limitation of mixing `ttk` with custom styling in Tkinter; worth revisiting for a fully consistent dark theme.

## Technologies

- Python 3
- tkinter / ttk — GUI
- json — data persistence
- datetime — parking time calculation
