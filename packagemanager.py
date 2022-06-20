import re
import requests
import shutil
import subprocess
import sys

from abc import ABC, abstractmethod

def validate_package_names(name_list):
    for name in name_list:
        if not re.match(r'[a-z0-9_-]+', name):
            print("Error: Invalid package name '%s'" % name, file=sys.stderr)


class PackageManager(ABC):
    NAME = None

    @staticmethod
    @abstractmethod
    def is_present():
        return False


    @abstractmethod
    def add_repositories(self, repo_list):
        pass


    @abstractmethod
    def install_packages(self, package_list):
        pass


class AptPackageManager(PackageManager):
    NAME = "apt"

    def __init__(self):
        self.BIN_PATH = shutil.which("apt")

        cp = subprocess.run(["lsb_release", "-cs"], text=True, stdout=subprocess.PIPE, check=True)
        self.RELEASE = cp.stdout.replace("\n", "")


    @staticmethod
    def is_present():
        return bool(shutil.which("apt"))


    def add_repositories(self, repo_list):
        for repo in repo_list:
            if "ppa" in repo:
                subprocess.run(["apt-add-repository", "-y", "-P", repo["ppa"]], check=True)
                continue

            if "sourcesLine" not in repo or "sourcesFile" not in repo:
                print("Error: Invalid apt repo definition", file=sys.stderr)
                exit(1)

            with open(repo["sourcesFile"], "w") as file:
                file.write(repo["sourcesLine"].replace("${RELEASE}", self.RELEASE))

            if "keyUrl" in repo and "keyFile" in repo:
                subprocess.run(["curl", "--create-dirs", "-o", repo["keyFile"], repo["keyUrl"]], check=True)
            elif "keyServer" in repo and "recvKeys" in repo:
                subprocess.run(["apt-key", "adv", "--keyserver", repo["keyServer"], "--recv-keys", repo["recvKeys"]], check=True)

        subprocess.run(["apt", "update"], check=True)


    def install_packages(self, package_list, deb_urls=False):
        # Gets all packageDefinitions where either "installName" and
        # "installUrl" are both defined, or neither is. Both are errors
        err = [pkg_def for pkg_def in package_list if ("installName" in pkg_def) == ("installUrl" in pkg_def)]
        if err:
            print("Error: Invalid packageDefinition for one or more apt packages", file=sys.stderr)
            exit(1)

        names = [pkg_def["installName"] for pkg_def in package_list if "installName" in pkg_def]
        urls = [pkg_def["installUrl"] for pkg_def in package_list if "installUrl" in pkg_def]

        self.install_from_urls(urls)
        self.install_from_names(names)


    def install_from_names(self, name_list):
        if name_list:
            validate_package_names(name_list)
            subprocess.run([self.BIN_PATH, "install", "-y", "--dry-run", *name_list], check=True)


    def install_from_urls(self, url_list):
        deb_files = []

        for i in range(len(url_list)):
            print("Get: %s" % url_list[i])

            content = requests.get(url_list[i])
            path = "%s/%d.deb" % (TEMP_DIR, i)

            with open(path, "wb") as file:
                file.write(content)

            deb_files.append(path)

        for deb in deb_files:
            subprocess.run([self.BIN_PATH, "install", "-y", "--dry-run", deb], check=True)

class PacmanPackageManager(PackageManager):
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
            subprocess.run([self.BIN_PATH, "--noconfirm", "-S", *package_names], check=True)


    def install_aur_packages(self, package_names):
        if package_names:
            validate_package_names(package_names)
            subprocess.run([self.PARU_BIN_PATH, "--skipreview", "-S", *package_names], check=True)


class SnapPackageManager(PackageManager):
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
            subprocess.run([self.BIN_PATH, "info", *package_names], check=True)


    def install_classic_packages(self, package_names):
        if package_names:
            validate_package_names(package_names)
            # TODO: Change to actual command when done debugging
            subprocess.run([self.BIN_PATH, "info", "--verbose", *package_names], check=True)


# TODO: Add flatpak support
class FlatpakPackageManager(PackageManager):
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
