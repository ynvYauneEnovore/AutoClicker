import tkinter as tk
import threading
import time
import pyautogui
import keyboard
import ctypes

class AutoClickerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Panel - AutoClicker")
        self.root.geometry("350x200")
        self.root.attributes("-topmost", True)
        
        self.x = 0
        self.y = 0
        self.corriendo = False
        self.pausa = 10 
        
        self.lbl_estado = tk.Label(root, text="Esperando coordenadas...", font=("Arial", 12))
        self.lbl_estado.pack(pady=20)
        
        self.btn_capturar = tk.Button(root, text="1. Capturar Posición (Tecla C)", command=self.preparar_captura)
        self.btn_capturar.pack(pady=5)
        
        self.btn_iniciar = tk.Button(root, text="2. Iniciar", command=self.iniciar, state=tk.DISABLED)
        self.btn_iniciar.pack(pady=5)
        
        self.btn_detener = tk.Button(root, text="Detener Emergencia (ESC)", command=self.detener, fg="red")
        self.btn_detener.pack(pady=5)
        
        keyboard.add_hotkey('esc', self.detener)
        keyboard.add_hotkey('c', self.capturar)

    def preparar_captura(self):
        self.lbl_estado.config(text="Coloca el mouse y presiona 'C'")

    def capturar(self):
        self.x, self.y = pyautogui.position()
        self.lbl_estado.config(text=f"Fijado en: X={self.x} | Y={self.y}")
        self.btn_iniciar.config(state=tk.NORMAL)

    def iniciar(self):
        if not self.corriendo:
            self.corriendo = True
            self.lbl_estado.config(text="¡EJECUTANDO! Presiona ESC para cancelar", fg="green")
            threading.Thread(target=self.bucle, daemon=True).start()

    def detener(self):
        self.corriendo = False
        self.lbl_estado.config(text="DETENIDO", fg="red")
        self.btn_iniciar.config(state=tk.NORMAL)

    def mostrar_marca_visual(self):
        marca = tk.Toplevel(self.root)
        marca.overrideredirect(True)
        marca.attributes("-topmost", True)
        marca.attributes("-transparentcolor", "white")
        marca.geometry(f"50x50+{self.x-25}+{self.y-25}")
        
        canvas = tk.Canvas(marca, width=50, height=50, bg="white", highlightthickness=0)
        canvas.pack()
        canvas.create_oval(5, 5, 45, 45, outline="red", width=4)
        
        self.root.after(300, marca.destroy)

    def click_rapido(self):
        pos_x, pos_y = pyautogui.position()
        
        ctypes.windll.user32.SetCursorPos(self.x, self.y)
        ctypes.windll.user32.mouse_event(2, 0, 0, 0, 0)
        ctypes.windll.user32.mouse_event(4, 0, 0, 0, 0)
        ctypes.windll.user32.SetCursorPos(pos_x, pos_y)

    def bucle(self):
        while self.corriendo:
            self.mostrar_marca_visual()
            self.click_rapido()
            time.sleep(self.pausa)

if __name__ == "__main__":
    ventana = tk.Tk()
    app = AutoClickerApp(ventana)
    ventana.mainloop()