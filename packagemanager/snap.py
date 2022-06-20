import shutil
import subprocess
import sys

from .base import PackageManagerBase
from .util import validate_package_names

class SnapPackageManager(PackageManagerBase):
    NAME = "snap"

    def __init__(self):
        self.BIN_PATH = shutil.which("snap")

    
    @staticmethod
    def is_present():
        return bool(shutil.which("snap"))


    def add_repositories(self, repo_list):
        # Snap doesn't support third-party repos -_-
        pass


    def install_packages(self, package_list):
        err = [pkg_def for pkg_def in package_list if "installName" not in pkg_def]
        if err:
            print("Error: No installName for one or more snap packages", file=sys.stderr)
            exit(1)

        normal = [pkg_def["installName"] for pkg_def in package_list if not pkg_def.get("classic")]
        classic = [pkg_def["installName"] for pkg_def in package_list if pkg_def.get("classic")]

        self.install_normal_packages(normal)
        self.install_classic_packages(classic)


    def install_normal_packages(self, package_names):
        if package_names:
            validate_package_names(package_names)
            # TODO: Change to actual command when done debugging
            subprocess.run([self.BIN_PATH, "info", *package_names], stdout=subprocess.DEVNULL, check=True)


    def install_classic_packages(self, package_names):
        if package_names:
            validate_package_names(package_names)
            # TODO: Change to actual command when done debugging
            subprocess.run([self.BIN_PATH, "info", "--verbose", *package_names], stdout=subprocess.DEVNULL, check=True)
