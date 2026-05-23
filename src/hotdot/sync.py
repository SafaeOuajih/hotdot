import subprocess
from pathlib import Path

from hotdot.profile import get_active_repo, ACTIVE_PROFILE_FILE
from hotdot.source import get_all_sources, source_profiles

def get_active_profile():
    path = Path(get_active_repo()) / ACTIVE_PROFILE_FILE
    if not path.exists():
        return None
    name = path.read_text().strip()
    return name if name else None

def get_stowable_dir():
    return Path(get_active_repo()) / "stowable"

# -- Sources sharing a name need their own stowable/ dir per profile --
def storage_name(src, all_sources):
    siblings = [s for s in all_sources if s.name == src.name]
    if len(siblings) == 1:
        return src.name
    profiles = source_profiles(src)
    if len(profiles) != 1:
        return None
    return src.name + "/" + profiles[0]

def fetch_source(src, name):
    dest = get_stowable_dir() / name
    if src.fetch == "local":
        return
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        subprocess.run(["git", "clone", "-q", src.fetch, str(dest)], check=True)
    except subprocess.CalledProcessError:
        print("hotdot: failed to fetch", src.name)

def run_stow(args):
    try:
        subprocess.run(["stow", *args], check=True)
        return True
    except subprocess.CalledProcessError:
        print("hotdot: stow failed, see the warnings above")
        return False

def cmd_sync(args):
    profile = get_active_profile()
    if not profile:
        print("no active profile set")
        return

    all_sources = get_all_sources()
    sources = [s for s in all_sources if profile in source_profiles(s)]
    if not sources:
        print("nothing to sync for profile", profile)
        return

    packages = []
    for src in sources:
        name = storage_name(src, all_sources)
        if name is None:
            print(src.name, "is ambiguous; give it a single profile or edit sources/ directly")
            continue
        fetch_source(src, name)
        if (get_stowable_dir() / name).exists():
            packages.append(name)
        else:
            print("skipping", src.name, "(nothing under stowable/ yet)")

    if not packages:
        print("nothing to sync for profile", profile)
        return

    run_stow(["-t", str(Path.home()), "-d", str(get_stowable_dir()), *sorted(packages)])
    print("synced", len(packages), "package(s)")
