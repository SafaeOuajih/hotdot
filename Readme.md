# HotDot

A Stow based dotfiles manager. Mange dotfiles, create by profile
configurations, switch profile when needed and STOW it all to get
the new environment.

<p align="center">
  <img src="assets/hotdot_logo.png" alt="The best Hot Dot!" width="360">
</p>

## install

Needs GNU `stow` on the system (`apt install stow`, `brew install stow`, whatever your distro calls it) and python >= 3.9.

Grab the wheel from [releases](https://github.com/SafaeOuajih/hotdot/releases) and:

```
pip install hotdot-<version>-py3-none-any.whl
```

Not on PyPI, so this is it for now.

## quick start

```
hotdot init ~/dotfiles
cd ~/dotfiles
hotdot profile laptop
hotdot switch laptop
```

`init` scaffolds `sources/` and `stowable/`, sets up git, and remembers this repo as your active one (so you can run `hotdot` from anywhere after that, not just from inside the repo).

Then write a `.src` file per thing you want managed (see below), `hotdot add <name> <profile>` it to a profile, and `hotdot sync`.

## how it works

- `sources/*.src` describes *what* to manage and *where it goes*. One file can hold several `{ }` blocks.
- `stowable/` is what actually gets symlinked into `$HOME`. Git-fetched sources land there automatically on `sync` (sparse-checked-out, only the `path` you asked for); `local` sources you just put there yourself and commit.
- profiles let different machines run different sets of sources. `.hotdot/active_profile` says which one is live right now.
- `sync` fetches whatever needs fetching, stows the active profile's sources into `$HOME` with `stow`, and un-stows anything the profile dropped since last time.

## `.src` format

```
{
    name: nvim
    fetch: git@github.com:you/nvim_cfg.git
    goes-to: .config/nvim
    profile: laptop
}
```

- `name`: the source's id, whatever you use with `add`/`rm`.
- `fetch`: a git url, or `local` if you're just going to drop the files in `stowable/` yourself.
- `goes-to`: where it lands under `$HOME`.
- `path`: optional, only for git sources. Sparse-checkout just this path out of the repo instead of cloning the whole thing (e.g. one file out of a big dotfiles monorepo). Skip it to clone the entire repo into `goes-to`.
- `profile`: comma-separated list of profiles this source is active on. Edited directly by `add`/`rm`, or by hand.

Same `name` can appear more than once (different `fetch`/`goes-to` per profile, like a `local` gitconfig on one machine and a fetched one on another). `hotdot` figures out which one you mean from the profile you're acting on, and complains if it's still ambiguous.

## commands

- `init [path]`: scaffold a new repo (defaults to `.`).
- `profile <name>`: add a new profile.
- `add <package> <profile>`: turn a source on for a profile.
- `rm <package> <profile>`: turn it back off.
- `list`: show every known source and which profile(s) it's on.
- `sync [-f] [-y]`: fetch + stow the active profile. `-f` backs up and takes over files that already exist and aren't stow's; `-y` skips the confirmation on that.
- `switch <name>`: change the active profile and sync it.

## gotchas

- **parsing is dumb on purpose.** No variables, no conditionals, `goes-to` is a literal path. Anything machine-specific (a Firefox profile hash, a uuid, whatever) has to be hardcoded. If it changes on a new machine, you edit the `.src` by hand, `hotdot` won't figure it out for you.
- **`stow` folds missing directories into one symlink.** If `goes-to` points somewhere nested under a directory that doesn't exist yet on a fresh machine, `stow` won't create the real directories down to your file, it'll symlink the whole missing parent straight into your dotfiles repo instead. Fine when the parent is already something real and app-owned (`.config/nvim`). Very much not fine when the parent is something shared across unrelated apps. Make sure the real directory chain already exists (run the app once) before the first `sync` that touches it.
- **`local` sources are never fetched.** `sync` just checks the content is already sitting under `stowable/<name>/` you own getting it there and committing it.
