[dotbot_repo]: https://github.com/anishathalye/dotbot

## Dotbot `scoop` Plugin
Plugin for [Dotbot][dotbot_repo], that adds the `scoop` directive, which allows you to install scoop packages 

Largely based on the [snap plugin](https://github.com/DrDynamic/dotbot-snap.git) for the same purpose.

## Installation
1. Simply add this repo as a submodule of your dotfiles repository:
```
git submodule add https://github.com/JamJar00/dotbot-scoop.git
```

2. Pass this folder (or directly scoop.py file) path with corresponding flag to your [Dotbot][dotbot_repo] script:
  - `-p /path/to/file/scoop.py`

  or

 - `--plugin-dir /pato/to/plugin/folder`

## Usage
### Example config
```yaml
...
- scoop:
    buckets:
      - extras
      ...
    apps:
      - firefox
      - win32yank
      ...
...
```

### Execution
```bash
"~/.dotfiles/bin/dotbot" -d "~/.dotfiles" -c "~/.dotfiles/packages.yaml" -p "~/.dotfiles/plugins/dotbot-scoop/scoop.py"
```