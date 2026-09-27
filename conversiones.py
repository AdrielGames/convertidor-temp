# conversiones.py
# ---------------------------------------------------------
# Funciones puras de conversión de temperatura.
# No dependen de Kivy ni de ningún widget: reciben un número
# y devuelven un número. Esto las hace fáciles de probar por
# separado (ej. con pytest) sin necesitar la interfaz gráfica.
# ---------------------------------------------------------


def celsius_a_fahrenheit(celsius: float) -> float:
    """F = (C × 9/5) + 32"""
    return (celsius * 9 / 5) + 32


def fahrenheit_a_celsius(fahrenheit: float) -> float:
    """C = (F − 32) × 5/9"""
    return (fahrenheit - 32) * 5 / 9


def celsius_a_kelvin(celsius: float) -> float:
    """K = C + 273.15"""
    return celsius + 273.15


def fahrenheit_a_kelvin(fahrenheit: float) -> float:
    """Convierte Fahrenheit a Kelvin pasando por Celsius."""
    return celsius_a_kelvin(fahrenheit_a_celsius(fahrenheit))


def kelvin_a_celsius(kelvin: float) -> float:
    """C = K − 273.15"""
    return kelvin - 273.15


# --- Límites de cada escala usados por la interfaz ---
# Se usan para fijar el rango del Slider según el modo activo
# y para calcular el color de fondo dinámico.
LIMITE_MIN_C = -40.0
LIMITE_MAX_C = 150.0
LIMITE_MIN_F = celsius_a_fahrenheit(LIMITE_MIN_C)   # -40.0
LIMITE_MAX_F = celsius_a_fahrenheit(LIMITE_MAX_C)   # 302.0

# --- Valores de referencia para los botones rápidos (siempre en °C) ---
REFERENCIAS_RAPIDAS = [
    ("Congelación", 0.0),
    ("Cuerpo humano", 37.0),
    ("Ebullición", 100.0),
]


def _interpolar(minimo, maximo, fraccion):
    return minimo + (maximo - minimo) * fraccion


def color_fondo_para_temperatura(celsius: float):
    """Color oscuro para el fondo de pantalla: azul (frío) -> rojo (calor)."""
    rango = LIMITE_MAX_C - LIMITE_MIN_C
    fraccion = max(0.0, min(1.0, (celsius - LIMITE_MIN_C) / rango))
    r = _interpolar(0.09, 0.35, fraccion)
    g = _interpolar(0.13, 0.09, fraccion)
    b = _interpolar(0.30, 0.09, fraccion)
    return [r, g, b, 1]


def color_acento_para_temperatura(celsius: float):
    """Color brillante para el slider y acentos: celeste (frío) -> naranja (calor)."""
    rango = LIMITE_MAX_C - LIMITE_MIN_C
    fraccion = max(0.0, min(1.0, (celsius - LIMITE_MIN_C) / rango))
    r = _interpolar(0.30, 0.95, fraccion)
    g = _interpolar(0.55, 0.45, fraccion)
    b = _interpolar(0.95, 0.25, fraccion)
    return [r, g, b, 1]
