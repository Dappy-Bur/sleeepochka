from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.popup import Popup
from kivy.graphics import Color, Rectangle, Line
from kivy.core.window import Window
from kivy.utils import get_color_from_hex
from kivy.properties import NumericProperty, BooleanProperty, StringProperty
from plyer import notification
import subprocess
import os

# Цветовая схема
COLORS = {
    'primary': get_color_from_hex('#6A1B9A'),
    'secondary': get_color_from_hex('#9C27B0'),
    'accent': get_color_from_hex('#7E57C2'),
    'background': get_color_from_hex('#121212'),
    'text': get_color_from_hex('#FFFFFF'),
    'progress': get_color_from_hex('#7E57C2')
}

class ProgressBarLine(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.size_hint_y = None
        self.height = '4dp'
        self.bind(pos=self.update_canvas, size=self.update_canvas)
        
        self._progress = 0
        self._max = 100
        
    def update_canvas(self, *args):
        self.canvas.clear()
        with self.canvas:
            # Фоновая линия
            Color(rgba=(0.1, 0.1, 0.1, 1))
            Line(width=1.5, points=[self.x, self.center_y, self.right, self.center_y])
            
            # Линия прогресса
            if self._progress > 0:
                progress_width = self.width * (self._progress / self._max)
                Color(*COLORS['progress'])
                Line(width=1.5, points=[self.x, self.center_y, self.x + progress_width, self.center_y])
                
                # Яркий конец
                Color(rgba=(1, 1, 1, 0.7))
                Line(width=2.5, points=[self.x + progress_width - 5, self.center_y, self.x + progress_width, self.center_y])
    
    @property
    def progress(self):
        return self._progress
    
    @progress.setter
    def progress(self, value):
        self._progress = value
        self.update_canvas()
    
    @property
    def max(self):
        return self._max
    
    @max.setter
    def max(self, value):
        self._max = value
        self.update_canvas()

class TVButton(Button):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.background_normal = ''
        self.background_color = (0, 0, 0, 0)
        self.color = COLORS['text']
        self.font_size = '20sp'
        self.bold = True
        self.size_hint_y = None
        self.height = '70dp'
        
        with self.canvas.before:
            Color(*COLORS['accent'])
            self.rect = Rectangle(size=self.size, pos=self.pos)
        
        self.bind(pos=self.update_rect, size=self.update_rect)
    
    def update_rect(self, *args):
        self.rect.pos = self.pos
        self.rect.size = self.size

class TimeInputPopup(Popup):
    def __init__(self, callback, **kwargs):
        super().__init__(**kwargs)
        self.callback = callback
        self.title = 'Свое время'
        self.size_hint = (0.8, 0.4)
        
        content = BoxLayout(orientation='vertical', spacing=15, padding=20)
        
        self.input = TextInput(
            hint_text='Введите минуты',
            input_filter='int',
            font_size='24sp',
            multiline=False,
            size_hint_y=None,
            height='60dp'
        )
        content.add_widget(self.input)
        
        btn_layout = BoxLayout(spacing=15, size_hint_y=None, height='70dp')
        btn_ok = TVButton(text='Установить')
        btn_ok.bind(on_press=self.set_time)
        btn_layout.add_widget(btn_ok)
        
        btn_cancel = TVButton(text='Отмена')
        btn_cancel.bind(on_press=self.dismiss)
        btn_layout.add_widget(btn_cancel)
        
        content.add_widget(btn_layout)
        self.content = content
    
    def set_time(self, instance):
        try:
            minutes = int(self.input.text)
            if 1 <= minutes <= 600:
                self.callback(minutes * 60)
                self.dismiss()
            else:
                notification.notify(title='Ошибка', message='Введите от 1 до 600 минут')
        except ValueError:
            notification.notify(title='Ошибка', message='Введите число')

class SleepTimerTV(App):
    timer_seconds = NumericProperty(0)
    timer_active = BooleanProperty(False)
    time_left = NumericProperty(0)
    status_text = StringProperty("Таймер сна для TV")

    def build(self):
        Window.clearcolor = COLORS['background']
        
        layout = BoxLayout(
            orientation='vertical',
            spacing=15,
            padding=[20, 40, 20, 20]
        )
        
        # Заголовок
        self.header = Label(
            text=self.status_text,
            font_size='30sp',
            color=COLORS['text'],
            size_hint_y=None,
            height='70dp'
        )
        layout.add_widget(self.header)
        
        # Таймер
        self.time_display = Label(
            text="00:00",
            font_size='48sp',
            color=COLORS['text']
        )
        layout.add_widget(self.time_display)
        
        # Прогрессбар
        self.progress = ProgressBarLine()
        layout.add_widget(self.progress)
        
        # Кнопки таймера
        btn_grid1 = BoxLayout(spacing=15, size_hint_y=None, height='70dp')
        for minutes in [30, 60]:  # 30 мин и 1 час
            btn = TVButton(
                text=f"{minutes} мин" if minutes < 60 else "1 час",
                on_press=lambda _, m=minutes: self.set_timer(m * 60)
            )
            btn_grid1.add_widget(btn)
        layout.add_widget(btn_grid1)
        
        btn_grid2 = BoxLayout(spacing=15, size_hint_y=None, height='70dp')
        for minutes in [90, 120]:  # 1.5 часа и 2 часа
            btn = TVButton(
                text=f"{minutes//60} часа" if minutes > 60 else "1.5 часа",
                on_press=lambda _, m=minutes: self.set_timer(m * 60)
            )
            btn_grid2.add_widget(btn)
        layout.add_widget(btn_grid2)
        
        # Кнопка своего времени
        custom_btn = TVButton(
            text="Свое время",
            on_press=self.show_custom_time_input
        )
        layout.add_widget(custom_btn)
        
        # Кнопка отмены
        self.cancel_btn = TVButton(
            text="Отменить таймер",
            on_press=self.cancel_timer,
            background_color=get_color_from_hex('#D32F2F'),
            opacity=0,
            disabled=True
        )
        layout.add_widget(self.cancel_btn)
        
        self.bind(
            status_text=lambda _, val: setattr(self.header, 'text', val),
            time_left=self.update_display,
            timer_active=self.toggle_cancel_button
        )
        
        return layout

    def show_custom_time_input(self, instance):
        TimeInputPopup(callback=self.set_timer).open()

    def update_display(self, instance, value):
        mins, secs = divmod(value, 60)
        self.time_display.text = f"{mins:02d}:{secs:02d}"
        self.progress.progress = 100 - (value / self.timer_seconds * 100) if self.timer_seconds else 0

    def toggle_cancel_button(self, instance, value):
        self.cancel_btn.opacity = 1 if value else 0
        self.cancel_btn.disabled = not value

    def set_timer(self, seconds):
        if self.timer_active:
            Clock.unschedule(self.update_timer)
        
        self.timer_seconds = self.time_left = seconds
        self.timer_active = True
        minutes = seconds // 60
        self.status_text = f"Таймер: {minutes} мин" if minutes < 60 else f"Таймер: {minutes//60} часа"
        Clock.schedule_interval(self.update_timer, 1)

    def update_timer(self, dt):
        if self.time_left > 0:
            self.time_left -= 1
            if self.time_left == 180:  # 3 минуты
                self.show_alert()
        else:
            self.timer_complete()

    def show_alert(self):
        notification.notify(
            title='Таймер сна',
            message='Осталось 3 минуты!',
            app_name='Таймер сна TV',
            timeout=10
        )

    def timer_complete(self):
        self.timer_active = False
        self.status_text = "Выключение..."
        try:
            subprocess.run(['am', 'start', '-a', 'android.intent.action.ACTION_REQUEST_SHUTDOWN'])
        except:
            os.system('reboot -p')

    def cancel_timer(self, instance):
        self.timer_active = False
        self.time_left = 0
        self.status_text = "Таймер отменен"
        Clock.unschedule(self.update_timer)

if __name__ == "__main__":
    SleepTimerTV().run()
