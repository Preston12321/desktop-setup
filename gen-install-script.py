#!/bin/python3

import yaml
import pyinputplus as pyip
import json
import shutil
import os
import sys

package_list = []
repository_dict = {}

with open("packages.yaml", "r") as file:
    package_list = yaml.safe_load(file)

with open("repositories.yaml", "r") as file:
    repository_dict = yaml.safe_load(file)

if not package_list or not repository_dict:
    exit(1)

# print(json.dumps(package_list, indent=2))

DEVICE_TYPE = pyip.inputMenu(
    ["Desktop", "Laptop", "Server"],
    prompt="What kind of device is this?\n",
    numbered=True
).lower()

apt = shutil.which("apt")
pacman = shutil.which("pacman")
PKG_MANAGER = "apt" if apt else "pacman"

SCRIPT = "#!/bin/bash\n"

repository_list = repository_dict[PKG_MANAGER]

if PKG_MANAGER == "apt":
    for repo in repository_list:
        if "ppa" in repo:
            SCRIPT += "apt-add-repository -y -P %s\n" % repo["ppa"]
        elif "sourcesLine" in repo and "sourcesFile" in repo:
            SCRIPT += "echo '%s' > '%s'\n" % (
                repo["sourcesLine"], repo["sourcesFile"])
            if "keyUrl" in repo and "keyFile" in repo:
                SCRIPT += "curl --create-dirs -o '%s' %s\n" % (
                    repo["keyFile"], repo["keyUrl"])
            elif "keyServer" in repo and "recvKeys" in repo:
                SCRIPT += "apt-key adv --keyserver %s --recv-keys %s\n" % (
                    repo["keyServer"], repo["recvKeys"])
        else:
            print("Error: Invalid apt repo definition", file=sys.stderr)
            exit(1)
    SCRIPT += "apt update\n"

# Organized in order of preference
pkg_managers = [PKG_MANAGER, "snap", "snap-classic"]

if PKG_MANAGER == "pacman":
    pkg_managers.insert(1, "paru")

for entry in package_list[:]:
    if "deviceTypes" in entry and DEVICE_TYPE not in entry["deviceTypes"]:
        package_list.remove(entry)
        continue

    if "packageDefinitions" in entry:
        for pkg_definition in entry["packageDefinitions"][:]:
            if pkg_definition["packageManager"] not in pkg_managers:
                entry["packageDefinitions"].remove(pkg_definition)

        # If no packageDefinitions remain, package is uninstallable on this system
        if not entry["packageDefinitions"]:
            package_list.remove(entry)
            continue

# Remove all packages with non-existent dependencies
while True:
    removed_package = False
    for entry in package_list[:]:
        if "requires" not in entry:
            continue
        for dependency in entry["requires"]:
            found_package = None
            for package in package_list:
                if package["name"] == dependency:
                    found_package = package
                    break
            if found_package:
                print("Found dependency '%s' of '%s'" %
                      (dependency, entry["name"]))
                # Replace name string with reference to dependency
                i = package_list.index(entry)
                j = entry["requires"].index(dependency)
                package_list[i]["requires"][j] = found_package
            else:
                package_list.remove(entry)
                removed_package = True
                break

    if not removed_package:
        break


def has_circular_dependency(entry, seen):
    if "requires" not in entry:
        return False
    for dep in entry["requires"]:
        if dep in seen:
            return True
        if has_circular_dependency(dep, seen + [entry]):
            return True


# Detect circular dependencies
for entry in package_list:
    if has_circular_dependency(entry, []):
        print("Error: Circular dependency involving package '%s'" %
              entry["name"], file=sys.stderr)
        exit(1)

# Organize packages into "waves" to ensure dependencies are installed in the right order
waves = [[p for p in package_list]]
while True:
    wave = waves[0]
    prev_wave = []
    for package in wave[:]:
        if "requires" not in package:
            continue
        for dependency in package["requires"]:
            if dependency in wave:
                wave.remove(dependency)
            if dependency not in prev_wave:
                prev_wave.append(dependency)

    if not prev_wave:
        break

    waves.insert(0, prev_wave)


def list_to_spaced_str(items):
    result = ""
    for item in items:
        result += " " + item
    if result:
        return result[1:]
    return result


# Go through each "wave" and install each package
for i in range(len(waves)):
    # print("WAVE #%d:" % (i + 1))
    SCRIPT += "\n"
    SCRIPT += "# WAVE #%d:\n" % (i + 1)

    apt_packages = []
    apt_url_packages = []
    pacman_packages = []
    paru_packages = []
    snap_packages = []
    snap_classic_packages = []
    post_install_packages = []

    for package in waves[i]:
        # print("- %s" % package["name"])
        if "postInstallSteps" in package:
            post_install_packages.append(package)

        if "installSteps" in package:
            for line in package["installSteps"]:
                SCRIPT += "%s\n" % line
        else:
            pkg_definition = None
            for pkg_manager in pkg_managers:
                for pkg_def in package["packageDefinitions"]:
                    if pkg_def["packageManager"] == pkg_manager:
                        pkg_definition = pkg_def

            if pkg_definition["packageManager"] == "apt":
                if "installName" in pkg_definition:
                    apt_packages.append(pkg_definition["installName"])
                else:
                    apt_url_packages.append(pkg_definition["installUrl"])
            elif pkg_definition["packageManager"] == "pacman":
                pacman_packages.append(pkg_definition["installName"])
            elif pkg_definition["packageManager"] == "paru":
                paru_packages.append(pkg_definition["installName"])
            elif pkg_definition["packageManager"] == "snap":
                snap_packages.append(pkg_definition["installName"])
            else:
                snap_classic_packages.append(pkg_definition["installName"])

    if apt_packages:
        SCRIPT += "apt install -y %s\n" % list_to_spaced_str(apt_packages)
    if apt_url_packages:
        for i in range(len(apt_url_packages)):
            url = apt_url_packages[i]
            SCRIPT += "curl %s > %d.deb\n" % (url, i)
            SCRIPT += "apt install -y ./%d.deb\n" % i

    if pacman_packages:
        SCRIPT += "pacman --noconfirm -S %s\n" % list_to_spaced_str(
            pacman_packages)
    if paru_packages:
        SCRIPT += "paru --skipreview -S %s\n" % list_to_spaced_str(
            paru_packages)

    if snap_packages:
        SCRIPT += "snap install %s\n" % list_to_spaced_str(snap_packages)
    if snap_classic_packages:
        SCRIPT += "snap install --classic %s\n" % list_to_spaced_str(
            snap_classic_packages)

    for package in post_install_packages:
        for line in package["postInstallSteps"]:
            SCRIPT += "%s\n" % line

with open("install-script.sh", "w") as file:
    file.write(SCRIPT)

# TODO: apt may accept installName OR installUrl
