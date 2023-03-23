import subprocess
import re

from exceptions.service_exceptions import CnfNotUploaded, NsNotUploaded, DeploymentFailed, VimNotFound


class NetworkService:
    def __init__(self, vnfd, nsd, ns_name, vim_account):
        self.vnfd = vnfd
        self.nsd = nsd
        self.ns_name = ns_name
        self.vim_account = vim_account
        self.package_id = None

    def upload_nfpkg(self):
        try:
            output = subprocess.check_output(['osm', 'nfpkg-create', self.vnfd.package_path])
            package_id_pattern = re.compile(r"([a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})")
            match = package_id_pattern.search(output.decode())
            if match:
                self.vnfd.package_id = match.group(1)
            else:
                print("CNF package upload ID not found in output")
            output = subprocess.check_output(['osm', 'vnfd-list'], text=True)
            if self.vnfd.package_id is None or self.vnfd.package_id not in output.lower():
                raise CnfNotUploaded(f"CNF package upload failed: {self.vnfd.package_path}")
            else:
                print("CNF Package successfully uploaded!")
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError exception: ', e)

    def upload_nspkg(self):
        try:
            output = subprocess.check_output(['osm', 'nspkg-create', self.nsd.package_path])
            package_id_pattern = re.compile(r"([a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})")
            match = package_id_pattern.search(output.decode())
            if match:
                self.nsd.package_id = match.group(1)
            else:
                print("NS package upload ID not found in output")
            output = subprocess.check_output(['osm', 'nsd-list'], text=True)
            if self.nsd.package_id is None or self.nsd.package_id not in output.lower():
                raise NsNotUploaded(f"NS package upload failed: {self.nsd.package_path}")
            else:
                print("NS Package successfully uploaded!")
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError exception: ', e)

    def deploy_ns(self):
        try:
            output = subprocess.check_output(['osm', 'ns-create', '--ns_name', self.ns_name, '--nsd_name',
                                              self.nsd.get_nsd_name(), '--vim_account', self.vim_account])
            package_id_pattern = re.compile(r"([a-f\d]{8}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{4}-[a-f\d]{12})")
            match = package_id_pattern.search(output.decode())
            if match:
                self.package_id = match.group(1)
            else:
                print("Deployment ID not found in output")
            output = subprocess.check_output(['osm', 'ns-list'], text=True)
            if self.package_id is None or self.package_id not in output.lower():
                raise DeploymentFailed(f"Deployment failed: {self.ns_name}")
            else:
                print(
                    f"\nDone! You need to manually check if the service is in READY state (osm ns-show {self.package_id})")
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError exception: ', e)

    def check_vim(self):
        try:
            output = subprocess.check_output(['osm', 'vim-list'], text=True)
            if self.vim_account is None or self.vim_account not in output.lower():
                raise VimNotFound(f"VIM account {self.vim_account} not found")
        except subprocess.CalledProcessError as e:
            print('Caught CalledProcessError exception: ', e)
