import argparse
import sys

from hotdot.init import cmd_init

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
        help="scaffold a new dotfiles repo",
    )
    init_parser.add_argument("path", nargs="?", default=".")
    init_parser.set_defaults(func=cmd_init)

    return parser

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)
    return 0

if __name__ == "__main__":
    sys.exit(main())
