import argparse
import sys

from hotdot.init import cmd_init
from hotdot.profile import cmd_profile
from hotdot.source import cmd_add, cmd_list, cmd_rm

def build_parser():
    parser = argparse.ArgumentParser(
        prog="hotdot",
        description="Manage your dotfiles with Stow.",
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
    add_parser.add_argument("package")
    add_parser.add_argument("profile")
    add_parser.set_defaults(func=cmd_add)

    rm_parser = subparsers.add_parser(
        "rm",
        help="remove a source from a profile.",
    )
    rm_parser.add_argument("package")
    rm_parser.add_argument("profile")
    rm_parser.set_defaults(func=cmd_rm)

    list_parser = subparsers.add_parser(
        "list",
        help="list available sources.",
    )
    # list_parser.add_argument("profile")
    list_parser.set_defaults(func=cmd_list)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
