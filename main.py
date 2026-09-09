import pyautogui
import time

def click_coordenadas_visible(x, y, pausa):
    print(f"Iniciando auto-clicker en X: {x}, Y: {y}")
    
    try:
        while True:
            pyautogui.moveTo(x, y, duration=1.5)
            pyautogui.click()
            time.sleep(pausa)
            
    except KeyboardInterrupt:
        print("\nFinalizado.")

if __name__ == "__main__":
    click_coordenadas_visible(367, 501, 10)