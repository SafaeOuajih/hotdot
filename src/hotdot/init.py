import os
import subprocess
from pathlib import Path
from hotdot.__init__ import __version__

VERSION_FILE = "hotdot.version"
PROFILES_FILE = ".hotdot/profiles"
ACTIVE_PROFILE_FILE = ".hotdot/active_profile"

def config_dir():
    base = os.environ.get("XDG_CONFIG_HOME") or os.path.join(os.path.expanduser("~"), ".config")
    return Path(base) / "hotdot"

def active_repo_file():
    return config_dir() / "active-repo"

def create_version_file(repo, version):
    with open(repo / VERSION_FILE, 'w+') as f:
        f.write("hotdot " + version + "\n")

def create_profiles_file(repo):
    path = repo / PROFILES_FILE
    if path.exists():
        return
    with open(path, 'w+') as f:
        pass

def create_active_profile_file(repo):
    path = repo / ACTIVE_PROFILE_FILE
    if path.exists():
        return
    with open(path, 'w+') as f:
        pass

def create_gitignore(repo):
    gitignore = repo / ".gitignore"
    if gitignore.exists():
        return
    with open(gitignore, 'w+') as f:
        f.write(".hotdot/active_profile\n.hotdot/state\n.hotdot/stage\n")

def init_git_repo(repo):
    if (repo / ".git").exists():
        return
    subprocess.run(["git", "init", "-q", str(repo)], check=True)

def create_active_repo(path):
    config_dir().mkdir(parents=True, exist_ok=True)
    with open(active_repo_file(),'w+') as f:
        f.write(path)

def cmd_init(args):
    repo = Path(args.path).expanduser().resolve()
    repo.mkdir(parents=True, exist_ok=True)
    (repo / "stowable").mkdir(parents=True, exist_ok=True)
    (repo / "sources").mkdir(parents=True, exist_ok=True)
    (repo / ".hotdot").mkdir(parents=True, exist_ok=True)
    create_version_file(repo, __version__)
    create_active_profile_file(repo)
    create_profiles_file(repo)
    create_gitignore(repo)
    init_git_repo(repo)
    create_active_repo(str(repo))
    print("initialized hotdot repo at", repo)
