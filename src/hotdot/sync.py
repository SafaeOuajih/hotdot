import shutil
import subprocess
from pathlib import Path

from hotdot.profile import get_active_repo, profile_exist, ACTIVE_PROFILE_FILE
from hotdot.source import get_all_sources, source_profiles

STATE_FILE = ".hotdot/state"
STAGE_DIR = ".hotdot/stage"

def get_active_profile():
    path = Path(get_active_repo()) / ACTIVE_PROFILE_FILE
    if not path.exists():
        return None
    name = path.read_text().strip()
    return name if name else None

def set_active_profile(name):
    (Path(get_active_repo()) / ACTIVE_PROFILE_FILE).write_text(name + "\n")

def get_stowable_dir():
    return Path(get_active_repo()) / "stowable"

def get_stage_dir():
    return Path(get_active_repo()) / STAGE_DIR

def get_state_file():
    return Path(get_active_repo()) / STATE_FILE

def read_state():
    f = get_state_file()
    if not f.exists():
        return {}
    state = {}
    for line in f.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        name, _, storage = line.partition("\t")
        state[name] = storage
    return state

def write_state(mapping):
    get_state_file().write_text("".join(n + "\t" + s + "\n" for n, s in sorted(mapping.items())))

# -- Sources sharing a name need their own stowable/ dir per profile --
def storage_name(src, all_sources):
    siblings = [s for s in all_sources if s.name == src.name]
    if len(siblings) == 1:
        return src.name
    profiles = source_profiles(src)
    if len(profiles) != 1:
        return None
    return src.name + "/" + profiles[0]

# -- Non-local sources are reproducible via `hotdot sync`; keep their copy out of git --
def ignore_fetched(name):
    repo = Path(get_active_repo())
    if not (repo / ".git").exists():
        return
    gitignore = repo / ".gitignore"
    entry = "stowable/" + name + "/"
    lines = gitignore.read_text().splitlines() if gitignore.exists() else []
    if entry in lines:
        return
    with open(gitignore, "a") as f:
        f.write(entry + "\n")

def fetch_sparse(src, dest):
    tmp = Path(str(dest) + ".fetch-tmp")
    shutil.rmtree(tmp, ignore_errors=True)
    try:
        subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", "--sparse", src.fetch, str(tmp)], check=True)
        subprocess.run(["git", "-C", str(tmp), "sparse-checkout", "set", src.path], check=True)
        subprocess.run(["git", "-C", str(tmp), "checkout", "-q"], check=True)
        shutil.move(str(tmp / src.path), str(dest))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

def fetch_source(src, name):
    dest = get_stowable_dir() / name / src.goes_to
    if src.fetch == "local":
        return
    ignore_fetched(name)
    if dest.exists():
        return
    dest.parent.mkdir(parents=True, exist_ok=True)
    try:
        if src.path:
            fetch_sparse(src, dest)
        else:
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

# -- Flat symlinks so stow (which rejects "/" in package names) can address nested storage --
def rebuild_stage(stage, stowable, mapping):
    if stage.exists():
        for child in stage.iterdir():
            child.unlink()
    else:
        stage.mkdir(parents=True)
    for name, storage in mapping.items():
        (stage / name).symlink_to(stowable / storage)

# -- Fetch, stow the given profile's sources and cleanly unstow whatever it dropped --
def sync_profile(profile):
    all_sources = get_all_sources()
    sources = [s for s in all_sources if profile in source_profiles(s)]

    active = {}
    for src in sources:
        storage = storage_name(src, all_sources)
        if storage is None:
            print(src.name, "is ambiguous; give it a single profile or edit sources/ directly")
            continue
        fetch_source(src, storage)
        if (get_stowable_dir() / storage).exists():
            active[src.name] = storage
        else:
            print("skipping", src.name, "(nothing under stowable/ yet)")

    previous = read_state()
    removed = {n: s for n, s in previous.items() if n not in active}

    stage = get_stage_dir()
    stowable = get_stowable_dir()
    rebuild_stage(stage, stowable, {**removed, **active})

    home = str(Path.home())
    if removed:
        run_stow(["-D", "-t", home, "-d", str(stage), *sorted(removed)])
    if active:
        run_stow(["-t", home, "-d", str(stage), *sorted(active)])
    rebuild_stage(stage, stowable, active)

    write_state(active)
    return active

def cmd_sync(args):
    profile = get_active_profile()
    if not profile:
        print("no active profile set")
        return

    packages = sync_profile(profile)
    if packages:
        print("synced", len(packages), "package(s)")
    else:
        print("nothing to sync")

def cmd_switch(args):
    if not profile_exist(args.name):
        print("profile does not exist\n\tuse : hotdot profile <..> to create a new profile")
        return

    set_active_profile(args.name)
    packages = sync_profile(args.name)
    print("switched to profile", args.name, "(", len(packages), "package(s))")
