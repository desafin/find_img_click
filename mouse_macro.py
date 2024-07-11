import cv2
import numpy as np
import pyautogui
import time
import tkinter as tk


def get_screenshot(region=None):
    screenshot = pyautogui.screenshot(region=region)
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    return screenshot


def find_image_on_screen(template_path, region=None):
    screenshot = get_screenshot(region)
    template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)

    sift = cv2.SIFT_create()
    kp1, des1 = sift.detectAndCompute(template, None)
    kp2, des2 = sift.detectAndCompute(screenshot, None)

    bf = cv2.BFMatcher()
    matches = bf.knnMatch(des1, des2, k=2)

    good_matches = []
    for m, n in matches:
        if m.distance < 0.75 * n.distance:
            good_matches.append(m)

    if len(good_matches) > 10:
        src_pts = np.float32([kp1[m.queryIdx].pt for m in good_matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in good_matches]).reshape(-1, 1, 2)

        M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
        h, w = template.shape
        pts = np.float32([[0, 0], [0, h - 1], [w - 1, h - 1], [w - 1, 0]]).reshape(-1, 1, 2)
        dst = cv2.perspectiveTransform(pts, M)

        center_x = int(np.mean(dst[:, 0, 0]))
        center_y = int(np.mean(dst[:, 0, 1]))

        return (center_x, center_y)
    return None


# 구역 선택을 위한 tkinter 창
class RegionSelector(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Select Region")
        self.attributes("-fullscreen", True)
        self.attributes("-alpha", 0.3)  # 투명도 설정
        self.canvas = tk.Canvas(self, cursor="cross")
        self.canvas.pack(fill="both", expand=True)
        self.start_x = None
        self.start_y = None
        self.rect = None
        self.region = None
        self.bind("<ButtonPress-1>", self.on_button_press)
        self.bind("<B1-Motion>", self.on_mouse_drag)
        self.bind("<ButtonRelease-1>", self.on_button_release)
        self.bind("<KeyPress-q>", self.on_quit)

    def on_button_press(self, event):
        self.start_x = event.x
        self.start_y = event.y
        if self.rect:
            self.canvas.delete(self.rect)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline="red")

    def on_mouse_drag(self, event):
        cur_x, cur_y = (event.x, event.y)
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_button_release(self, event):
        end_x, end_y = (event.x, event.y)
        self.region = (
        min(self.start_x, end_x), min(self.start_y, end_y), abs(end_x - self.start_x), abs(end_y - self.start_y))
        self.quit()  # 구역 지정 후 창 종료

    def on_quit(self, event):
        self.region = None
        self.quit()


def get_region():
    selector = RegionSelector()
    selector.mainloop()
    region = selector.region
    selector.destroy()  # RegionSelector 창을 완전히 제거
    return region


def show_click_effect(x, y):
    effect_duration = 0.5  # 효과 지속 시간 (초)
    root = tk.Tk()
    root.overrideredirect(True)  # 창 테두리 없애기
    root.attributes("-topmost", True)  # 항상 위에 표시
    root.geometry(f"+{x}+{y}")
    canvas = tk.Canvas(root, width=50, height=50, highlightthickness=0)
    canvas.pack()
    oval = canvas.create_oval(10, 10, 40, 40, outline="red", width=2)
    root.after(int(effect_duration * 1000), root.destroy)  # 효과 지속 시간 후 창 닫기
    root.mainloop()


def main():
    region = get_region()  # GUI로 구역 선택

    if region is None:
        print("No region selected. Exiting...")
        return

    print(f"Selected region: {region}")

    while True:
        try:
            result = find_image_on_screen('daily_check.png', region)
            if result is not None:
                center_x, center_y = result
                print(f"Clicking at: ({center_x}, {center_y})")
                pyautogui.click(center_x, center_y)
                show_click_effect(center_x, center_y)  # 클릭 효과 표시
                time.sleep(0.5)
            else:
                print("image not found in the region")
                time.sleep(0.5)
        except Exception as e:
            print(f"Exception occurred: {e}")
        time.sleep(1)  # Main loop delay


if __name__ == "__main__":
    main()
