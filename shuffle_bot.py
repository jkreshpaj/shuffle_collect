import cv2
import numpy as np
import pyautogui
import time
import mss

def find_and_click(template_path, confidence, monitor, monitor_offset, click_coords=None):
    """
    Look for the specified template on the screen, and if found, click on it.

    Args:
        template_path (str): Path to the template image.
        confidence (float): Matching confidence threshold.
        monitor (dict): Screen region to capture.
        monitor_offset (tuple): (left, top) offset of the monitor.
        click_coords (tuple): (x_offset, y_offset) relative to the matched center, for precise clicking.

    Returns:
        bool: True if the template was found and clicked, False otherwise.
    """
    with mss.mss() as sct:
        screenshot = np.array(sct.grab(monitor))
        screenshot = cv2.cvtColor(screenshot, cv2.COLOR_BGRA2BGR)

    template = cv2.imread(template_path, cv2.IMREAD_UNCHANGED)
    if template is None:
        print(f"Error: Template {template_path} not found!")
        return False

    if template.shape[2] == 4:
        template = cv2.cvtColor(template, cv2.COLOR_BGRA2BGR)

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)

    if max_val >= confidence:
        print(f"Match found for {template_path} with confidence {max_val:.2f}.")
        template_height, template_width = template.shape[:2]
        center_x = max_loc[0] + template_width // 2 + monitor_offset[0]
        center_y = max_loc[1] + template_height // 2 + monitor_offset[1]

        if click_coords:
            center_x += click_coords[0]
            center_y += click_coords[1]

        pyautogui.moveTo(center_x, center_y + 45, duration=0.5)
        pyautogui.click()
        return True
    else:
        print(f"No match found for {template_path}.")
        return False

def monitor_and_click(first_template, dialog_template, monitor_index=1, confidence=0.8):
    """
    Continuously monitors the screen for the first template and interacts with the dialog.

    Args:
        first_template (str): Path to the first template image.
        dialog_template (str): Path to the dialog template image.
        monitor_index (int): Monitor index (1 for primary monitor, etc.).
        confidence (float): Matching confidence threshold.

    Returns:
        None
    """
    with mss.mss() as sct:
        monitors = sct.monitors
        if monitor_index >= len(monitors):
            print(f"Invalid monitor index {monitor_index}. Only {len(monitors) - 1} monitors available.")
            return

        monitor = monitors[monitor_index]
        monitor_offset = (monitor["left"], monitor["top"])
        print(f"Using monitor {monitor_index}: {monitor}")

        last_clicked_time = 0

        while True:
            current_time = time.time()

            if current_time - last_clicked_time >= 3600:
                print("Looking for the first template...")
                if find_and_click(first_template, confidence, monitor, monitor_offset):
                    time.sleep(3)

                    print("Looking for the dialog template...")
                    if find_and_click(dialog_template, confidence, monitor, monitor_offset, click_coords=(0, 200)):  # Adjust `click_coords` as needed
                        print("Successfully clicked on the dialog.")
                        last_clicked_time = current_time
                    else:
                        print("Dialog not found.")
                else:
                    print("First template not found.")
            else:
                #print("Waiting for the next cycle...")
                time.sleep(5)

if __name__ == "__main__":
    first_template_path = "bonus_unclaimed.png"
    dialog_template_path = "dialog_unclaimed.png"

    monitor_index = 2

    monitor_and_click(first_template_path, dialog_template_path, monitor_index=monitor_index, confidence=0.8)
