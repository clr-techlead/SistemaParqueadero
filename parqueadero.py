# ---------------------------------------------------------
# Control de Parqueadero - Version Mejorada
# Curso: Programacion
# Autor: Camilo Andres Leon Rubriche
# ---------------------------------------------------------

from datetime import datetime
import json
import os
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext


class Vehiculo:

    def __init__(self, placa, tipo, hora_entrada, hora_salida=None):
        self.placa = placa
        self.tipo = tipo
        self.__hora_entrada = hora_entrada
        self.__hora_salida = hora_salida

    def registrar_salida(self, hora_salida):
        self.__hora_salida = hora_salida

    def calcular_tiempo(self):
        if self.__hora_salida is None:
            return 0

        diferencia = self.__hora_salida - self.__hora_entrada
        return diferencia.total_seconds() / 60

    def calcular_pago(self):
        minutos = self.calcular_tiempo()

        tarifas = {
            "carro": 120,
            "moto": 70
        }

        tarifa = tarifas.get(self.tipo, 100)

        return round(minutos * tarifa)

    def mostrar_resumen(self):
        print("\n----- RESUMEN DEL SERVICIO -----")
        print("Placa:", self.placa)
        print("Tipo:", self.tipo)
        print("Tiempo:", int(self.calcular_tiempo()), "min")
        print("Total: $", self.calcular_pago())

    def to_dict(self):
        """Para guardar en archivo"""
        return {
            "placa": self.placa,
            "tipo": self.tipo,
            "hora_entrada": self.__hora_entrada.strftime("%Y-%m-%d %H:%M:%S"),
            "hora_salida": self.__hora_salida.strftime("%Y-%m-%d %H:%M:%S") if self.__hora_salida else None
        }
    
    def get_hora_entrada(self):
        return self.__hora_entrada
    
    def get_hora_salida(self):
        return self.__hora_salida


class Parqueadero:

    def __init__(self):
        self.lista_vehiculos = []
        self.historico = []
        self.archivo = "vehiculos.json"
        self.archivo_historico = "historico.json"
        self.cargar_datos()

    def _buscar_por_placa(self, placa):
        for idx, vehiculo in enumerate(self.lista_vehiculos):
            if vehiculo.placa == placa:
                return idx, vehiculo
        return None, None

    def validar_tipo(self, tipo):
        tipos_validos = ["carro", "moto"]
        if tipo not in tipos_validos:
            raise ValueError("Tipo de vehículo inválido")

    def registrar_ingreso(self):
        try:
            placa = input("Placa: ").strip().upper()
            tipo = input("Tipo (carro/moto): ").strip().lower()

            if not placa:
                raise ValueError("Placa inválida")

            self.validar_tipo(tipo)

            _, existente = self._buscar_por_placa(placa)
            if existente:
                print("Vehículo ya registrado")
                return

            vehiculo = Vehiculo(placa, tipo, datetime.now())
            self.lista_vehiculos.append(vehiculo)

            self.guardar_datos()

            print("Ingreso exitoso")

        except ValueError as e:
            print("Error:", e)

    def registrar_salida(self):
        try:
            placa = input("Placa: ").strip().upper()

            idx, vehiculo = self._buscar_por_placa(placa)

            if vehiculo is None:
                raise ValueError("Vehículo no encontrado")

            vehiculo.registrar_salida(datetime.now())
            vehiculo.mostrar_resumen()

            del self.lista_vehiculos[idx]

            self.guardar_datos()

        except ValueError as e:
            print("Error:", e)

    def mostrar_vehiculos(self):
        if not self.lista_vehiculos:
            print("No hay vehículos")
            return

        print("\nVehículos activos:")
        for v in self.lista_vehiculos:
            print(f"{v.placa} - {v.tipo}")

    def filtrar_por_tipo(self, tipo):
        """Filtrar vehículos activos por tipo"""
        return [v for v in self.lista_vehiculos if v.tipo == tipo]
    
    def obtener_estadisticas(self):
        """Obtener estadísticas del parqueadero"""
        total_activos = len(self.lista_vehiculos)
        carros_activos = len([v for v in self.lista_vehiculos if v.tipo == "carro"])
        motos_activas = len([v for v in self.lista_vehiculos if v.tipo == "moto"])
        
        historico_completado = [v for v in self.historico if v.get_hora_salida()]
        ingresos_totales = sum(v.calcular_pago() for v in historico_completado)
        
        stats = {
            "total_activos": total_activos,
            "carros_activos": carros_activos,
            "motos_activas": motos_activas,
            "total_historico": len(historico_completado),
            "ingresos_totales": ingresos_totales
        }
        
        if historico_completado:
            stats["ingreso_promedio"] = ingresos_totales / len(historico_completado)
            stats["tiempo_promedio"] = sum(v.calcular_tiempo() for v in historico_completado) / len(historico_completado)
        
        return stats

    # ------------------------------
    # Persistencia
    # ------------------------------

    def guardar_datos(self):
        datos = [v.to_dict() for v in self.lista_vehiculos]

        with open(self.archivo, "w") as f:
            json.dump(datos, f, indent=4)

    def cargar_datos(self):
        if not os.path.exists(self.archivo):
            return

        with open(self.archivo, "r") as f:
            datos = json.load(f)

            for item in datos:
                hora = datetime.strptime(item["hora_entrada"], "%Y-%m-%d %H:%M:%S")
                vehiculo = Vehiculo(item["placa"], item["tipo"], hora)
                self.lista_vehiculos.append(vehiculo)
        
        self.cargar_historico()
    
    def guardar_historico(self, vehiculo):
        """Guardar un vehículo en el histórico cuando sale"""
        self.historico.append(vehiculo)
        
        datos = [v.to_dict() for v in self.historico]
        with open(self.archivo_historico, "w") as f:
            json.dump(datos, f, indent=4)
    
    def cargar_historico(self):
        """Cargar histórico completo de vehículos"""
        if not os.path.exists(self.archivo_historico):
            return

        with open(self.archivo_historico, "r") as f:
            datos = json.load(f)

            for item in datos:
                hora_entrada = datetime.strptime(item["hora_entrada"], "%Y-%m-%d %H:%M:%S")
                hora_salida = None
                if item.get("hora_salida"):
                    hora_salida = datetime.strptime(item["hora_salida"], "%Y-%m-%d %H:%M:%S")
                
                vehiculo = Vehiculo(item["placa"], item["tipo"], hora_entrada, hora_salida)
                self.historico.append(vehiculo)


