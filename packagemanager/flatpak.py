import shutil

from .base import PackageManagerBase

# TODO: Add flatpak support
class FlatpakPackageManager(PackageManagerBase):
    NAME = "flatpak"

    def __init__(self):
        self.BIN_PATH = shutil.which("flatpak")


    @staticmethod
    def is_present():
        return bool(shutil.which("flatpak"))


    def add_repositories(self, repo_list):
        pass

    def install_packages(self, package_list):
        pass
