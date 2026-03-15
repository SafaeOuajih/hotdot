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

def source_exist(src_name: str):
    sources = []
    files = glob.glob(get_source_dir()+"*.src")
    for f in files:
        srcs = list(parse_source_file(f))
        sources.extend(srcs)

    for src in sources:
        print(src.name, src_name)
        if src.name == src_name:
            return True
    return False

# -- List available sources/packages
def cmd_list(args):
    sources = []
    files = glob.glob(get_source_dir()+"*.src")
    for f in files:
        srcs = list(parse_source_file(f))
        sources.extend(srcs)
    print_sources(sources)

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
    #-- Tag the source file name with the user name --#

