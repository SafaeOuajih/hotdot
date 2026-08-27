import glob
from hotdot.profile import profile_exist, get_active_repo

class Source():
    name : str
    fetch : str
    goes_to : str
    profile : str
    file : str
    start : int
    end : int

def parse_source_file(src_file) -> list[Source]:
    sources = []
    with open(src_file, "r") as f:
        lines = f.readlines()

    # parse the .src file
    # keep it dumb for now
    src = None
    for i, line in enumerate(lines):
        if (line.startswith('{')):
            src = Source()
            src.file = src_file
            src.start = i
            src.profile = ""
            continue
        if src is None:
            continue
        if (line.strip().startswith('name')):
            src.name = (line.strip().split(':')[1]).strip()
            continue
        if (line.strip().startswith('fetch')):
            src.fetch = (line.strip().split(':')[1]).strip()
            continue
        if (line.strip().startswith('goes-to')):
            src.goes_to = (line.strip().split(':')[1]).strip()
            continue
        if (line.strip().startswith('profile')):
            src.profile = (line.strip().split(':')[1]).strip()
            continue
        if (line.startswith('}')):
            src.end = i
            sources.append(src)
            src = None
    return sources

def print_sources(list: list[Source]):
    for src in list:
        print(src.profile, ":", src.name)

def get_source_dir():
    return get_active_repo()+"/sources/"

def get_all_sources():
    sources = []
    files = glob.glob(get_source_dir()+"*.src")
    for f in files:
        srcs = list(parse_source_file(f))
        sources.extend(srcs)
    return sources

def source_exist(src_name: str):
    for src in get_all_sources():
        if src.name == src_name:
            return True
    return False

def source_profiles(src: Source):
    if not getattr(src, "profile", None):
        return []
    return [p.strip() for p in src.profile.split(",") if p.strip()]

# -- Find the one source a name (+ profile hint) refers to, or None --
def find_source(src_name: str, profile: str = None):
    matches = [s for s in get_all_sources() if s.name == src_name]
    if not matches:
        return None
    if len(matches) == 1:
        return matches[0]

    scoped = [s for s in matches if profile and profile in source_profiles(s)]
    if len(scoped) == 1:
        return scoped[0]

    print(src_name, "is ambiguous (", len(matches), "sources share that name), edit sources/ directly")
    return None

# -- List available sources/packages
def cmd_list(args):
    print_sources(get_all_sources())

# -- Rewrite a source's profile field in place --
def write_profile_field(src: Source, profiles: list[str]):
    with open(src.file, "r") as f:
        lines = f.readlines()

    new_line = "    profile: " + ", ".join(profiles) + "\n"
    for i in range(src.start + 1, src.end):
        if lines[i].strip().startswith('profile'):
            lines[i] = new_line
            break
    else:
        lines.insert(src.end, new_line)

    with open(src.file, "w") as f:
        f.writelines(lines)

# -- Adopt a source for a profile
def cmd_add(args):
    src_name = args.package
    profile = args.profile
    if not profile_exist(profile):
        print("profile does not exist\n\tuse : hotdot profile <..> to create a new profile")
        return
    if not source_exist(src_name):
        print("source does not exist")
        return

    src = find_source(src_name, profile)
    if src is None:
        return

    profiles = source_profiles(src)
    if profile in profiles:
        print(src_name, "already uses profile", profile)
        return

    profiles.append(profile)
    write_profile_field(src, profiles)
    print("added", src_name, "to profile", profile)

# -- Drop a source from a profile
def cmd_rm(args):
    src_name = args.package
    profile = args.profile
    if not source_exist(src_name):
        print("source does not exist")
        return

    src = find_source(src_name, profile)
    if src is None:
        return

    profiles = source_profiles(src)
    if profile not in profiles:
        print(src_name, "does not use profile", profile)
        return

    profiles.remove(profile)
    write_profile_field(src, profiles)
    print("removed", src_name, "from profile", profile)
