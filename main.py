import pyautogui
import time

def click_coordenadas(x, y, pausa):
    print(f"Iniciando auto-clicker en las coordenadas X: {x}, Y: {y}")
    print(f"Hará un clic cada {pausa} segundos.")
    print("Presiona Ctrl+C en esta consola para detenerlo.")
    
    try:
        while True:
            pyautogui.click(x=x, y=y)
            time.sleep(pausa)
            
    except KeyboardInterrupt:
        print("\nAuto-clicker finalizado por el usuario.")

if __name__ == "__main__":
    click_coordenadas(367, 501, 10)