import json
import os
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
from kivy.animation import Animation
from kivy.core.window import Window
from kivy.metrics import dp

# ==========================================
# 1. MODELO: Lógica y Datos del Juego
# ==========================================
class GameState:
    def __init__(self):
        self.save_file = 'tycoon_save.json'
        # Estado inicial por defecto
        self.data = {
            'tokens': 0,          # Moneda del juego
            'click_power': 1,     # Cuánto ganas por tap
            'auto_power': 0,      # Cuánto ganas por segundo
            'ai_level': 1,        # Nivel de tu IA
            'upgrades': {
                'algoritmo': {'level': 0, 'base_cost': 10, 'cost_mult': 1.5, 'effect': 1, 'type': 'click'},
                'servidor': {'level': 0, 'base_cost': 50, 'cost_mult': 1.6, 'effect': 2, 'type': 'auto'},
                'red_neuronal': {'level': 0, 'base_cost': 500, 'cost_mult': 2.0, 'effect': 10, 'type': 'auto'}
            }
        }
        self.load_game()

    def gain_tokens(self, amount):
        self.data['tokens'] += amount

    def get_upgrade_cost(self, upg_id):
        upg = self.data['upgrades'][upg_id]
        # Fórmula de escalado exponencial
        return int(upg['base_cost'] * (upg['cost_mult'] ** upg['level']))

    def buy_upgrade(self, upg_id):
        cost = self.get_upgrade_cost(upg_id)
        if self.data['tokens'] >= cost:
            self.data['tokens'] -= cost
            upg = self.data['upgrades'][upg_id]
            upg['level'] += 1
            
            # Aplicar el efecto
            if upg['type'] == 'click':
                self.data['click_power'] += upg['effect']
            elif upg['type'] == 'auto':
                self.data['auto_power'] += upg['effect']
            
            # Evolucionar la IA cada 10 mejoras totales
            total_levels = sum(u['level'] for u in self.data['upgrades'].values())
            self.data['ai_level'] = 1 + (total_levels // 10)
            
            self.save_game()
            return True
        return False

    def save_game(self):
        try:
            with open(self.save_file, 'w') as f:
                json.dump(self.data, f)
        except Exception as e:
            print(f"Error crítico al guardar: {e}")

    def load_game(self):
        if os.path.exists(self.save_file):
            try:
                with open(self.save_file, 'r') as f:
                    saved_data = json.load(f)
                    # Actualizar claves existentes para evitar crasheos si hay versiones viejas
                    for key in self.data.keys():
                        if key in saved_data:
                            self.data[key] = saved_data[key]
            except Exception as e:
                print(f"Archivo corrupto, iniciando nueva partida: {e}")

# ==========================================
# 2. VISTA Y CONTROLADOR: Interfaz Kivy
# ==========================================
class MainUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=dp(10), spacing=dp(10), **kwargs)
        Window.clearcolor = (0.1, 0.1, 0.15, 1) # Fondo oscuro cyber
        
        self.game = GameState()
        
        # --- SECCIÓN SUPERIOR: Estadísticas ---
        stats_box = BoxLayout(orientation='vertical', size_hint=(1, 0.2))
        
        self.lbl_ai_name = Label(text="IA Nivel: Perceptrón Básico", font_size='20sp', bold=True, color=(0, 1, 0.8, 1))
        self.lbl_tokens = Label(text="Datos (Tokens): 0", font_size='24sp', bold=True, color=(1, 1, 1, 1))
        self.lbl_gps = Label(text="Generación: 0/seg", font_size='14sp', color=(0.7, 0.7, 0.7, 1))
        
        stats_box.add_widget(self.lbl_ai_name)
        stats_box.add_widget(self.lbl_tokens)
        stats_box.add_widget(self.lbl_gps)
        self.add_widget(stats_box)

        # --- SECCIÓN CENTRAL: Botón Principal (El Clicker) ---
        center_box = BoxLayout(orientation='vertical', size_hint=(1, 0.4), padding=dp(20))
        self.btn_mine = Button(
            text="[ENTRENAR IA]\nProcesar Datos",
            font_size='22sp',
            background_color=(0.2, 0.6, 1, 1),
            background_normal='',
            halign='center'
        )
        self.btn_mine.bind(on_press=self.on_mine_click)
        center_box.add_widget(self.btn_mine)
        self.add_widget(center_box)

        # --- SECCIÓN INFERIOR: Tienda de Mejoras ---
        self.add_widget(Label(text="--- MEJORAS DE ARQUITECTURA ---", size_hint=(1, 0.05), bold=True))
        
        scroll = ScrollView(size_hint=(1, 0.35))
        self.store_grid = GridLayout(cols=1, spacing=dp(5), size_hint_y=None)
        self.store_grid.bind(minimum_height=self.store_grid.setter('height'))
        
        self.upg_buttons = {}
        self.create_store_ui()
        scroll.add_widget(self.store_grid)
        self.add_widget(scroll)

        # Iniciar el Game Loop (1 vez por segundo)
        Clock.schedule_interval(self.game_loop, 1.0)
        # Bucle rápido para refrescar UI (30 FPS)
        Clock.schedule_interval(self.update_ui, 1.0 / 30.0)

    def on_mine_click(self, instance):
        # Lógica
        self.game.gain_tokens(self.game.data['click_power'])
        
        # Animación visual adictiva (rebote)
        anim = Animation(size_hint=(0.95, 0.95), duration=0.05) + Animation(size_hint=(1, 1), duration=0.1, t='out_bounce')
        anim.start(instance)

    def create_store_ui(self):
        nombres_amigables = {
            'algoritmo': "Optimizar Algoritmo (+Click)",
            'servidor': "Comprar Servidor Cloud (+Auto)",
            'red_neuronal': "Clúster Neuronal (+Auto Avanzado)"
        }
        
        for upg_id in self.game.data['upgrades'].keys():
            btn = Button(text="", size_hint_y=None, height=dp(60), background_color=(0.3, 0.3, 0.3, 1), background_normal='')
            btn.bind(on_press=lambda instance, uid=upg_id: self.buy_action(uid))
            self.store_grid.add_widget(btn)
            self.upg_buttons[upg_id] = {'btn': btn, 'name': nombres_amigables[upg_id]}

    def buy_action(self, upg_id):
        if self.game.buy_upgrade(upg_id):
            # Animación de éxito
            btn = self.upg_buttons[upg_id]['btn']
            anim = Animation(background_color=(0, 1, 0, 1), duration=0.1) + Animation(background_color=(0.3, 0.3, 0.3, 1), duration=0.3)
            anim.start(btn)

    def game_loop(self, dt):
        # Generación automática (Idle)
        auto_gen = self.game.data['auto_power']
        if auto_gen > 0:
            self.game.gain_tokens(auto_gen)
            # Autoguardado silencioso cada ciertos segundos (gestionado en segundo plano)
            self.game.save_game()

    def update_ui(self, dt):
        # Refrescar textos
        self.lbl_tokens.text = f"Datos procesados: {int(self.game.data['tokens'])} TB"
        self.lbl_gps.text = f"Generación automática: {self.game.data['auto_power']} TB/s | Por click: {self.game.data['click_power']} TB"
        
        # Nombres de evolución de la IA
        nombres_ia = ["Perceptrón Básico", "Red Multicapa", "Deep Learning", "IA Generativa", "AGI (Inteligencia General)", "ASI (Súper Inteligencia)"]
        nivel_idx = min(self.game.data['ai_level'] - 1, len(nombres_ia) - 1)
        self.lbl_ai_name.text = f"Evolución IA [Nvl {self.game.data['ai_level']}]: {nombres_ia[nivel_idx]}"

        # Actualizar botones de tienda (Precio y disponibilidad)
        for upg_id, upg_data in self.game.data['upgrades'].items():
            btn_info = self.upg_buttons[upg_id]
            cost = self.game.get_upgrade_cost(upg_id)
            nivel = upg_data['level']
            btn_info['btn'].text = f"{btn_info['name']} (Nvl {nivel})\nCosto: {cost} TB"
            
            # Feedback de color si puedes comprarlo o no
            if self.game.data['tokens'] >= cost:
                btn_info['btn'].color = (0.5, 1, 0.5, 1) # Verde texto
            else:
                btn_info['btn'].color = (0.5, 0.5, 0.5, 1) # Gris texto

# ==========================================
# 3. LANZADOR: Motor de la App
# ==========================================
class AITycoonApp(App):
    def build(self):
        self.title = "AI Evolution Tycoon"
        return MainUI()

    def on_pause(self):
        # Concepto avanzado Android: Guardar al minimizar
        if hasattr(self.root, 'game'):
            self.root.game.save_game()
        return True

if __name__ == '__main__':
    AITycoonApp().run()
