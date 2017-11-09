import pyautogui


def wait_for_screen_to_show(picture_path, prompt_when_done):
    while True:
        if pyautogui.locateOnScreen(picture_path) is not None:
            break
    print prompt_when_done


def click_button(button_picture_path):
    wait_for_screen_to_show(button_picture_path, 'Button {} is visible.'.format(button_picture_path))
    cors = pyautogui.locateOnScreen(button_picture_path)
    pyautogui.click(cors[0] + int(cors[2] / 2), cors[1] + int(cors[3] / 2))
