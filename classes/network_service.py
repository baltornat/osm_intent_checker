import subprocess


class NetworkService:
    def __init__(self, vnfd, nsd, ns_name, vim_account):
        self.vnfd = vnfd
        self.nsd = nsd
        self.ns_name = ns_name
        self.vim_account = vim_account

    def upload_nfpkg(self):
        print("osm nfpkg-create {}".format(self.vnfd.package_path))
        '''
        try:
            output = subprocess.check_output(['osm', 'nfpkg-create', self.vnfd.package_path], text=True)
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError: ', e)
        '''

    def upload_nspkg(self):
        print("osm nspkg-create {}".format(self.nsd.package_path))
        '''
        # Check if nfpkg is done before nspkg
        try:
            output = subprocess.check_output(['osm', 'nspkg-create', self.nsd.package_path], text=True)
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError: ', e)
        '''

    def deploy_ns(self):
        print("osm ns-create --ns_name {} --nsd_name {} --vim_account {}".format(self.ns_name, self.nsd.get_nsd_name(),
              self.vim_account))
        '''
        # Check if both the VNFD and the NSD are uploaded on the server
        try:
            output = subprocess.check_output(['osm', 'ns-create', '--ns_name', self.ns_name, '--nsd_name',
                                              self.nsd.get_nsd_name(), '--vim_account', self.vim_account], text=True)
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError: ', e)
        '''
