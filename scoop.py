import dotbot
import json
import subprocess


class Bucket:
    def __init__(self, name, repo=None):
        self.name = name
        self.repo = repo

    def __eq__(self, other):
        if isinstance(other, Bucket):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        if self.repo is not None:
            return f"{self.name} ({self.repo})"
        else:
            return self.name


class App:
    def __init__(self, name):
        self.name = name

    def __eq__(self, other):
        if isinstance(other, App):
            return self.name == other.name
        else:
            return False

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


def _parse_buckets_config(buckets):
    if buckets is None:
        return []

    parsed_buckets = []
    for bucket in buckets:
        if isinstance(bucket, str):
            parsed_buckets.append(Bucket(bucket))
        else:
            parsed_buckets.append(Bucket(bucket["name"], bucket["repo"]))
    return parsed_buckets


def _parse_apps_config(apps):
    if apps is None:
        return []

    parsed_apps = []
    for app in apps:
        parsed_apps.append(App(app))
    return parsed_apps


def _diff(desired, installed):
    return set(desired).difference(set(installed))


def _verify(desired, installed):
    return set(installed).issuperset(set(desired))


class Scoop(dotbot.Plugin):
    _directive = 'scoop'

    def _manifest(self):
        command = ['scoop', 'export']
        try:
            res = subprocess.run(
                command,
                shell=True,
                check=True,
                stdout=subprocess.PIPE)
            manifest = json.loads(res.stdout)
        except subprocess.CalledProcessError:
            self._log.error(f'Unable to extract manifest from scoop running command "{command}"')
            return False

        buckets = [Bucket(bucket["Name"], bucket["Source"]) for bucket in manifest["buckets"]]
        apps = [App(app["Name"]) for app in manifest["apps"]]

        return (buckets, apps)

    def _add_missing_buckets(self, to_add):
        self._log.debug(f'Adding buckets [{", ".join(str(b) for b in to_add)}]')

        success = True
        for bucket in to_add:
            if bucket.repo is not None:
                command = ['scoop', 'bucket', 'add', bucket.name, bucket.repo]
            else:
                command = ['scoop', 'bucket', 'add', bucket.name]

            try:
                subprocess.run(
                    command,
                    shell=True,
                    check=True)
            except subprocess.CalledProcessError:
                self._log.error(f"Failed to add bucket {bucket} by running the command {command}")
                success = False

        return success

    def _add_missing_apps(self, to_add):
        self._log.debug(f'Adding apps [{", ".join(a.name for a in to_add)}]')

        success = True
        for app in to_add:
            command = ['scoop', 'install', app.name]

            try:
                subprocess.run(
                    command,
                    shell=True,
                    check=True)
            except subprocess.CalledProcessError:
                self._log.error(f"Failed to add app {app} by running the command {command}")
                success = False

        return success

    def can_handle(self, directive):
        return self._directive == directive

    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('scoop cannot handle directive %s' % directive)

        desired_buckets = _parse_buckets_config(data['buckets'])
        desired_apps = _parse_apps_config(data['apps'])

        if data is None:
            self._log.error('No buckets nor apps configured for the scoop directive to install (have you indented them correctly?)')
            return False

        manifest = self._manifest()
        if not manifest:
            return False
        (installed_buckets, installed_apps) = manifest
        self._log.debug(f'Found buckets [{", ".join(str(b) for b in installed_buckets)}] already '
                        + f'configured and apps [{", ".join(str(a) for a in installed_apps)}] '
                        + 'already installed')
        self._log.debug(f'Aiming for buckets [{", ".join(set(str(b) for b in desired_buckets))}] '
                        + 'to be configured and apps '
                        + f'[{", ".join(set(str(a) for a in desired_apps))}] to be installed')

        buckets_to_add = _diff(desired_buckets, installed_buckets)
        apps_to_add = _diff(desired_apps, installed_apps)

        add_missing_bucket_success = self._add_missing_buckets(buckets_to_add)
        add_missing_app_success = self._add_missing_apps(apps_to_add)

        if not add_missing_bucket_success or not add_missing_app_success:
            return False

        # Scoop doesn't return useful exit codes (booo) so get a manifest again and see if it
        # actually added the bucket
        new_manifest = self._manifest()
        if not new_manifest:
            return False

        (new_installed_buckets, new_installed_apps) = new_manifest
        self._log.debug('New installed set of buckets '
                        + f'[{", ".join(str(b) for b in new_installed_buckets)}] and apps '
                        + f'[{", ".join(str(a) for a in new_installed_apps)}]')

        add_missing_bucket_verify = _verify(desired_buckets, new_installed_buckets)
        add_missing_app_verify = _verify(desired_apps, new_installed_apps)

        if add_missing_bucket_verify:
            self._log.info('All buckets have been added')
        else:
            self._log.error('Some buckets were not successfully added')

        if add_missing_app_verify:
            self._log.info('All apps have been added')
        else:
            self._log.error('Some apps were not successfully added')

        return add_missing_bucket_success and add_missing_app_success
