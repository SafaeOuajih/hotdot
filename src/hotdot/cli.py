import argparse
import sys

import argcomplete

from hotdot.__init__ import __version__
from hotdot.init import cmd_init
from hotdot.profile import cmd_profile, get_all_profiles
from hotdot.source import cmd_add, cmd_list, cmd_rm, get_all_sources
from hotdot.sync import cmd_sync, cmd_switch

# -- Completers must never blow up a user's shell: swallow errors, just offer nothing --
def complete_profiles(prefix, parsed_args, **kwargs):
    try:
        return get_all_profiles()
    except Exception:
        return []

def complete_packages(prefix, parsed_args, **kwargs):
    try:
        return sorted({s.name for s in get_all_sources()})
    except Exception:
        return []

def build_parser():
    parser = argparse.ArgumentParser(
        prog="hotdot",
        description="Manage your dotfiles with Stow.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="hotdot " + __version__,
    )

    subparsers = parser.add_subparsers(
        dest="command",
        required=True,
    )

    init_parser = subparsers.add_parser(
        "init",
        help="scaffold a new dotfiles repo.",
    )
    init_parser.add_argument("path", nargs="?", default=".")
    init_parser.set_defaults(func=cmd_init)

    profile_parser = subparsers.add_parser(
        "profile",
        help="add a new profile.",
    )
    profile_parser.add_argument("name")
    profile_parser.set_defaults(func=cmd_profile)

    add_parser = subparsers.add_parser(
        "add",
        help="add a source to a profile.",
    )
    add_parser.add_argument("package").completer = complete_packages
    add_parser.add_argument("profile").completer = complete_profiles
    add_parser.set_defaults(func=cmd_add)

    rm_parser = subparsers.add_parser(
        "rm",
        help="remove a source from a profile.",
    )
    rm_parser.add_argument("package").completer = complete_packages
    rm_parser.add_argument("profile").completer = complete_profiles
    rm_parser.set_defaults(func=cmd_rm)

    list_parser = subparsers.add_parser(
        "list",
        help="list available sources.",
    )
    # list_parser.add_argument("profile")
    list_parser.set_defaults(func=cmd_list)

    sync_parser = subparsers.add_parser(
        "sync",
        help="fetch sources and stow the active profile.",
    )
    sync_parser.add_argument(
        "-f", "--force",
        action="store_true",
        help="back up and take over files that already exist and aren't managed by stow.",
    )
    sync_parser.add_argument(
        "-y", "--yes",
        action="store_true",
        help="assume yes to the -f confirmation prompt, don't ask.",
    )
    sync_parser.set_defaults(func=cmd_sync)

    switch_parser = subparsers.add_parser(
        "switch",
        help="switch the active profile.",
    )
    switch_parser.add_argument("name").completer = complete_profiles
    switch_parser.set_defaults(func=cmd_switch)

    return parser

def main():
    parser = build_parser()
    argcomplete.autocomplete(parser)
    args = parser.parse_args()
    args.func(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
