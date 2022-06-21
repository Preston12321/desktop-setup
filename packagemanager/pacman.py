import shutil
import subprocess
import sys

from .base import PackageManagerBase
from .util import validate_package_names

class PacmanPackageManager(PackageManagerBase):
    NAME = "pacman"

    def __init__(self):
        self.BIN_PATH = shutil.which("pacman")
        self.PARU_BIN_PATH = shutil.which("paru")


    @staticmethod
    def is_present():
        return bool(shutil.which("pacman")) and bool(shutil.which("paru"))


    def add_repositories(self, repo_list):
        # TODO: Implement third-party repo support for pacman
        # Supported by pacman, but relatively uncommon because of AUR
        pass


    def install_packages(self, package_list):
        err = [pkg_def for pkg_def in package_list if "installName" not in pkg_def]
        if err:
            print("Error: No installName for one or more snap packages", file=sys.stderr)
            exit(1)

        normal = [pkg_def["installName"] for pkg_def in package_list if not pkg_def.get("aur")]
        aur = [pkg_def["installName"] for pkg_def in package_list if pkg_def.get("aur")]

        self.install_normal_packages(normal)
        self.install_aur_packages(aur)


    def install_normal_packages(self, package_names):
        if package_names:
            validate_package_names(package_names)
            run_package_manager([self.BIN_PATH, "--noconfirm", "-S", *package_names])


    def install_aur_packages(self, package_names):
        if package_names:
            validate_package_names(package_names)
            run_package_manager([self.PARU_BIN_PATH, "--skipreview", "-S", *package_names])
