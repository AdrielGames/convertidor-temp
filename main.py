# main.py
# ---------------------------------------------------------
# Convertir °C - °F - °K
# App que convierte entre Celsius, Fahrenheit y Kelvin.
# Se puede deslizar en °C o en °F (modo intercambiable),
# escribir un valor manualmente, o tocar un botón rápido.
# Guarda el último valor usado y lo restaura al abrir la app.
# ---------------------------------------------------------

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.animation import Animation
from kivy.storage.jsonstore import JsonStore

from conversiones import (
    celsius_a_fahrenheit,
    fahrenheit_a_celsius,
    celsius_a_kelvin,
    color_fondo_para_temperatura,
    color_acento_para_temperatura,
    LIMITE_MIN_C,
    LIMITE_MAX_C,
    LIMITE_MIN_F,
    LIMITE_MAX_F,
)

# Archivo donde se guarda el último valor y modo usados.
# Se crea automáticamente junto al ejecutable la primera vez que se usa.
ALMACEN = JsonStore("ajustes_temperatura.json")


class ConvertidorTemperatura(BoxLayout):
    """
    Layout principal de la app. Mantiene la temperatura actual
    siempre en Celsius internamente (celsius_actual) sin importar
    en qué modo esté el slider, y a partir de ahí calcula todo
    lo demás (Fahrenheit, Kelvin, color de fondo, etc).
    """

    # Modo del slider: "C" (Celsius) o "F" (Fahrenheit)
    modo = StringProperty("C")

    # Temperatura actual en Celsius (fuente única de verdad)
    celsius_actual = NumericProperty(0.0)

    # Valor animado que se muestra en pantalla (para transiciones suaves
    # cuando el cambio viene de un botón rápido o de texto, no del slider)
    celsius_mostrado = NumericProperty(0.0)

    # Color de fondo, recalculado cada vez que cambia la temperatura
    color_fondo = ListProperty([0.09, 0.11, 0.15, 1])

    # Color de acento (más brillante) usado en el relleno del slider
    color_acento = ListProperty([0.3, 0.55, 0.95, 1])

    def on_kv_post(self, base_widget):
        """Se ejecuta justo después de cargar el .kv: aquí restauramos
        el último valor guardado, si existe."""
        self._cargar_estado_guardado()
        self._refrescar_todo(animar=False)

    # ------------------------------------------------------------------
    # Entradas de valor (slider, texto, botones rápidos)
    # ------------------------------------------------------------------

    def convertir_desde_slider(self, valor):
        """Se llama en cada movimiento del Slider. 'valor' está en la
        unidad del modo actual (°C o °F)."""
        if self.modo == "C":
            self.celsius_actual = valor
        else:
            self.celsius_actual = fahrenheit_a_celsius(valor)

        # El slider ya se mueve suavemente por sí solo: no animamos,
        # solo refrescamos texto/color al instante para que no haya retraso.
        self.celsius_mostrado = self.celsius_actual
        self._refrescar_textos()
        self._refrescar_color()
        self._guardar_estado()

    def establecer_valor_manual(self, texto):
        """Se llama al confirmar el TextInput. Interpreta el número
        escrito según el modo actual del slider."""
        texto = texto.strip().replace(",", ".")
        if not texto:
            return
        try:
            valor = float(texto)
        except ValueError:
            self.ids.txt_manual.text = ""
            self.ids.txt_manual.hint_text = "Valor inválido"
            return

        if self.modo == "C":
            valor = max(LIMITE_MIN_C, min(LIMITE_MAX_C, valor))
        else:
            valor = max(LIMITE_MIN_F, min(LIMITE_MAX_F, valor))

        self.ids.slider.value = valor  # dispara convertir_desde_slider
        self.ids.txt_manual.text = ""
        self._animar_a_valor_actual()

    def establecer_valor_rapido(self, celsius):
        """Botones rápidos (congelación, cuerpo humano, ebullición).
        Siempre reciben el valor en Celsius y lo convierten al modo activo."""
        if self.modo == "C":
            self.ids.slider.value = celsius
        else:
            self.ids.slider.value = celsius_a_fahrenheit(celsius)
        self._animar_a_valor_actual()

    def cambiar_modo(self):
        """Alterna el slider entre modo °C y modo °F, conservando la
        misma temperatura real (solo cambia la unidad de la escala)."""
        if self.modo == "C":
            self.modo = "F"
            self.ids.slider.min = LIMITE_MIN_F
            self.ids.slider.max = LIMITE_MAX_F
            self.ids.slider.value = celsius_a_fahrenheit(self.celsius_actual)
            self.ids.btn_modo.text = "Cambiar a °C"
            self.ids.lbl_unidad_slider.text = "Deslizador en °F"
        else:
            self.modo = "C"
            self.ids.slider.min = LIMITE_MIN_C
            self.ids.slider.max = LIMITE_MAX_C
            self.ids.slider.value = self.celsius_actual
            self.ids.btn_modo.text = "Cambiar a °F"
            self.ids.lbl_unidad_slider.text = "Deslizador en °C"
        self._guardar_estado()

    # ------------------------------------------------------------------
    # Refresco visual
    # ------------------------------------------------------------------

    def _animar_a_valor_actual(self):
        """Anima celsius_mostrado hasta celsius_actual (usado en botones
        rápidos y entrada manual, donde el salto no es gradual como
        al arrastrar el slider)."""
        Animation.cancel_all(self, "celsius_mostrado")
        anim = Animation(celsius_mostrado=self.celsius_actual, duration=0.35, t="out_cubic")
        anim.bind(on_progress=lambda *a: self._refrescar_textos())
        anim.bind(on_complete=lambda *a: self._refrescar_color())
        anim.start(self)

    def _refrescar_todo(self, animar=True):
        if animar:
            self._animar_a_valor_actual()
        else:
            self.celsius_mostrado = self.celsius_actual
            self._refrescar_textos()
            self._refrescar_color()

    def _refrescar_textos(self):
        c = self.celsius_mostrado
        f = celsius_a_fahrenheit(c)
        k = celsius_a_kelvin(c)
        self.ids.lbl_celsius.text = f"{c:.1f} °C"
        self.ids.lbl_fahrenheit.text = f"{f:.1f} °F"
        self.ids.lbl_kelvin.text = f"{k:.1f} K"

    def _refrescar_color(self):
        self.color_fondo = color_fondo_para_temperatura(self.celsius_mostrado)
        self.color_acento = color_acento_para_temperatura(self.celsius_mostrado)

    # ------------------------------------------------------------------
    # Persistencia (recuerda el último valor y modo al reabrir la app)
    # ------------------------------------------------------------------

    def _guardar_estado(self):
        try:
            ALMACEN.put(
                "ultimo_valor",
                celsius=self.celsius_actual,
                modo=self.modo,
            )
        except Exception:
            # Si el almacenamiento falla (ej. sin permisos de escritura),
            # la app sigue funcionando normalmente, solo sin recordar.
            pass

    def _cargar_estado_guardado(self):
        if not ALMACEN.exists("ultimo_valor"):
            return
        datos = ALMACEN.get("ultimo_valor")
        self.celsius_actual = datos.get("celsius", 0.0)
        modo_guardado = datos.get("modo", "C")

        if modo_guardado == "F":
            self.modo = "F"
            self.ids.slider.min = LIMITE_MIN_F
            self.ids.slider.max = LIMITE_MAX_F
            self.ids.slider.value = celsius_a_fahrenheit(self.celsius_actual)
            self.ids.btn_modo.text = "Cambiar a °C"
            self.ids.lbl_unidad_slider.text = "Deslizador en °F"
        else:
            self.modo = "C"
            self.ids.slider.value = self.celsius_actual


class TemperaturaApp(App):
    def build(self):
        Builder.load_file("interfaz.kv")
        return ConvertidorTemperatura()


if __name__ == "__main__":
    TemperaturaApp().run()
