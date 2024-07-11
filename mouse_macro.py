import pyautogui
import time

def main():
    while True:
        try:
            pos = pyautogui.locateOnScreen('forgespirit.png', confidence=0.2)
            if pos is not None:
                print("I can see it.")
                center_x = pos.left + pos.width // 2
                center_y = pos.top + pos.height // 2
                print(f"Clicking at: ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                time.sleep(0.5)
            else:
                print("image not found")
                time.sleep(0.5)
        except Exception as e:
            print(f"image not found: {e}")
        time.sleep(1)  # Main loop delay

if __name__ == "__main__":
    main()
