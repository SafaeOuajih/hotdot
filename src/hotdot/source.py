import glob
from hotdot.profile import profile_exist, get_active_repo

class Source():
    name : str
    fetch : str
    goes_to : str
    profile : str

def parse_source_file(src_file) -> list[Source]:
    sources = []
    with open(src_file, "r") as f:
        # parse the .src file
        # keep it dumb for now
        src = Source()
        for line in f:
            if (line.startswith('{')):
                src = Source()
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
            if not line:
                continue
            if (line.startswith('}')):
                sources.append(src)
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

# -- List available sources/packages
def cmd_list(args):
    print_sources(get_all_sources())

# -- Tag a source file with a profile, in place --
def tag_source_with_profile(src_name: str, profile: str):
    files = glob.glob(get_source_dir()+"*.src")
    for path in files:
        with open(path, "r") as f:
            lines = f.readlines()

        in_block = False
        name_matches = False
        profile_line = None
        for i, line in enumerate(lines):
            if line.startswith('{'):
                in_block = True
                name_matches = False
                profile_line = None
                continue
            if in_block and line.strip().startswith('name'):
                name_matches = (line.strip().split(':')[1]).strip() == src_name
                continue
            if in_block and line.strip().startswith('profile'):
                profile_line = i
                continue
            if line.startswith('}'):
                if name_matches:
                    if profile_line is not None:
                        current = lines[profile_line].split(':', 1)[1].strip()
                        profiles = [p.strip() for p in current.split(',') if p.strip()]
                        if profile not in profiles:
                            profiles.append(profile)
                        lines[profile_line] = "    profile: " + ", ".join(profiles) + "\n"
                    else:
                        lines.insert(i, "    profile: " + profile + "\n")
                    with open(path, "w") as f:
                        f.writelines(lines)
                    return True
                in_block = False
    return False

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

    for src in get_all_sources():
        if src.name == src_name and profile in source_profiles(src):
            print(src_name, "already uses profile", profile)
            return

    tag_source_with_profile(src_name, profile)
    print("added", src_name, "to profile", profile)

