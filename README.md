[dotbot_repo]: https://github.com/anishathalye/dotbot

## Dotbot `scoop` Plugin
Plugin for [Dotbot][dotbot_repo], that adds the `scoop` directive, which allows you to install scoop packages 

Largely based on the [snap plugin](https://github.com/DrDynamic/dotbot-snap.git) for the same purpose.

## Installation
1. Simply add this repo as a submodule of your dotfiles repository:
```
git submodule add https://github.com/JamJar00/dotbot-scoop.git
```

2. Pass this folder (or directly scoop.py file) path with corresponding flag to dotbot in your install script:
  - `-p /path/to/file/scoop.py`

  or

 - `--plugin-dir /pato/to/plugin/folder`

## Usage
### Example Config
```yaml
...
- scoop:
    buckets:
      - extras
      - name: nerd-fonts
        repo: https://github.com/matthewjberger/scoop-nerd-fonts
      ...
    apps:
      - firefox
      - win32yank
      ...
...
```

### Troubleshooting
If it fails run `./install -v` to see more info
If the more info just says `Extra data: line 1 column 2 (char 1)` your scoop is old, run `scoop update`

### Developing
Run the following command to get some linting
```bash
poetry run pylama
```
