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
    init_parser.set_defaults(func=cmd_init)

    return parser.parse_args()

def main():
    args = build_parser()
    return args.func(args)

if __name__ == "__main__":
    sys.exit(main())
