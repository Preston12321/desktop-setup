import os
import re
import requests
import shutil
import subprocess
import sys
import tempfile

from .base import PackageManagerBase
from .util import validate_package_names, pm_run


def read_deb822_file(filepath):
    """
    Reads the fields in a deb822 format file and returns a dict with its field data

    NOTE: The API of this method assumes that the file has only one "paragraph", as defined
    by deb822 spec. This implementation is also naive in that it expects all fields to be
    "simple" fields. Lastly, any comments, explicit line ordering, or extraneous whitespace
    present in the file will not be available. Details on paragraphs and field types can be
    found in the man page by running `man 5 deb822` or visiting the following web page:
    https://manpages.debian.org/bullseye/dpkg-dev/deb822.5.en.html
    """
    contents = ""
    with open("repo-files/apt/%s" % sources_file["filename"], "r") as f:
        contents = f.read()

    # Parse the file into a dict
    data = dict()
    for key, value in re.findall(r'^([!\"$-,.-9;-~][!-9;-~]*):[\t ]*(.*)', contents, re.M):
        data[key] = value

    return data


def write_deb822_file(filepath, data):
    with open(filepath, "w") as f:
        for key, value in data.items():
            f.write("%s: %s\n" % (key, value))


class AptPackageManager(PackageManagerBase):
    NAME = "apt"
    KEYRING_PATH = "/usr/share/keyrings"
    SOURCES_PATH = "/etc/apt/sources.list.d"

    def __init__(self):
        self.BIN_PATH = shutil.which("apt-get")

        cp = subprocess.run(["lsb_release", "-cs"], text=True, stdout=subprocess.PIPE, check=True)
        self.RELEASE = cp.stdout.replace("\n", "")


    @staticmethod
    def is_present():
        return bool(shutil.which("apt-get"))


    def add_signing_key(self, key):
        if "name" not in key:
            raise Exception("Missing 'name' attribute for key")

        if "filename" not in key:
            raise Exception("Missing 'filename' attribute for key '%s'" % key["name"])

        temp_dir = tempfile.mkdtemp()
        temp_path = "%s/%s" % (temp_dir, key["filename"])

        # Download the key file to a temporary directory for some preliminary checks
        if "url" in key:
            pm_run(["curl", "--create-dirs", "-o", temp_path, key["url"]])
        elif "server" in key and "id" in key:
            pm_run(["gpg", "--no-default-keyring", "--keyring", temp_path, "--keyserver", key["server"], "--recv-keys", key["id"]])
        else:
            raise Exception("Missing either 'url' or 'server' and 'id' attributes for key '%s'" % key["name"])

        key_path = "%s/%s" % (KEYRING_PATH, key["filename"])
        
        p = pm_run(["gpg", "--list-packets", temp_path])
        key_ids = re.findall(r"keyid: ([0-9A-F]+)", p.stdout, re.M)

        # Check the destination keyring dir for pre-existing keys that match this one
        alt_path = key_path
        for entry in os.scandir(KEYRING_PATH):
            if not entry.is_file():
                continue

            p = pm_run(["gpg", "--list-packets", entry.path])
            ids = re.findall(r"keyid: ([0-9A-F]+)", p.stdout, re.M)

            match = True
            for key_id in key_ids:
                if key_id not in ids:
                    match = False

            if match:
                print("Matching key file found for '%s' at '%s'" % (key_ids[0], entry.path))
                alt_path = entry.path
                break

        # Move the downloaded key file from temp dir if no match was found
        if alt_path == key_path:
            shutil.move(temp_path, key_path)

        # Clean up the temp directory
        shutil.rmtree(temp_dir)

        # Return a dict that tells us where the key file was ultimately written to (or found)
        return {key["name"]: alt_path}


    def add_ppa(self, ppa):
        pm_run(["apt-add-repository", "-y", "-P", ppa])


    def add_sources_file(self, sources_file, signing_keys):
        if "filename" not in sources_file:
            raise Exception("Missing 'filename' attribute for sources file")

        defaults = {"Enabled": "yes", "Suites": self.RELEASE}
        overrides = {}
        if "signingKey" in sources_file:
            overrides["Signed-By"] = signing_keys[sources_file["signingKey"]]

        data = read_deb822_file("repo-files/apt/%s" % sources_file["filename"])

        for entry in os.scandir(SOURCES_PATH):
            if not entry.is_file():
                continue
            if read_deb822_file(entry.path).get("URIs", "") == data["URIs"]:
                print("Matching apt sources file for '%s' found at '%s'" % (sources_file["filename"], entry.path))
                return

        data.update(overrides)
        for key, value in defaults.items():
            data.setdefault(key, value)

        write_deb822_file("%s/%s" % (SOURCES_PATH, sources_file["filename"]), data)


    def add_sources(self, sources_data):
        signing_keys = dict()

        if "keys" in sources_data:
            for key in sources_data["keys"]:
                signing_keys.update(self.add_signing_key(key))

        if "ppas" in sources_data:
            for ppa in sources_data["ppas"]:
                self.add_ppa(ppa)

        if "sources_files" in sources_data:
            for sources_file in sources_data["sources_files"]:
                self.add_sources_file(sources_file, signing_keys)

        pm_run([self.BIN_PATH, "update"])


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
            pm_run([self.BIN_PATH, "install", "-y", *name_list])


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
            pm_run([self.BIN_PATH, "install", "-y", deb])

        # TODO: Have this log a WARNING message if it fails, instead of throwing an exception
        # (Use the onerror argument of shutil.rmtree)
        try:
            # TODO: Log message at DEBUG level when logging is implemented
            print("Cleaning up temporary directory '%s'" % temp_dir)
            shutil.rmtree(temp_dir)
        except:
            print("Warning: Failed to delete directory '%s'" % temp_dir)
