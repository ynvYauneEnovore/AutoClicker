import pyautogui
import time

print("Presiona Ctrl+C para detener el script")
try:
    while True:
        x, y = pyautogui.position()
        print(f"X: {x} | Y: {y}", end="\r")
        time.sleep(0.1)
except KeyboardInterrupt:
    print("\nFinalizado")