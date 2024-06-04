
import json
import subprocess
from os import path, makedirs

from tkinter import filedialog, messagebox


class LauncherConfig():
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


def get_launcher_exe_path() -> str:
    """
    Return a cached path of the game's launcher.
    If no cached can be found, ask the user to manually pick one then cache it.
    """
    # TODO: move these to a separated module, so it can be statically accessed
    cache_dir = working_dir("cache")
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
    subprocess.call([exe_path], shell=True)
    print("launcher stopped")
    # TODO: use opencv to find the button and launch the actual game
