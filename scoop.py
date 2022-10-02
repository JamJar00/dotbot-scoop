import subprocess, dotbot, json

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

        buckets = [bucket["Name"] for bucket in manifest["buckets"]]
        apps = [app["Name"] for app in manifest["apps"]]

        return (buckets, apps)


    def _add_missing_buckets(self, desired, installed):
        to_install = desired.difference(installed)
        self._log.info(f'Installing buckets {", ".join(to_install)}')

        success = True
        for bucket in to_install:
            try:
                command = ['scoop bucket add', bucket]

                subprocess.run(
                        [' '.join(command)],
                        shell=True,
                        check=True)
            except subprocess.CalledProcessError:
                success = False

        return success


    def _add_missing_apps(self, desired, installed):
        to_install = desired.difference(installed)
        self._log.info(f'Installing apps {", ".join(to_install)}')

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


    def can_handle(self, directive):
        return self._directive == directive


    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('scoop cannot handle directive %s' %
                directive)

        manifest = self._manifest()
        if not manifest:
            return False
        (installed_buckets, installed_apps) = manifest
        self._log.debug(f'Found buckets {", ".join(installed_buckets)} already configured and apps {", ".join(installed_apps)} already installed')

        if 'buckets' in data:
            add_missing_bucket_success = self._add_missing_buckets(set(data['buckets']), set(installed_buckets))
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
        if not manifest:
            return False
        (new_installed_buckets, new_installed_apps) = manifest
        self._log.debug(f'New installed set of buckets {", ".join(new_installed_buckets)} and apps {", ".join(new_installed_apps)}')

        if 'buckets' in data:
            add_missing_bucket_success &= set(new_installed_buckets) == set(data['buckets'])
        if 'apps' in data:
            add_missing_app_success &= set(new_installed_apps) == set(data['apps'])

        if add_missing_bucket_success:
            self._log.info('All buckets have been added')
        else:
            self._log.error('Some buckets were not successfully added')

        if add_missing_app_success:
            self._log.info('All apps have been installed')
        else:
            self._log.error('Some apps were not successfully installed')

        return add_missing_bucket_success and add_missing_app_success
