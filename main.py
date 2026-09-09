import pyautogui
import time

def click_y_regresa(x, y, pausa):
    print(f"Iniciando AutoClicker en X: {x}, Y: {y}")
    
    try:
        while True:
            posicion_actual = pyautogui.position()
            
            pyautogui.moveTo(x, y, duration=1.0)
            pyautogui.click()
            
            pyautogui.moveTo(posicion_actual.x, posicion_actual.y, duration=0.5)
            
            time.sleep(pausa)
            
    except KeyboardInterrupt:
        print("\nFinalizado.")

if __name__ == "__main__":
    click_y_regresa(367, 501, 10)