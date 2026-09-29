# main.py
# ---------------------------------------------------------
# Convertir °C - °F - °K
# ---------------------------------------------------------

import os
import traceback
from os.path import dirname, join, exists

os.environ.setdefault("KIVY_NO_CONSOLELOG", "0")

from kivy.config import Config
Config.set("graphics", "multisamples", "0")
Config.set("kivy", "log_level", "debug")

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.lang import Builder
from kivy.properties import NumericProperty, StringProperty, ListProperty
from kivy.animation import Animation
from kivy.resources import resource_add_path
from kivy.clock import Clock

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

DIR_APP = dirname(__file__)
resource_add_path(DIR_APP)


class ConvertidorTemperatura(BoxLayout):
    modo = StringProperty("C")
    celsius_actual = NumericProperty(0.0)
    celsius_mostrado = NumericProperty(0.0)
    color_fondo = ListProperty([0.09, 0.11, 0.15, 1])
    color_acento = ListProperty([0.3, 0.55, 0.95, 1])

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_once(self._inicio_seguro, 0)

    def _inicio_seguro(self, dt):
        try:
            self._refrescar_todo(animar=False)
            self._actualizar_limites_slider()
        except Exception as e:
            print("[inicio] error:", e)
            traceback.print_exc()

    def convertir_desde_slider(self, valor):
        try:
            if self.modo == "C":
                self.celsius_actual = valor
            else:
                self.celsius_actual = fahrenheit_a_celsius(valor)
            self.celsius_mostrado = self.celsius_actual
            self._refrescar_textos()
            self._refrescar_color()
            self._actualizar_valor_slider_label()
        except Exception as e:
            print("[slider] error:", e)

    def establecer_valor_manual(self, texto):
        try:
            texto = (texto or "").strip().replace(",", ".")
            if not texto:
                return
            try:
                valor = float(texto)
            except ValueError:
                if "txt_manual" in self.ids:
                    self.ids.txt_manual.text = ""
                    self.ids.txt_manual.hint_text = "Valor inválido"
                return

            if self.modo == "C":
                valor = max(LIMITE_MIN_C, min(LIMITE_MAX_C, valor))
            else:
                valor = max(LIMITE_MIN_F, min(LIMITE_MAX_F, valor))

            if "slider" in self.ids:
                self.ids.slider.value = valor
            if "txt_manual" in self.ids:
                self.ids.txt_manual.text = ""
            self._animar_a_valor_actual()
        except Exception as e:
            print("[manual] error:", e)

    def establecer_valor_rapido(self, celsius):
        try:
            if "slider" not in self.ids:
                return
            if self.modo == "C":
                self.ids.slider.value = celsius
            else:
                self.ids.slider.value = celsius_a_fahrenheit(celsius)
            self._animar_a_valor_actual()
        except Exception as e:
            print("[rapido] error:", e)

    def cambiar_modo(self):
        try:
            if "slider" not in self.ids:
                return
            if self.modo == "C":
                self.modo = "F"
                self.ids.slider.min = LIMITE_MIN_F
                self.ids.slider.max = LIMITE_MAX_F
                self.ids.slider.value = celsius_a_fahrenheit(self.celsius_actual)
                if "btn_modo" in self.ids:
                    self.ids.btn_modo.text = "Cambiar a °C"
                if "lbl_unidad_slider" in self.ids:
                    self.ids.lbl_unidad_slider.text = "Deslizador en °F"
            else:
                self.modo = "C"
                self.ids.slider.min = LIMITE_MIN_C
                self.ids.slider.max = LIMITE_MAX_C
                self.ids.slider.value = self.celsius_actual
                if "btn_modo" in self.ids:
                    self.ids.btn_modo.text = "Cambiar a °F"
                if "lbl_unidad_slider" in self.ids:
                    self.ids.lbl_unidad_slider.text = "Deslizador en °C"
            self._actualizar_limites_slider()
            self._actualizar_valor_slider_label()
        except Exception as e:
            print("[modo] error:", e)

    def _animar_a_valor_actual(self):
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
            self._actualizar_valor_slider_label()

    def _refrescar_textos(self):
        try:
            c = self.celsius_mostrado
            f = celsius_a_fahrenheit(c)
            k = celsius_a_kelvin(c)
            if "lbl_celsius" in self.ids:
                self.ids.lbl_celsius.text = "{:.1f} °C".format(c)
            if "lbl_fahrenheit" in self.ids:
                self.ids.lbl_fahrenheit.text = "{:.1f} °F".format(f)
            if "lbl_kelvin" in self.ids:
                self.ids.lbl_kelvin.text = "{:.1f} K".format(k)
        except Exception as e:
            print("[textos] error:", e)

    def _refrescar_color(self):
        try:
            self.color_fondo = color_fondo_para_temperatura(self.celsius_mostrado)
            self.color_acento = color_acento_para_temperatura(self.celsius_mostrado)
        except Exception as e:
            print("[color] error:", e)

    def _actualizar_valor_slider_label(self):
        try:
            if "lbl_valor_slider" in self.ids and "slider" in self.ids:
                self.ids.lbl_valor_slider.text = "{:.1f}°".format(self.ids.slider.value)
        except Exception:
            pass

    def _actualizar_limites_slider(self):
        try:
            if "slider" not in self.ids:
                return
            if "lbl_min_slider" in self.ids:
                self.ids.lbl_min_slider.text = "{:.0f}°".format(self.ids.slider.min)
            if "lbl_max_slider" in self.ids:
                self.ids.lbl_max_slider.text = "{:.0f}°".format(self.ids.slider.max)
        except Exception:
            pass


class TemperaturaApp(App):
    def build(self):
        try:
            kv_path = join(DIR_APP, "interfaz.kv")
            if exists(kv_path):
                Builder.load_file(kv_path)
                print("[build] KV cargado:", kv_path)
            else:
                Builder.load_file("interfaz.kv")
                print("[build] KV cargado: interfaz.kv")
            return ConvertidorTemperatura()
        except Exception as e:
            print("[build] ERROR FATAL:", e)
            traceback.print_exc()
            root = BoxLayout(orientation="vertical", padding=20)
            root.add_widget(Label(
                text="Error al iniciar:\n" + str(e),
                color=(1, 0.3, 0.3, 1),
            ))
            return root


if __name__ == "__main__":
    try:
        TemperaturaApp().run()
    except Exception as e:
        print("[run] ERROR FATAL:", e)
        traceback.print_exc()
        raise
