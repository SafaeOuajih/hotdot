import os
from pathlib import Path
from hotdot.__init__ import __version__

VERSION_FILE = "hotdot.version"
CONFIG_FILE = ".config/hotdot"
PROFILES_FILE = ".hotdot/profiles"
ACTIVE_PROFILE_FILE = ".hotdot/active_profile"

def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "hotdot"

def active_repo_file():
    return config_dir() / "active-repo"

def create_version_file(version):
    with open(VERSION_FILE, 'w+') as f:
        f.write("hotdot " + version + "\n")
        f.close()

def create_profiles_file():
    with open(PROFILES_FILE, 'w+') as f:
        f.close()

def create_active_profile_file():
    with open(ACTIVE_PROFILE_FILE, 'w+') as f:
        f.close()

def create_active_repo(path):
    config_dir().mkdir(parents=True, exist_ok=True)
    with open(active_repo_file(),'w+') as f:
        f.write(path)

def cmd_init(args):
    create_version_file(__version__)
    repo = Path(args.path).expanduser().resolve()
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "stowable").mkdir(parents=True, exist_ok=True)
    (repo / "sources").mkdir(parents=True, exist_ok=True)
    (repo / ".hotdot").mkdir(parents=True, exist_ok=True)
    create_active_profile_file()
    create_profiles_file()
    create_active_repo(str(repo))

