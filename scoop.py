import subprocess, dotbot, json

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


class Scoop(dotbot.Plugin):
    _directive = 'scoop'

    def _manifest(self):
        try:
            res = subprocess.run(
                    'scoop export',
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE)
            manifest = json.loads(res.stdout)
        except subprocess.CalledProcessError:
            self._log.error('Unable to extract manifest from scoop')
            return False

        buckets = [Bucket(bucket["Name"], bucket["Source"]) for bucket in manifest["buckets"]]
        apps = [app["Name"] for app in manifest["apps"]]

        return (buckets, apps)


    def _add_missing_buckets(self, desired, installed):
        to_install = desired.difference(installed)
        self._log.debug(f'Installing buckets {", ".join(str(b) for b in to_install)}')

        success = True
        for bucket in to_install:
            try:
                if bucket.repo is not None:
                    command = ['scoop bucket add', bucket.name, bucket.repo]
                else:
                    command = ['scoop bucket add', bucket.name]

                subprocess.run(
                        [' '.join(command)],
                        shell=True,
                        check=True)
            except subprocess.CalledProcessError:
                success = False

        return success


    def _add_missing_apps(self, desired, installed):
        to_install = desired.difference(installed)
        self._log.debug(f'Installing apps [{", ".join(to_install)}]')

        success = True
        for app in to_install:
            try:
                command = ['scoop install', app]

                subprocess.run(
                        [' '.join(command)],
                        shell=True,
                        check=True)
            except subprocess.CalledProcessError:
                success = False

        return success


    def _parse_buckets(self, buckets):
        parsed_buckets = []
        for bucket in buckets:
            if isinstance(bucket, str):
                parsed_buckets.append(Bucket(bucket))
            else:
                parsed_buckets.append(Bucket(bucket["name"], bucket["repo"]))
        return parsed_buckets


    def can_handle(self, directive):
        return self._directive == directive


    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('scoop cannot handle directive %s' %
                directive)

        desired_buckets = self._parse_buckets(data['buckets'])

        manifest = self._manifest()
        if not manifest:
            return False
        (installed_buckets, installed_apps) = manifest
        self._log.debug(f'Found buckets [{", ".join(str(b) for b in installed_buckets)}] already configured and apps [{", ".join(installed_apps)}] already installed')
        self._log.debug(f'Aiming for buckets [{", ".join(set(str(b) for b in desired_buckets))}] to be configured and apps [{", ".join(set(data["apps"]))}] to be installed')

        if 'buckets' in data:
            add_missing_bucket_success = self._add_missing_buckets(set(desired_buckets), set(installed_buckets))
        else:
            add_missing_bucket_success = True

        if 'apps' in data:
            add_missing_app_success = self._add_missing_apps(set(data['apps']), set(installed_apps))
        else:
            add_missing_app_success = True

        if not add_missing_bucket_success or not add_missing_app_success:
            return False

        # Scoop doesn't return useful exit codes (booo) so get a manifest again and see if it actually added the bucket
        new_manifest = self._manifest()
        if not new_manifest:
            return False

        (new_installed_buckets, new_installed_apps) = new_manifest
        self._log.debug(f'New installed set of buckets [{", ".join(str(b) for b in new_installed_buckets)}] and apps [{", ".join(new_installed_apps)}]')

        if 'buckets' in data:
            add_missing_bucket_success &= set(new_installed_buckets).issuperset(set(desired_buckets))
        if 'apps' in data:
            add_missing_app_success &= set(new_installed_apps).issuperset(set(data['apps']))

        if add_missing_bucket_success:
            self._log.info('All buckets have been added')
        else:
            self._log.error('Some buckets were not successfully added')

        if add_missing_app_success:
            self._log.info('All apps have been installed')
        else:
            self._log.error('Some apps were not successfully installed')

        return add_missing_bucket_success and add_missing_app_success
