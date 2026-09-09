import tkinter as tk
from tkinter import font as tkfont
import threading
import time
import pyautogui
import keyboard
import ctypes
from datetime import datetime

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(1)
except Exception:
    pass

THEME = {
    "bg_primary": "#0a0a0a",
    "bg_panel": "#111111",
    "bg_input": "#0d0d0d",
    "bg_button": "#0f0f0f",
    "bg_button_hover": "#1a1a1a",
    "bg_titlebar": "#050505",
    "bg_log": "#080808",
    "fg_green": "#00ff41",
    "fg_green_dim": "#00cc33",
    "fg_green_bright": "#39ff14",
    "fg_cyan": "#00e5ff",
    "fg_red": "#ff0040",
    "fg_gray": "#555555",
    "fg_white": "#cccccc",
    "border_green": "#00ff41",
    "border_dim": "#1a3a1a",
    "font_mono": "Consolas",
    "font_mono_alt": "Courier New",
}


class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.overrideredirect(True)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=THEME["bg_primary"])

        self.window_width = 460
        self.window_height = 560
        screen_w = self.root.winfo_screenwidth()
        screen_h = self.root.winfo_screenheight()
        pos_x = screen_w - self.window_width - 30
        pos_y = (screen_h - self.window_height) // 2
        self.root.geometry(f"{self.window_width}x{self.window_height}+{pos_x}+{pos_y}")

        self.x = 0
        self.y = 0
        self.corriendo = False
        self.pausa = 10
        self.click_count = 0
        self.click_type = tk.StringVar(value="left")
        self.pulse_state = False
        self.pulse_after_id = None
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.captura_activa = False

        self.mono_font = self._resolve_font()

        self._build_border_frame()
        self._build_titlebar()
        self._build_status_section()
        self._build_config_section()
        self._build_buttons_section()
        self._build_log_section()

        keyboard.add_hotkey('esc', self.detener)
        self._start_pulse()

    def _resolve_font(self):
        available = tkfont.families()
        if THEME["font_mono"] in available:
            return THEME["font_mono"]
        if THEME["font_mono_alt"] in available:
            return THEME["font_mono_alt"]
        return "TkFixedFont"

    def _build_border_frame(self):
        self.border_frame = tk.Frame(
            self.root,
            bg=THEME["border_dim"],
            highlightthickness=0,
        )
        self.border_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.main_container = tk.Frame(
            self.border_frame,
            bg=THEME["bg_primary"],
        )
        self.main_container.pack(fill=tk.BOTH, expand=True)

    def _build_titlebar(self):
        titlebar = tk.Frame(self.main_container, bg=THEME["bg_titlebar"], height=36)
        titlebar.pack(fill=tk.X)
        titlebar.pack_propagate(False)

        titlebar.bind("<Button-1>", self._start_drag)
        titlebar.bind("<B1-Motion>", self._on_drag)

        title_label = tk.Label(
            titlebar,
            text="AUTOCLICKER ENTERPRISE",
            font=(self.mono_font, 10, "bold"),
            fg=THEME["fg_green"],
            bg=THEME["bg_titlebar"],
        )
        title_label.pack(side=tk.LEFT, padx=12)
        title_label.bind("<Button-1>", self._start_drag)
        title_label.bind("<B1-Motion>", self._on_drag)

        version_label = tk.Label(
            titlebar,
            text="v1.0",
            font=(self.mono_font, 8),
            fg=THEME["fg_gray"],
            bg=THEME["bg_titlebar"],
        )
        version_label.pack(side=tk.LEFT, padx=(0, 6))
        version_label.bind("<Button-1>", self._start_drag)
        version_label.bind("<B1-Motion>", self._on_drag)

        btn_close = tk.Label(
            titlebar,
            text=" X ",
            font=(self.mono_font, 10, "bold"),
            fg=THEME["fg_red"],
            bg=THEME["bg_titlebar"],
            cursor="hand2",
        )
        btn_close.pack(side=tk.RIGHT, padx=(0, 6))
        btn_close.bind("<Button-1>", lambda e: self._close_app())
        btn_close.bind("<Enter>", lambda e: btn_close.config(bg="#2a0010"))
        btn_close.bind("<Leave>", lambda e: btn_close.config(bg=THEME["bg_titlebar"]))

        btn_minimize = tk.Label(
            titlebar,
            text=" _ ",
            font=(self.mono_font, 10),
            fg=THEME["fg_gray"],
            bg=THEME["bg_titlebar"],
            cursor="hand2",
        )
        btn_minimize.pack(side=tk.RIGHT, padx=(0, 2))
        btn_minimize.bind("<Button-1>", lambda e: self._minimize_app())
        btn_minimize.bind("<Enter>", lambda e: btn_minimize.config(fg=THEME["fg_white"]))
        btn_minimize.bind("<Leave>", lambda e: btn_minimize.config(fg=THEME["fg_gray"]))

        separator = tk.Frame(self.main_container, bg=THEME["border_dim"], height=1)
        separator.pack(fill=tk.X)

    def _build_status_section(self):
        status_frame = tk.Frame(self.main_container, bg=THEME["bg_primary"])
        status_frame.pack(fill=tk.X, padx=16, pady=(14, 0))

        row_estado = tk.Frame(status_frame, bg=THEME["bg_primary"])
        row_estado.pack(fill=tk.X, pady=2)

        self.pulse_indicator = tk.Canvas(
            row_estado, width=10, height=10,
            bg=THEME["bg_primary"], highlightthickness=0,
        )
        self.pulse_indicator.pack(side=tk.LEFT, padx=(0, 8), pady=2)
        self.pulse_dot = self.pulse_indicator.create_oval(1, 1, 9, 9, fill=THEME["fg_gray"], outline="")

        self.lbl_estado = tk.Label(
            row_estado,
            text="[SYS] Estado: EN ESPERA",
            font=(self.mono_font, 10),
            fg=THEME["fg_green_dim"],
            bg=THEME["bg_primary"],
            anchor="w",
        )
        self.lbl_estado.pack(side=tk.LEFT, fill=tk.X)

        self.lbl_target = tk.Label(
            status_frame,
            text="[TARGET] Coordenadas: ---",
            font=(self.mono_font, 10),
            fg=THEME["fg_gray"],
            bg=THEME["bg_primary"],
            anchor="w",
        )
        self.lbl_target.pack(fill=tk.X, pady=2)

        self.lbl_counter = tk.Label(
            status_frame,
            text="[STATS] Clics ejecutados: 0000",
            font=(self.mono_font, 10),
            fg=THEME["fg_gray"],
            bg=THEME["bg_primary"],
            anchor="w",
        )
        self.lbl_counter.pack(fill=tk.X, pady=2)

    def _build_config_section(self):
        sep = tk.Frame(self.main_container, bg=THEME["border_dim"], height=1)
        sep.pack(fill=tk.X, padx=16, pady=(12, 0))

        config_frame = tk.Frame(self.main_container, bg=THEME["bg_primary"])
        config_frame.pack(fill=tk.X, padx=16, pady=(10, 0))

        interval_row = tk.Frame(config_frame, bg=THEME["bg_primary"])
        interval_row.pack(fill=tk.X, pady=4)

        tk.Label(
            interval_row,
            text="Intervalo (seg):",
            font=(self.mono_font, 9),
            fg=THEME["fg_green_dim"],
            bg=THEME["bg_primary"],
        ).pack(side=tk.LEFT)

        self.interval_var = tk.StringVar(value="10")
        self.interval_entry = tk.Entry(
            interval_row,
            textvariable=self.interval_var,
            font=(self.mono_font, 10),
            fg=THEME["fg_cyan"],
            bg=THEME["bg_input"],
            insertbackground=THEME["fg_cyan"],
            highlightthickness=1,
            highlightcolor=THEME["fg_green"],
            highlightbackground=THEME["border_dim"],
            relief=tk.FLAT,
            width=8,
            justify=tk.CENTER,
        )
        self.interval_entry.pack(side=tk.LEFT, padx=(10, 0))
        self.interval_entry.bind("<FocusOut>", self._update_interval)
        self.interval_entry.bind("<Return>", self._update_interval)

        click_row = tk.Frame(config_frame, bg=THEME["bg_primary"])
        click_row.pack(fill=tk.X, pady=(6, 0))

        tk.Label(
            click_row,
            text="Tipo de clic:",
            font=(self.mono_font, 9),
            fg=THEME["fg_green_dim"],
            bg=THEME["bg_primary"],
        ).pack(side=tk.LEFT)

        click_options = [("IZQ", "left"), ("DER", "right"), ("2xCLIC", "double")]
        for label_text, value in click_options:
            rb = tk.Radiobutton(
                click_row,
                text=label_text,
                variable=self.click_type,
                value=value,
                font=(self.mono_font, 9),
                fg=THEME["fg_green_dim"],
                bg=THEME["bg_primary"],
                selectcolor=THEME["bg_panel"],
                activebackground=THEME["bg_primary"],
                activeforeground=THEME["fg_green"],
                highlightthickness=0,
                relief=tk.FLAT,
            )
            rb.pack(side=tk.LEFT, padx=(10, 0))

    def _build_buttons_section(self):
        sep = tk.Frame(self.main_container, bg=THEME["border_dim"], height=1)
        sep.pack(fill=tk.X, padx=16, pady=(12, 0))

        btn_frame = tk.Frame(self.main_container, bg=THEME["bg_primary"])
        btn_frame.pack(fill=tk.X, padx=16, pady=(10, 0))

        self.btn_capturar = self._create_styled_button(
            btn_frame,
            "[ CAPTURAR POSICION  (C) ]",
            self.preparar_captura,
            THEME["fg_cyan"],
        )
        self.btn_capturar.pack(fill=tk.X, pady=3)

        self.btn_iniciar = self._create_styled_button(
            btn_frame,
            "[       INICIAR      (F5) ]",
            self.iniciar,
            THEME["fg_green"],
        )
        self.btn_iniciar.pack(fill=tk.X, pady=3)
        self.btn_iniciar.config(state=tk.DISABLED)

        self.btn_detener = self._create_styled_button(
            btn_frame,
            "[      DETENER      (ESC) ]",
            self.detener,
            THEME["fg_red"],
        )
        self.btn_detener.pack(fill=tk.X, pady=3)

    def _create_styled_button(self, parent, text, command, fg_color):
        btn = tk.Button(
            parent,
            text=text,
            command=command,
            font=(self.mono_font, 10, "bold"),
            fg=fg_color,
            bg=THEME["bg_button"],
            activebackground=THEME["bg_button_hover"],
            activeforeground=fg_color,
            highlightthickness=1,
            highlightcolor=fg_color,
            highlightbackground=THEME["border_dim"],
            relief=tk.FLAT,
            cursor="hand2",
            pady=6,
            disabledforeground=THEME["fg_gray"],
        )
        btn.bind("<Enter>", lambda e, b=btn, c=fg_color: self._btn_hover_enter(b, c))
        btn.bind("<Leave>", lambda e, b=btn: self._btn_hover_leave(b))
        return btn

    def _btn_hover_enter(self, btn, color):
        if btn.cget("state") != "disabled":
            btn.config(bg=THEME["bg_button_hover"], highlightbackground=color)

    def _btn_hover_leave(self, btn):
        btn.config(bg=THEME["bg_button"], highlightbackground=THEME["border_dim"])

    def _build_log_section(self):
        sep = tk.Frame(self.main_container, bg=THEME["border_dim"], height=1)
        sep.pack(fill=tk.X, padx=16, pady=(12, 0))

        log_header = tk.Label(
            self.main_container,
            text="[LOG] Registro de Actividad",
            font=(self.mono_font, 9),
            fg=THEME["fg_gray"],
            bg=THEME["bg_primary"],
            anchor="w",
        )
        log_header.pack(fill=tk.X, padx=16, pady=(6, 2))

        log_frame = tk.Frame(
            self.main_container,
            bg=THEME["border_dim"],
            highlightthickness=0,
        )
        log_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=(0, 12))

        self.log_text = tk.Text(
            log_frame,
            font=(self.mono_font, 8),
            fg=THEME["fg_green_dim"],
            bg=THEME["bg_log"],
            insertbackground=THEME["fg_green"],
            highlightthickness=0,
            relief=tk.FLAT,
            wrap=tk.WORD,
            state=tk.DISABLED,
            height=8,
            padx=8,
            pady=6,
        )
        self.log_text.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        self.log_text.tag_configure("sys", foreground=THEME["fg_cyan"])
        self.log_text.tag_configure("exec", foreground=THEME["fg_green"])
        self.log_text.tag_configure("target", foreground=THEME["fg_green_bright"])
        self.log_text.tag_configure("error", foreground=THEME["fg_red"])
        self.log_text.tag_configure("timestamp", foreground=THEME["fg_gray"])

        self._log("SYS", "Motor inicializado", "sys")
        self._log("SYS", "Esperando captura de coordenadas", "sys")

    def _log(self, prefix, message, tag="sys"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.config(state=tk.NORMAL)
        self.log_text.insert(tk.END, f"[{timestamp}] ", "timestamp")
        self.log_text.insert(tk.END, f"{prefix} > {message}\n", tag)
        self.log_text.see(tk.END)
        self.log_text.config(state=tk.DISABLED)

    def _start_pulse(self):
        if self.corriendo:
            color = THEME["fg_green"] if self.pulse_state else THEME["fg_green_dim"]
        else:
            color = THEME["fg_gray"] if self.pulse_state else THEME["bg_primary"]
        self.pulse_indicator.itemconfig(self.pulse_dot, fill=color)
        self.pulse_state = not self.pulse_state
        self.pulse_after_id = self.root.after(700, self._start_pulse)

    def _start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y

    def _on_drag(self, event):
        new_x = self.root.winfo_x() + event.x - self.drag_start_x
        new_y = self.root.winfo_y() + event.y - self.drag_start_y
        self.root.geometry(f"+{new_x}+{new_y}")

    def _close_app(self):
        self.corriendo = False
        if self.pulse_after_id:
            self.root.after_cancel(self.pulse_after_id)
        try:
            keyboard.unhook_all_hotkeys()
        except Exception:
            pass
        self.root.destroy()

    def _minimize_app(self):
        self.root.overrideredirect(False)
        self.root.iconify()
        self.root.after(100, self._restore_overrideredirect)

    def _restore_overrideredirect(self):
        def on_map(event):
            self.root.overrideredirect(True)
            self.root.attributes("-topmost", True)
            self.root.unbind("<Map>")
        self.root.bind("<Map>", on_map)

    def _update_interval(self, event=None):
        try:
            value = float(self.interval_var.get())
            if value <= 0:
                raise ValueError
            self.pausa = value
            self._log("SYS", f"Intervalo actualizado: {value}s", "sys")
        except ValueError:
            self.interval_var.set(str(self.pausa))
            self._log("SYS", "Valor de intervalo invalido", "error")

    def preparar_captura(self):
        if self.captura_activa:
            return
        self.captura_activa = True
        self.lbl_estado.config(text="[SYS] Coloca el mouse y presiona 'C'", fg=THEME["fg_cyan"])
        self._log("SYS", "Captura activada - posicione el cursor y presione C", "sys")
        keyboard.add_hotkey('c', self._on_captura_key, suppress=False)

    def _on_captura_key(self):
        if not self.captura_activa:
            return
        self.captura_activa = False
        try:
            keyboard.remove_hotkey('c')
        except Exception:
            pass
        self.root.after(0, self.capturar)

    def capturar(self):
        self.x, self.y = pyautogui.position()
        self.lbl_estado.config(
            text=f"[SYS] Estado: LISTO",
            fg=THEME["fg_green_dim"],
        )
        self.lbl_target.config(
            text=f"[TARGET] Coordenadas: X={self.x} | Y={self.y}",
            fg=THEME["fg_green"],
        )
        self.btn_iniciar.config(state=tk.NORMAL)
        self._log("TARGET", f"Coordenadas fijadas: X={self.x} Y={self.y}", "target")

    def iniciar(self):
        if self.corriendo:
            return
        self._update_interval()
        self.corriendo = True
        self.click_count = 0
        self.lbl_counter.config(
            text=f"[STATS] Clics ejecutados: 0000",
            fg=THEME["fg_cyan"],
        )
        self.lbl_estado.config(
            text="[SYS] Estado: EJECUTANDO",
            fg=THEME["fg_green"],
        )
        self.btn_iniciar.config(state=tk.DISABLED)
        self.btn_capturar.config(state=tk.DISABLED)
        self._log("SYS", f"Secuencia iniciada | Intervalo: {self.pausa}s | Tipo: {self.click_type.get()}", "exec")
        threading.Thread(target=self.bucle, daemon=True).start()

    def detener(self):
        was_running = self.corriendo
        self.corriendo = False
        self.lbl_estado.config(text="[SYS] Estado: DETENIDO", fg=THEME["fg_red"])
        self.btn_iniciar.config(state=tk.NORMAL)
        self.btn_capturar.config(state=tk.NORMAL)
        if was_running:
            self._log("SYS", f"Secuencia abortada | Total clics: {self.click_count}", "error")

    def mostrar_marca_visual(self):
        marca = tk.Toplevel(self.root)
        marca.overrideredirect(True)
        marca.attributes("-topmost", True)
        marca.attributes("-transparentcolor", "black")
        marca.geometry(f"50x50+{self.x-25}+{self.y-25}")

        canvas = tk.Canvas(marca, width=50, height=50, bg="black", highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 45, 45, outline=THEME["fg_green"], width=3)
        canvas.create_oval(15, 15, 35, 35, outline=THEME["fg_cyan"], width=2)

        self.root.after(250, marca.destroy)

    def click_rapido(self):
        pos_x, pos_y = pyautogui.position()
        start_time = time.perf_counter()

        click_mode = self.click_type.get()

        ctypes.windll.user32.SetCursorPos(self.x, self.y)

        if click_mode == "left":
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
        elif click_mode == "right":
            ctypes.windll.user32.mouse_event(8, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(16, 0, 0, 0, 0)
        elif click_mode == "double":
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
            ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

        ctypes.windll.user32.SetCursorPos(pos_x, pos_y)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)

        elapsed = (time.perf_counter() - start_time) * 1000
        self.click_count += 1

        self.root.after(0, self._update_click_ui, elapsed)

    def _update_click_ui(self, elapsed_ms):
        self.lbl_counter.config(
            text=f"[STATS] Clics ejecutados: {self.click_count:04d}",
        )
        self._log("EXEC", f"Clic #{self.click_count:03d} despachado en {elapsed_ms:.1f}ms", "exec")

    def bucle(self):
        while self.corriendo:
            self.mostrar_marca_visual()
            self.click_rapido()
            time.sleep(self.pausa)


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AutoClickerApp(ventana)
    ventana.mainloop()