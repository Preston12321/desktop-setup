#!/bin/python3

import yaml
import pyinputplus as pyip
import json
import shutil
import os
import sys

program_list = []
repository_dict = {}

with open("programs.yaml", "r") as file:
    program_list = yaml.safe_load(file)

with open("repositories.yaml", "r") as file:
    repository_dict = yaml.safe_load(file)

if not program_list or not repository_dict:
    exit(1)

# print(json.dumps(program_list, indent=2))

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

for entry in program_list[:]:
    if "deviceTypes" in entry and DEVICE_TYPE not in entry["deviceTypes"]:
        program_list.remove(entry)
        continue

    if "packageDefinitions" in entry:
        for pkg_definition in entry["packageDefinitions"][:]:
            if pkg_definition["packageManager"] not in pkg_managers:
                entry["packageDefinitions"].remove(pkg_definition)

        # If no packageDefinitions remain, program is uninstallable on this system
        if not entry["packageDefinitions"]:
            program_list.remove(entry)
            continue

# Remove all programs with non-existent dependencies
while True:
    removed_program = False
    for entry in program_list[:]:
        if "requires" not in entry:
            continue
        for dependency in entry["requires"]:
            found_program = None
            for program in program_list:
                if program["name"] == dependency:
                    found_program = program
                    break
            if found_program:
                print("Found dependency '%s' of '%s'" %
                      (dependency, entry["name"]))
                # Replace name string with reference to dependency
                i = program_list.index(entry)
                j = entry["requires"].index(dependency)
                program_list[i]["requires"][j] = found_program
            else:
                program_list.remove(entry)
                removed_program = True
                break

    if not removed_program:
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
for entry in program_list:
    if has_circular_dependency(entry, []):
        print("Error: Circular dependency involving program '%s'" %
              entry["name"], file=sys.stderr)
        exit(1)

# Organize packages into "waves" to ensure dependencies are installed in the right order
waves = [[p for p in program_list]]
while True:
    wave = waves[0]
    prev_wave = []
    for program in wave[:]:
        if "requires" not in program:
            continue
        for dependency in program["requires"]:
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


# Go through each "wave" and install each program
for i in range(len(waves)):
    # print("WAVE #%d:" % (i + 1))
    SCRIPT += "\n"
    SCRIPT += "# WAVE #%d:\n" % (i + 1)

    apt_programs = []
    apt_url_programs = []
    pacman_programs = []
    paru_programs = []
    snap_programs = []
    snap_classic_programs = []
    post_install_programs = []

    for program in waves[i]:
        # print("- %s" % program["name"])
        if "postInstallSteps" in program:
            post_install_programs.append(program)

        if "installSteps" in program:
            for line in program["installSteps"]:
                SCRIPT += "%s\n" % line
        else:
            pkg_definition = None
            for pkg_manager in pkg_managers:
                for pkg_def in program["packageDefinitions"]:
                    if pkg_def["packageManager"] == pkg_manager:
                        pkg_definition = pkg_def

            if pkg_definition["packageManager"] == "apt":
                if "installName" in pkg_definition:
                    apt_programs.append(pkg_definition["installName"])
                else:
                    apt_url_programs.append(pkg_definition["installUrl"])
            elif pkg_definition["packageManager"] == "pacman":
                pacman_programs.append(pkg_definition["installName"])
            elif pkg_definition["packageManager"] == "paru":
                paru_programs.append(pkg_definition["installName"])
            elif pkg_definition["packageManager"] == "snap":
                snap_programs.append(pkg_definition["installName"])
            else:
                snap_classic_programs.append(pkg_definition["installName"])

    if apt_programs:
        SCRIPT += "apt install -y %s\n" % list_to_spaced_str(apt_programs)
    if apt_url_programs:
        for i in range(len(apt_url_programs)):
            url = apt_url_programs[i]
            SCRIPT += "curl %s > %d.deb\n" % (url, i)
            SCRIPT += "apt install -y ./%d.deb\n" % i

    if pacman_programs:
        SCRIPT += "pacman -S %s\n" % list_to_spaced_str(pacman_programs)
    if paru_programs:
        SCRIPT += "paru -S %s\n" % list_to_spaced_str(paru_programs)

    if snap_programs:
        SCRIPT += "snap install %s\n" % list_to_spaced_str(snap_programs)
    if snap_classic_programs:
        SCRIPT += "snap install --classic %s\n" % list_to_spaced_str(
            snap_classic_programs)

    for program in post_install_programs:
        for line in program["postInstallSteps"]:
            SCRIPT += "%s\n" % line

with open("install-script.sh", "w") as file:
    file.write(SCRIPT)

# TODO: apt may accept installName OR installUrl
