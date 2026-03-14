import os
from pathlib import Path

CONFIG_FILE = ".config/hotdot"
PROFILES_FILE = ".hotdot/profiles"
ACTIVE_PROFILE_FILE = ".hotdot/active_profile"

def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "hotdot"

def active_repo_file():
    return config_dir() / "active-repo"

def get_active_repo():
    line = None
    with open(active_repo_file(), "r+") as f:
        line = f.readline()
        f.close()
    return line

def profile_exist(name):
    with open(get_active_repo()+ "/" + PROFILES_FILE, "r", -1, "utf_8") as f:
        for line in f:
            if (name == line.strip("\n")):
                print('profile already exist')
                f.close()
                return True
        f.close()
    return False

def cmd_profile(args):
    if profile_exist(args.name):
        return 0

    with open(get_active_repo()+ "/" + PROFILES_FILE, "a") as f:
        f.write(args.name + "\n")
        f.close()
    print('created new profile', args.name)
