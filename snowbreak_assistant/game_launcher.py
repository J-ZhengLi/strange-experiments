import sys
import ctypes
import json
import subprocess
from types import SimpleNamespace
from time import sleep
from os import path, makedirs

from tkinter import filedialog, messagebox
import pyautogui
import pyscreeze
import pygetwindow


class LauncherConfig():
    # TODO: include language setting
    # Emmm, currently only the path to executable is needed, but maybe there will be
    # more things to configurate in the future? Anyway, I'll just keep it as a class for now.
    def __init__(self, launcher_path):
        self.launcher_path = launcher_path

    def toJson(self):
        return json.dumps(self, indent=4, default=lambda o: o.__dict__)


def working_dir(*paths) -> str:
    res = path.dirname(path.abspath(__file__))
    for sub in paths:
        res = path.join(res, sub)
    return res


# TODO: move these to a separated module, so it can be statically accessed
cache_dir = working_dir("cache")
data_dir = working_dir("data")
localization = "zh_cn"


def get_launcher_exe_path() -> str:
    """
    Return a cached path of the game's launcher.
    If no cached can be found, ask the user to manually pick one then cache it.
    """
    config_path = path.join(cache_dir, "config.json")

    if not path.isfile(config_path):
        # Ensure there is a data dir
        makedirs(cache_dir, exist_ok=True)
        # Ensure config file
        open(config_path, "w").close()

    with open(config_path, "r+", encoding="utf8") as config_file:
        content = config_file.read()
        if content:
            config = json.loads(
                content, object_hook=lambda d: LauncherConfig(**d))
        else:
            # Prompt user to select one then store it.
            file_path = ""
            while not file_path:
                if not messagebox.askokcancel(
                    message="looks like you are running this program for the first time, "
                        + "you'll need to select the game launcher binary manually.",
                    title="initializing"
                ):
                    break

                file_path = filedialog.askopenfilename(
                    title="please select the game launcher (snow_launcher.exe)",
                    filetypes=[("Executable files", "*.exe"),
                               ('All files', '*.*')]
                )
            config = LauncherConfig(file_path)
            config_file.write(config.toJson())
        return config.launcher_path


def launch_game():
    exe_path = get_launcher_exe_path()
    # For some reason, this game's launcher requires admin privilage... well...
    # I just copy-pasted this following code from stackoverflow, what is it do?
    # It re-run this script with admin rights, but why `> 32`? I have no idea
    if not ctypes.windll.shell32.IsUserAnAdmin() and ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1) > 32:
        exit()

    # This is actually starting the game launcher, not the game itself.
    # We still need to autoclick the `start` button to launch the game.
    subprocess.Popen([exe_path])

    localization_dir = path.join(data_dir, localization)
    # Load window title names
    with open(path.join(localization_dir, "local.json"), "r", encoding="utf8") as i18n_file:
        # TODO: Create a class for this
        config = json.loads(
            i18n_file.read(), object_hook=lambda d: SimpleNamespace(**d))
        launcher_title = config.launcher_title
        game_title = config.game_title

    start_btn_loc = None
    while start_btn_loc is None:
        try:
            # TODO: Can we get the pop-up window instead of searching on the whole screen?
            start_btn_loc = pyautogui.locateOnWindow(
                path.join(localization_dir, "start_game.png"), launcher_title, confidence=0.9)
            if start_btn_loc is not None:
                x, y = pyautogui.center(start_btn_loc)
                pyautogui.click(x, y)
                break
        except pyscreeze.PyScreezeException:
            print("waiting for game launcher window...")
        except pyautogui.ImageNotFoundException:
            print("locating 'start game' button...")
        finally:
            sleep(1)

    # debug code to check if the game window can be found after launching it
    for retry_counter in range(0, 30):
        if retry_counter == 30:
            break
        if pygetwindow.getWindowsWithTitle(game_title):
            print("Successfully locate the game window")
            return
        sleep(1)
    print("did not locate the game window")
    input("press Enter to continue...")
    exit(1)
