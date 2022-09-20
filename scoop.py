import subprocess, dotbot

class Scoop(dotbot.Plugin):
    _directive = 'scoop'


    def can_handle(self, directive):
        return self._directive == directive


    def handle(self, directive, data):
        if directive != self._directive:
            raise ValueError('scoop cannot handle directive %s' %
                directive)
        
        bucket_success = True
        app_success = True

        if 'buckets' in data:
            for bucket, options in data['buckets'].items():
                try:
                    command = ['scoop bucket add', bucket]

                    subprocess.run(
                            [' '.join(command)], 
                            shell=True, 
                            check=True)
                except subprocess.CalledProcessError:
                    bucket_success = False

            if bucket_success:
                self._log.info('All buckets have been added')
            else:
                self._log.error('Some buckets were not successfully added')

        if 'apps' in data:
            for app, options in data['apps'].items():
                try:
                    command = ['scoop install', app]

                    subprocess.run(
                            [' '.join(command)], 
                            shell=True, 
                            check=True)
                except subprocess.CalledProcessError:
                    app_success = False

            if app_success:
                self._log.info('All apps have been installed')
            else:
                self._log.error('Some apps were not successfully installed')

        return bucket_success and app_success