# ---------------------------------------------------------
# Menu - Interfaz Gráfica con Tkinter (Premium Design)
# ---------------------------------------------------------

class InterfazParqueadero:
    
    # Paleta de colores moderna - TEMA CLARO
    COLOR_PRINCIPAL = "#1a1a2e"      # Azul profundo
    COLOR_SECUNDARIO = "#16213e"     # Azul oscuro
    COLOR_ACENTO1 = "#0f3460"        # Azul claro
    COLOR_ACENTO2 = "#e94560"        # Rojo/Rosa
    COLOR_EXITO = "#00d084"          # Verde éxito
    COLOR_ADVERTENCIA = "#ffa502"    # Naranja
    COLOR_FONDO = "#f5f7fa"          # Gris claro
    COLOR_TEXTO = "#2c3e50"          # Gris texto
    COLOR_BORDE = "#d0d0d0"          # Gris borde
    
    # Colores para tema oscuro
    COLOR_PRINCIPAL_DARK = "#0f0f1e"
    COLOR_FONDO_DARK = "#1a1a2e"
    COLOR_CARD_DARK = "#16213e"
    COLOR_TEXTO_DARK = "#e0e0e0"
    
    def __init__(self, root):
        self.parqueadero = Parqueadero()
        self.root = root
        self.root.title("🅿️  SISTEMA DE PARQUEADERO PREMIUM")
        self.root.geometry("1100x850")
        self.root.minsize(900, 700)
        
        # Control de tema
        self.tema_oscuro = False
        
        # Configurar estilo global
        self.root.configure(bg=self.COLOR_FONDO)
        
        # Configurar estilos ttk
        self.configurar_estilos()
        
        self.crear_widgets()
        self.actualizar_estadisticas()
    
    def configurar_estilos(self):
        """Configurar estilos modernos para ttk"""
        style = ttk.Style()
        
        # Tema general
        style.theme_use('clam')
        
        # Estilo para Notebook (pestañas)
        style.configure(
            'TNotebook',
            background=self.COLOR_FONDO,
            borderwidth=0
        )
        style.configure(
            'TNotebook.Tab',
            padding=[20, 15],
            font=("Segoe UI", 11, "bold")
        )
        style.map(
            'TNotebook.Tab',
            background=[("selected", self.COLOR_ACENTO1)],
            foreground=[("selected", "white")],
            relief=[("selected", "flat")]
        )
        
        # Estilo para LabelFrame
        style.configure(
            'TLabelframe',
            background=self.COLOR_FONDO,
            borderwidth=1,
            relief="solid"
        )
        style.configure(
            'TLabelframe.Label',
            background=self.COLOR_FONDO,
            foreground=self.COLOR_TEXTO,
            font=("Segoe UI", 10, "bold")
        )
        
        # Estilo para botones
        style.configure(
            'TButton',
            font=("Segoe UI", 10, "bold"),
            padding=[15, 10],
            relief="flat",
            borderwidth=0
        )
        style.map(
            'TButton',
            background=[
                ("active", self.COLOR_ACENTO2),
                ("!active", self.COLOR_ACENTO1)
            ],
            foreground=[("active", "white"), ("!active", "white")]
        )
        
        # Estilo para Entry
        style.configure(
            'TEntry',
            font=("Segoe UI", 10),
            padding=8,
            relief="solid",
            borderwidth=1
        )
        
        # Estilo para Combobox
        style.configure(
            'TCombobox',
            font=("Segoe UI", 10),
            padding=8,
            relief="solid",
            borderwidth=1
        )
        
        # Estilo para Label
        style.configure(
            'TLabel',
            background=self.COLOR_FONDO,
            foreground=self.COLOR_TEXTO,
            font=("Segoe UI", 10)
        )
    
    def crear_widgets(self):
        """Crear widgets con diseño premium"""
        
        # ====== HEADER PREMIUM ======
        header = tk.Frame(self.root, bg=self.COLOR_PRINCIPAL, height=100)
        header.pack(fill=tk.X, side=tk.TOP)
        header.pack_propagate(False)
        
        # Contenedor del header
        header_content = tk.Frame(header, bg=self.COLOR_PRINCIPAL)
        header_content.pack(fill=tk.BOTH, expand=True, padx=30, pady=15)
        
        # Frame de título y botón tema
        titulo_frame = tk.Frame(header_content, bg=self.COLOR_PRINCIPAL)
        titulo_frame.pack(fill=tk.X, expand=True)
        
        # Título principal
        titulo = tk.Label(
            titulo_frame,
            text="🅿️  SISTEMA DE CONTROL DE PARQUEADERO",
            font=("Segoe UI", 26, "bold"),
            bg=self.COLOR_PRINCIPAL,
            fg="white"
        )
        titulo.pack(anchor=tk.W, side=tk.LEFT, pady=(0, 5))
        
        # Botón para cambiar tema
        self.btn_tema = tk.Button(
            titulo_frame,
            text="🌙 Tema Oscuro",
            font=("Segoe UI", 10, "bold"),
            bg=self.COLOR_ACENTO1,
            fg="white",
            activebackground=self.COLOR_ACENTO2,
            activeforeground="white",
            relief=tk.FLAT,
            bd=0,
            padx=15,
            pady=8,
            cursor="hand2",
            command=self.alternar_tema
        )
        self.btn_tema.pack(anchor=tk.E, side=tk.RIGHT)
        
        # Subtítulo
        subtitulo = tk.Label(
            header_content,
            text="Gestión inteligente de estacionamientos | Premium Edition",
            font=("Segoe UI", 10),
            bg=self.COLOR_PRINCIPAL,
            fg="#b0c4de"
        )
        subtitulo.pack(anchor=tk.W, pady=(5, 0))
        
        # Separador animado
        self.separador = tk.Frame(self.root, bg=self.COLOR_ACENTO1, height=4)
        self.separador.pack(fill=tk.X)
        
        # Crear Notebook (pestañas)
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=15, pady=15)
        
        # Crear pestañas
        self.crear_tab_operaciones()
        self.crear_tab_activos()
        self.crear_tab_busqueda()
        self.crear_tab_estadisticas()
        self.crear_tab_historico()
    
    def alternar_tema(self):
        """Cambiar entre tema claro y oscuro con animación"""
        self.tema_oscuro = not self.tema_oscuro
        
        if self.tema_oscuro:
            # Cambiar a tema oscuro
            color_fondo = self.COLOR_FONDO_DARK
            color_principal = self.COLOR_PRINCIPAL_DARK
            color_texto = self.COLOR_TEXTO_DARK
            btn_texto = "☀️ Tema Claro"
        else:
            # Cambiar a tema claro
            color_fondo = self.COLOR_FONDO
            color_principal = self.COLOR_PRINCIPAL
            color_texto = self.COLOR_TEXTO
            btn_texto = "🌙 Tema Oscuro"
        
        # Actualizar colores del root y frames
        self.root.configure(bg=color_fondo)
        
        # Encontrar el header y actualizarlo
        for widget in self.root.winfo_children():
            if isinstance(widget, tk.Frame) and widget.cget('bg') == (self.COLOR_PRINCIPAL if not self.tema_oscuro else self.COLOR_FONDO_DARK):
                widget.configure(bg=color_principal)
                break
        
        # Actualizar botón
        self.btn_tema.configure(text=btn_texto)
        
        # Mostrar notificación
        messagebox.showinfo("Tema", f"Tema {'oscuro' if self.tema_oscuro else 'claro'} activado ✨")
    
    def animar_boton(self, boton, original_bg, hover_bg):
        """Animar botón al pasar el mouse"""
        def on_enter(event):
            boton.config(bg=hover_bg)
        
        def on_leave(event):
            boton.config(bg=original_bg)
        
        boton.bind("<Enter>", on_enter)
        boton.bind("<Leave>", on_leave)
    
    def crear_tab_operaciones(self):
        """Pestaña de operaciones con diseño mejorado"""
        frame = ttk.Frame(self.notebook, padding="0")
        self.notebook.add(frame, text="📋 Operaciones Rápidas")
        
        # Contenedor principal
        main_container = tk.Frame(frame, bg=self.COLOR_FONDO)
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # ====== SECCIÓN DE ENTRADA ======
        entrada_frame = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=0)
        entrada_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Sombra simulada
        sombra = tk.Frame(entrada_frame, bg="#e0e0e0", height=1)
        sombra.pack(fill=tk.X, side=tk.BOTTOM)
        
        entrada_inner = tk.Frame(entrada_frame, bg="white")
        entrada_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        # Icono y título
        titulo_entrada = tk.Label(
            entrada_inner,
            text="✅ REGISTRAR INGRESO",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.COLOR_ACENTO1
        )
        titulo_entrada.pack(anchor=tk.W, pady=(0, 20))
        
        # Campos
        campos_frame = tk.Frame(entrada_inner, bg="white")
        campos_frame.pack(fill=tk.X)
        
        tk.Label(
            campos_frame,
            text="Placa del Vehículo",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg=self.COLOR_TEXTO
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.entrada_placa = ttk.Entry(campos_frame, width=40)
        self.entrada_placa.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(
            campos_frame,
            text="Tipo de Vehículo",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg=self.COLOR_TEXTO
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.combo_tipo = ttk.Combobox(
            campos_frame,
            values=["🚗 Carro", "🏍️ Moto"],
            state="readonly",
            width=37
        )
        self.combo_tipo.pack(fill=tk.X, pady=(0, 25))
        self.combo_tipo.current(0)
        
        btn_ingreso = ttk.Button(
            entrada_inner,
            text="✓ REGISTRAR INGRESO",
            command=self.registrar_ingreso
        )
        btn_ingreso.pack(fill=tk.X, pady=(0, 0))
        
        # ====== SECCIÓN DE SALIDA ======
        salida_frame = tk.Frame(main_container, bg="white", relief=tk.FLAT, bd=0)
        salida_frame.pack(fill=tk.X, pady=(0, 20))
        
        sombra2 = tk.Frame(salida_frame, bg="#e0e0e0", height=1)
        sombra2.pack(fill=tk.X, side=tk.BOTTOM)
        
        salida_inner = tk.Frame(salida_frame, bg="white")
        salida_inner.pack(fill=tk.BOTH, expand=True, padx=25, pady=25)
        
        titulo_salida = tk.Label(
            salida_inner,
            text="❌ REGISTRAR SALIDA",
            font=("Segoe UI", 14, "bold"),
            bg="white",
            fg=self.COLOR_ACENTO2
        )
        titulo_salida.pack(anchor=tk.W, pady=(0, 20))
        
        tk.Label(
            salida_inner,
            text="Placa del Vehículo",
            font=("Segoe UI", 10, "bold"),
            bg="white",
            fg=self.COLOR_TEXTO
        ).pack(anchor=tk.W, pady=(0, 5))
        
        self.salida_placa = ttk.Entry(salida_inner, width=40)
        self.salida_placa.pack(fill=tk.X, pady=(0, 25))
        
        btn_salida = ttk.Button(
            salida_inner,
            text="✓ REGISTRAR SALIDA",
            command=self.registrar_salida
        )
        btn_salida.pack(fill=tk.X)
    
    def crear_tab_activos(self):
        """Pestaña de vehículos activos con diseño mejorado"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="🚗 Vehículos Activos")
        
        # Encabezado
        header_frame = tk.Frame(frame, bg=self.COLOR_FONDO)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        
        titulo_activos = tk.Label(
            header_frame,
            text="Vehículos Actualmente en el Parqueadero",
            font=("Segoe UI", 13, "bold"),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO
        )
        titulo_activos.pack(side=tk.LEFT)
        
        btn_act = ttk.Button(
            header_frame,
            text="🔄 Actualizar",
            command=self.actualizar_lista_vehiculos
        )
        btn_act.pack(side=tk.RIGHT)
        
        # Tabla con mejor estilo
        columns = ("Placa", "Tipo", "Hora Entrada", "Tiempo (min)")
        self.tree_activos = ttk.Treeview(
            frame,
            columns=columns,
            height=18,
            show="headings",
            style='Treeview'
        )
        
        self.tree_activos.heading("Placa", text="🔑 Placa")
        self.tree_activos.heading("Tipo", text="🚘 Tipo")
        self.tree_activos.heading("Hora Entrada", text="⏰ Hora Entrada")
        self.tree_activos.heading("Tiempo (min)", text="⏱️ Tiempo (min)")
        
        self.tree_activos.column("Placa", width=100)
        self.tree_activos.column("Tipo", width=100)
        self.tree_activos.column("Hora Entrada", width=200)
        self.tree_activos.column("Tiempo (min)", width=150)
        
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=self.tree_activos.yview)
        self.tree_activos.configure(yscroll=scrollbar.set)
        
        self.tree_activos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def crear_tab_busqueda(self):
        """Pestaña para búsqueda y filtrado"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="🔍 Búsqueda y Filtros")
        
        # Marco de búsqueda
        busqueda_frame = ttk.LabelFrame(frame, text="BUSCAR POR PLACA", padding="15")
        busqueda_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(busqueda_frame, text="Placa:").grid(row=0, column=0, sticky=tk.W, pady=8)
        self.entrada_busqueda = ttk.Entry(busqueda_frame, width=30, font=("Arial", 10))
        self.entrada_busqueda.grid(row=0, column=1, sticky=tk.EW, padx=10)
        
        btn_buscar = ttk.Button(
            busqueda_frame,
            text="🔍 Buscar",
            command=self.buscar_vehiculo
        )
        btn_buscar.grid(row=0, column=2, padx=5)
        
        # Marco de filtros
        filtro_frame = ttk.LabelFrame(frame, text="FILTRAR POR TIPO", padding="15")
        filtro_frame.pack(fill=tk.X, pady=10)
        
        ttk.Label(filtro_frame, text="Tipo:").pack(side=tk.LEFT, padx=5)
        
        btn_todos = ttk.Button(
            filtro_frame,
            text="Ver Todos",
            command=self.filtrar_todos
        )
        btn_todos.pack(side=tk.LEFT, padx=5)
        
        btn_carros = ttk.Button(
            filtro_frame,
            text="Solo Carros",
            command=lambda: self.filtrar_por_tipo("carro")
        )
        btn_carros.pack(side=tk.LEFT, padx=5)
        
        btn_motos = ttk.Button(
            filtro_frame,
            text="Solo Motos",
            command=lambda: self.filtrar_por_tipo("moto")
        )
        btn_motos.pack(side=tk.LEFT, padx=5)
        
        # Resultados de búsqueda
        resultado_frame = ttk.LabelFrame(frame, text="RESULTADOS", padding="15")
        resultado_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        columns = ("Placa", "Tipo", "Hora Entrada", "Tiempo (min)")
        self.tree_busqueda = ttk.Treeview(resultado_frame, columns=columns, height=12, show="headings")
        
        self.tree_busqueda.heading("Placa", text="Placa")
        self.tree_busqueda.heading("Tipo", text="Tipo")
        self.tree_busqueda.heading("Hora Entrada", text="Hora Entrada")
        self.tree_busqueda.heading("Tiempo (min)", text="Tiempo (min)")
        
        self.tree_busqueda.column("Placa", width=80)
        self.tree_busqueda.column("Tipo", width=70)
        self.tree_busqueda.column("Hora Entrada", width=150)
        self.tree_busqueda.column("Tiempo (min)", width=100)
        
        scrollbar = ttk.Scrollbar(resultado_frame, orient=tk.VERTICAL, command=self.tree_busqueda.yview)
        self.tree_busqueda.configure(yscroll=scrollbar.set)
        
        self.tree_busqueda.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    def crear_tab_estadisticas(self):
        """Pestaña para mostrar estadísticas con diseño premium"""
        frame = ttk.Frame(self.notebook, padding="0")
        self.notebook.add(frame, text="📊 Estadísticas")
        
        container = tk.Frame(frame, bg=self.COLOR_FONDO)
        container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Título
        titulo = tk.Label(
            container,
            text="📈 MÉTRICAS DEL PARQUEADERO",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO
        )
        titulo.pack(pady=(0, 20))
        
        # Grid de estadísticas activas
        stats_grid = tk.Frame(container, bg=self.COLOR_FONDO)
        stats_grid.pack(fill=tk.X, pady=(0, 20))
        
        self.label_activos = self._crear_card_stats(
            stats_grid, "🚗 ACTIVOS", "0", self.COLOR_ACENTO1
        )
        
        self.label_carros = self._crear_card_stats(
            stats_grid, "🚙 CARROS", "0", "#2ecc71", 1
        )
        
        self.label_motos = self._crear_card_stats(
            stats_grid, "🏍️ MOTOS", "0", self.COLOR_ACENTO2, 2
        )
        
        # Separador
        sep = tk.Frame(container, bg=self.COLOR_BORDE, height=2)
        sep.pack(fill=tk.X, pady=20)
        
        # Grid de estadísticas financieras
        financiero_titulo = tk.Label(
            container,
            text="💰 HISTÓRICO Y FINANZAS",
            font=("Segoe UI", 16, "bold"),
            bg=self.COLOR_FONDO,
            fg=self.COLOR_TEXTO
        )
        financiero_titulo.pack(pady=(0, 20))
        
        financiero_grid = tk.Frame(container, bg=self.COLOR_FONDO)
        financiero_grid.pack(fill=tk.X, pady=(0, 20))
        
        self.label_historico = self._crear_card_stats(
            financiero_grid, "📋 PROCESADOS", "0", "#9b59b6"
        )
        
        self.label_ingresos = self._crear_card_stats(
            financiero_grid, "💵 TOTAL", "$0", "#f39c12", 1
        )
        
        self.label_promedio = self._crear_card_stats(
            financiero_grid, "📊 PROMEDIO", "$0", "#16a085", 2
        )
        
        # Botón de actualización
        ttk.Button(
            container,
            text="🔄 Actualizar Estadísticas",
            command=self.actualizar_estadisticas
        ).pack(fill=tk.X, pady=10)
    
    def _crear_card_stats(self, parent, titulo, valor, color, column=0):
        """Crear una tarjeta de estadística con estilo premium"""
        card = tk.Frame(parent, bg="white", relief=tk.FLAT, bd=0)
        card.grid(row=0, column=column, padx=10, pady=0, sticky=tk.NSEW, ipadx=20, ipady=20)
        
        # Barra de color
        barra = tk.Frame(card, bg=color, height=4)
        barra.pack(fill=tk.X, pady=(0, 15))
        
        # Título
        lbl_titulo = tk.Label(
            card,
            text=titulo,
            font=("Segoe UI", 11, "bold"),
            bg="white",
            fg="#666666"
        )
        lbl_titulo.pack(anchor=tk.W, pady=(0, 5))
        
        # Valor
        lbl_valor = tk.Label(
            card,
            text=valor,
            font=("Segoe UI", 24, "bold"),
            bg="white",
            fg=color
        )
        lbl_valor.pack(anchor=tk.W)
        
        parent.columnconfigure(column, weight=1)
        
        return lbl_valor
    
    def crear_tab_historico(self):
        """Pestaña para histórico completo y reportes"""
        frame = ttk.Frame(self.notebook, padding="20")
        self.notebook.add(frame, text="📜 Histórico y Reportes")
        
        # Botones de reportes
        botones_frame = ttk.Frame(frame)
        botones_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            botones_frame,
            text="📄 Ver Histórico Completo",
            command=self.ver_historico
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botones_frame,
            text="📊 Generar Reporte del Día",
            command=self.generar_reporte
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            botones_frame,
            text="🔄 Actualizar",
            command=self.actualizar_historico
        ).pack(side=tk.LEFT, padx=5)
        
        # Tabla de histórico
        historico_frame = ttk.LabelFrame(frame, text="VEHÍCULOS PROCESADOS", padding="10")
        historico_frame.pack(fill=tk.BOTH, expand=True)
        
        columns = ("Placa", "Tipo", "Entrada", "Salida", "Tiempo (min)", "Pago ($)")
        self.tree_historico = ttk.Treeview(historico_frame, columns=columns, height=15, show="headings")
        
        self.tree_historico.heading("Placa", text="Placa")
        self.tree_historico.heading("Tipo", text="Tipo")
        self.tree_historico.heading("Entrada", text="Hora Entrada")
        self.tree_historico.heading("Salida", text="Hora Salida")
        self.tree_historico.heading("Tiempo (min)", text="Tiempo")
        self.tree_historico.heading("Pago ($)", text="Pago")
        
        self.tree_historico.column("Placa", width=70)
        self.tree_historico.column("Tipo", width=60)
        self.tree_historico.column("Entrada", width=120)
        self.tree_historico.column("Salida", width=120)
        self.tree_historico.column("Tiempo (min)", width=80)
        self.tree_historico.column("Pago ($)", width=80)
        
        scrollbar = ttk.Scrollbar(historico_frame, orient=tk.VERTICAL, command=self.tree_historico.yview)
        self.tree_historico.configure(yscroll=scrollbar.set)
        
        self.tree_historico.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # ====== MÉTODOS DE OPERACIONES ======
    
    def registrar_ingreso(self):
        """Registrar el ingreso de un vehículo con animación"""
        placa = self.entrada_placa.get().strip().upper()
        tipo_seleccionado = self.combo_tipo.get()
        
        # Extraer solo el tipo (carro o moto) del valor con emoji
        tipo = "carro" if "Carro" in tipo_seleccionado else "moto"
        
        if not placa:
            messagebox.showerror("⚠️ Error de Validación", "Por favor ingrese una placa")
            return
        
        if not tipo:
            messagebox.showerror("⚠️ Error de Validación", "Por favor seleccione un tipo de vehículo")
            return
        
        try:
            self.parqueadero.validar_tipo(tipo)
            
            _, existente = self.parqueadero._buscar_por_placa(placa)
            if existente:
                messagebox.showwarning("⚠️ Advertencia", "Este vehículo ya está registrado")
                return
            
            vehiculo = Vehiculo(placa, tipo, datetime.now())
            self.parqueadero.lista_vehiculos.append(vehiculo)
            self.parqueadero.guardar_datos()
            
            # Animación de éxito
            self._mostrar_notificacion_exito(f"✓ Vehículo {placa} ingresó correctamente", "success")
            
            self.entrada_placa.delete(0, tk.END)
            self.combo_tipo.current(0)
            self.actualizar_lista_vehiculos()
            self.actualizar_estadisticas()
            
        except ValueError as e:
            messagebox.showerror("❌ Error", str(e))
    
    def _mostrar_notificacion_exito(self, mensaje, tipo="success"):
        """Mostrar notificación flotante de éxito sin bloquear"""
        ventana_notif = tk.Toplevel(self.root)
        ventana_notif.wm_overrideredirect(True)
        ventana_notif.wm_attributes("-topmost", True)
        
        # Posicionar en la esquina superior derecha
        x = self.root.winfo_x() + self.root.winfo_width() - 350
        y = self.root.winfo_y() + 20
        ventana_notif.geometry(f"+{x}+{y}")
        
        # Colores según el tipo
        if tipo == "success":
            bg_color = self.COLOR_EXITO
            text_color = "white"
        else:
            bg_color = self.COLOR_ADVERTENCIA
            text_color = "white"
        
        frame = tk.Frame(ventana_notif, bg=bg_color, relief=tk.FLAT, bd=0)
        frame.pack(padx=15, pady=12)
        
        lbl = tk.Label(
            frame,
            text=mensaje,
            font=("Segoe UI", 11, "bold"),
            bg=bg_color,
            fg=text_color
        )
        lbl.pack()
        
        # Auto-cerrar después de 3 segundos
        ventana_notif.after(3000, ventana_notif.destroy)
    
    def registrar_salida(self):
        """Registrar la salida de un vehículo"""
        placa = self.salida_placa.get().strip().upper()
        
        if not placa:
            messagebox.showerror("⚠️ Error de Validación", "Por favor ingrese una placa")
            return
        
        try:
            idx, vehiculo = self.parqueadero._buscar_por_placa(placa)
            
            if vehiculo is None:
                messagebox.showerror("❌ Vehículo no encontrado", "La placa ingresada no existe en el sistema")
                return
            
            vehiculo.registrar_salida(datetime.now())
            
            minutos = int(vehiculo.calcular_tiempo())
            pago = vehiculo.calcular_pago()
            tarifa = 120 if vehiculo.tipo == 'carro' else 70
            
            # Crear resumen con mejor formato
            resumen = f"""
╔════════════════════════════════════════════╗
║        RESUMEN DEL SERVICIO                ║
╠════════════════════════════════════════════╣
║ Placa:           {vehiculo.placa:<28} ║
║ Tipo:            {vehiculo.tipo.upper():<28} ║
║ Entrada:         {vehiculo.get_hora_entrada().strftime('%Y-%m-%d %H:%M:%S'):<28} ║
║ Salida:          {vehiculo.get_hora_salida().strftime('%Y-%m-%d %H:%M:%S'):<28} ║
╠════════════════════════════════════════════╣
║ Tiempo:          {minutos} minutos{' ' * (25-len(str(minutos)))} ║
║ Tarifa/min:      ${tarifa}{' ' * (25-len(str(tarifa)))} ║
║ TOTAL A PAGAR:   ${pago}{' ' * (25-len(str(pago)))} ║
╚════════════════════════════════════════════╝
            """
            
            # Mostrar en una ventana grande
            ventana_salida = tk.Toplevel(self.root)
            ventana_salida.title("✓ Salida Registrada")
            ventana_salida.geometry("500x400")
            ventana_salida.configure(bg=self.COLOR_EXITO)
            
            # Header
            header_salida = tk.Frame(ventana_salida, bg=self.COLOR_EXITO, height=60)
            header_salida.pack(fill=tk.X)
            header_salida.pack_propagate(False)
            
            titulo_salida = tk.Label(
                header_salida,
                text="✓ VEHÍCULO PROCESADO CON ÉXITO",
                font=("Segoe UI", 16, "bold"),
                bg=self.COLOR_EXITO,
                fg="white"
            )
            titulo_salida.pack(pady=15)
            
            # Contenido
            contenido = tk.Frame(ventana_salida, bg="white")
            contenido.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
            
            texto_resumen = scrolledtext.ScrolledText(
                contenido,
                wrap=tk.WORD,
                font=("Courier New", 11),
                bg="white",
                fg=self.COLOR_TEXTO,
                height=15,
                width=60
            )
            texto_resumen.pack(fill=tk.BOTH, expand=True)
            texto_resumen.insert(tk.END, resumen)
            texto_resumen.config(state=tk.DISABLED)
            
            # Botón de confirmación
            btn_frame = tk.Frame(ventana_salida, bg="white")
            btn_frame.pack(fill=tk.X, padx=20, pady=20)
            
            btn_ok = ttk.Button(
                btn_frame,
                text="✓ Confirmar",
                command=ventana_salida.destroy
            )
            btn_ok.pack(fill=tk.X)
            
            # Guardar en histórico
            self.parqueadero.guardar_historico(vehiculo)
            
            del self.parqueadero.lista_vehiculos[idx]
            self.parqueadero.guardar_datos()
            
            self.salida_placa.delete(0, tk.END)
            self.actualizar_lista_vehiculos()
            self.actualizar_historico()
            self.actualizar_estadisticas()
            
            # Notificación de éxito
            self._mostrar_notificacion_exito(f"✓ Cobro de ${pago} procesado", "success")
            
        except ValueError as e:
            messagebox.showerror("❌ Error", str(e))
    
    # ====== MÉTODOS DE ACTUALIZACIÓN Y FILTRADO ======
    
    def actualizar_lista_vehiculos(self):
        """Actualizar la lista de vehículos activos"""
        for item in self.tree_activos.get_children():
            self.tree_activos.delete(item)
        
        if not self.parqueadero.lista_vehiculos:
            self.tree_activos.insert("", tk.END, values=("Sin vehículos", "", "", ""))
        else:
            for vehiculo in self.parqueadero.lista_vehiculos:
                hora_entrada = vehiculo.get_hora_entrada().strftime("%Y-%m-%d %H:%M:%S")
                tiempo_minutos = int((datetime.now() - vehiculo.get_hora_entrada()).total_seconds() / 60)
                self.tree_activos.insert(
                    "", 
                    tk.END, 
                    values=(vehiculo.placa, vehiculo.tipo, hora_entrada, tiempo_minutos)
                )
    
    def buscar_vehiculo(self):
        """Buscar un vehículo por placa"""
        placa = self.entrada_busqueda.get().strip().upper()
        
        for item in self.tree_busqueda.get_children():
            self.tree_busqueda.delete(item)
        
        if not placa:
            messagebox.showwarning("Advertencia", "Por favor ingrese una placa")
            return
        
        encontrado = False
        for vehiculo in self.parqueadero.lista_vehiculos:
            if vehiculo.placa == placa:
                hora_entrada = vehiculo.get_hora_entrada().strftime("%Y-%m-%d %H:%M:%S")
                tiempo_minutos = int((datetime.now() - vehiculo.get_hora_entrada()).total_seconds() / 60)
                self.tree_busqueda.insert(
                    "",
                    tk.END,
                    values=(vehiculo.placa, vehiculo.tipo, hora_entrada, tiempo_minutos)
                )
                encontrado = True
                break
        
        if not encontrado:
            messagebox.showinfo("Resultado", f"No se encontró vehículo con placa {placa}")
    
    def filtrar_por_tipo(self, tipo):
        """Filtrar vehículos por tipo"""
        for item in self.tree_busqueda.get_children():
            self.tree_busqueda.delete(item)
        
        vehiculos_filtrados = self.parqueadero.filtrar_por_tipo(tipo)
        
        if not vehiculos_filtrados:
            self.tree_busqueda.insert("", tk.END, values=("Sin vehículos de este tipo", "", "", ""))
        else:
            for vehiculo in vehiculos_filtrados:
                hora_entrada = vehiculo.get_hora_entrada().strftime("%Y-%m-%d %H:%M:%S")
                tiempo_minutos = int((datetime.now() - vehiculo.get_hora_entrada()).total_seconds() / 60)
                self.tree_busqueda.insert(
                    "",
                    tk.END,
                    values=(vehiculo.placa, vehiculo.tipo, hora_entrada, tiempo_minutos)
                )
    
    def filtrar_todos(self):
        """Mostrar todos los vehículos activos"""
        self.entrada_busqueda.delete(0, tk.END)
        self.actualizar_lista_vehiculos()
        
        for item in self.tree_busqueda.get_children():
            self.tree_busqueda.delete(item)
        
        if not self.parqueadero.lista_vehiculos:
            self.tree_busqueda.insert("", tk.END, values=("Sin vehículos activos", "", "", ""))
        else:
            for vehiculo in self.parqueadero.lista_vehiculos:
                hora_entrada = vehiculo.get_hora_entrada().strftime("%Y-%m-%d %H:%M:%S")
                tiempo_minutos = int((datetime.now() - vehiculo.get_hora_entrada()).total_seconds() / 60)
                self.tree_busqueda.insert(
                    "",
                    tk.END,
                    values=(vehiculo.placa, vehiculo.tipo, hora_entrada, tiempo_minutos)
                )
    
    def actualizar_estadisticas(self):
        """Actualizar panel de estadísticas"""
        stats = self.parqueadero.obtener_estadisticas()
        
        self.label_activos.config(text=f"{stats['total_activos']}")
        self.label_carros.config(text=f"{stats['carros_activos']}")
        self.label_motos.config(text=f"{stats['motos_activas']}")
        self.label_historico.config(text=f"{stats['total_historico']}")
        self.label_ingresos.config(text=f"${stats['ingresos_totales']}")
        
        promedio = stats.get('ingreso_promedio', 0)
        self.label_promedio.config(text=f"${round(promedio, 2)}")
    
    def actualizar_historico(self):
        """Actualizar tabla de histórico"""
        for item in self.tree_historico.get_children():
            self.tree_historico.delete(item)
        
        if not self.parqueadero.historico:
            self.tree_historico.insert("", tk.END, values=("Sin registros", "", "", "", "", ""))
        else:
            for vehiculo in self.parqueadero.historico:
                if vehiculo.get_hora_salida():
                    entrada = vehiculo.get_hora_entrada().strftime("%Y-%m-%d %H:%M")
                    salida = vehiculo.get_hora_salida().strftime("%Y-%m-%d %H:%M")
                    tiempo = int(vehiculo.calcular_tiempo())
                    pago = vehiculo.calcular_pago()
                    
                    self.tree_historico.insert(
                        "",
                        tk.END,
                        values=(vehiculo.placa, vehiculo.tipo, entrada, salida, tiempo, pago)
                    )
    
    def ver_historico(self):
        """Mostrar histórico completo en ventana emergente"""
        ventana = tk.Toplevel(self.root)
        ventana.title("Histórico Completo")
        ventana.geometry("700x500")
        
        # Tabla
        columns = ("Placa", "Tipo", "Entrada", "Salida", "Tiempo (min)", "Pago ($)")
        tree = ttk.Treeview(ventana, columns=columns, height=20, show="headings")
        
        tree.heading("Placa", text="Placa")
        tree.heading("Tipo", text="Tipo")
        tree.heading("Entrada", text="Hora Entrada")
        tree.heading("Salida", text="Hora Salida")
        tree.heading("Tiempo (min)", text="Tiempo")
        tree.heading("Pago ($)", text="Pago")
        
        tree.column("Placa", width=60)
        tree.column("Tipo", width=50)
        tree.column("Entrada", width=110)
        tree.column("Salida", width=110)
        tree.column("Tiempo (min)", width=80)
        tree.column("Pago ($)", width=80)
        
        scrollbar = ttk.Scrollbar(ventana, orient=tk.VERTICAL, command=tree.yview)
        tree.configure(yscroll=scrollbar.set)
        
        # Llenar tabla
        for vehiculo in self.parqueadero.historico:
            if vehiculo.get_hora_salida():
                entrada = vehiculo.get_hora_entrada().strftime("%Y-%m-%d %H:%M")
                salida = vehiculo.get_hora_salida().strftime("%Y-%m-%d %H:%M")
                tiempo = int(vehiculo.calcular_tiempo())
                pago = vehiculo.calcular_pago()
                
                tree.insert(
                    "",
                    tk.END,
                    values=(vehiculo.placa, vehiculo.tipo, entrada, salida, tiempo, pago)
                )
        
        tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y, pady=10)
    
    def generar_reporte(self):
        """Generar y mostrar reporte del día"""
        stats = self.parqueadero.obtener_estadisticas()
        
        reporte = f"""
{'='*60}
REPORTE DE PARQUEADERO - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
{'='*60}

ESTADO ACTUAL:
  Vehículos Activos: {stats['total_activos']}
    - Carros: {stats['carros_activos']}
    - Motos: {stats['motos_activas']}

HISTÓRICO Y FINANZAS:
  Total Vehículos Procesados: {stats['total_historico']}
  Ingresos Totales: ${stats['ingresos_totales']}
  Ingreso Promedio por Vehículo: ${round(stats.get('ingreso_promedio', 0), 2)}
  Tiempo Promedio: {round(stats.get('tiempo_promedio', 0), 2)} minutos

{'='*60}
        """
        
        ventana_reporte = tk.Toplevel(self.root)
        ventana_reporte.title("Reporte del Sistema")
        ventana_reporte.geometry("700x400")
        
        texto = scrolledtext.ScrolledText(
            ventana_reporte,
            wrap=tk.WORD,
            font=("Courier", 11),
            padx=20,
            pady=20
        )
        texto.pack(fill=tk.BOTH, expand=True)
        texto.insert(tk.END, reporte)
        texto.config(state=tk.DISABLED)


def menu():
    """Crear e inicializar la interfaz gráfica"""
    root = tk.Tk()
    app = InterfazParqueadero(root)
    root.mainloop()


if __name__ == "__main__":
    menu()