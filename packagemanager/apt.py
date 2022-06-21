import requests
import shutil
import subprocess
import sys
import tempfile

from .base import PackageManagerBase
from .util import validate_package_names, run_package_manager

class AptPackageManager(PackageManagerBase):
    NAME = "apt"

    def __init__(self):
        self.BIN_PATH = shutil.which("apt-get")

        cp = subprocess.run(["lsb_release", "-cs"], text=True, stdout=subprocess.PIPE, check=True)
        self.RELEASE = cp.stdout.replace("\n", "")


    @staticmethod
    def is_present():
        return bool(shutil.which("apt-get"))


    def add_repositories(self, repo_list):
        for repo in repo_list:
            if "ppa" in repo:
                run_package_manager(["apt-add-repository", "-y", "-P", repo["ppa"]])
                continue

            if "sourcesLine" not in repo or "sourcesFile" not in repo:
                print("Error: Invalid apt repo definition", file=sys.stderr)
                exit(1)

            with open(repo["sourcesFile"], "w") as file:
                file.write(repo["sourcesLine"].replace("${RELEASE}", self.RELEASE))

            if "keyUrl" in repo and "keyFile" in repo:
                run_package_manager(["curl", "--create-dirs", "-o", repo["keyFile"], repo["keyUrl"]])
            elif "keyServer" in repo and "recvKeys" in repo:
                run_package_manager(["apt-key", "adv", "--keyserver", repo["keyServer"], "--recv-keys", repo["recvKeys"]])

        run_package_manager([self.BIN_PATH, "update"])


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
            run_package_manager([self.BIN_PATH, "install", "-y", *name_list])


    def install_from_urls(self, url_list):
        deb_files = []

        if not url_list:
            return

        temp_dir = tempfile.mkdtemp(prefix="apt-files-")

        for i in range(len(url_list)):
            print("Get: %s" % url_list[i])

            content = requests.get(url_list[i]).content
            path = "%s/%d.deb" % (temp_dir, i)

            with open(path, "wb") as file:
                file.write(content)

            deb_files.append(path)

        for deb in deb_files:
            run_package_manager([self.BIN_PATH, "install", "-y", deb])

        # TODO: Have this log a WARNING message if it fails, instead of throwing an exception
        # (Use the onerror argument of shutil.rmtree)
        try:
            # TODO: Log message at DEBUG level when logging is implemented
            print("Cleaning up temporary directory '%s'" % temp_dir)
            shutil.rmtree(temp_dir)
        except:
            print("Warning: Failed to delete directory '%s'" % temp_dir)
