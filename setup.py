#!/bin/python3

import yaml
import pyinputplus as pyip
import os
import sys
import subprocess
import copy

from packagemanager import AptPackageManager, PacmanPackageManager, SnapPackageManager

TEMP_DIR = "/tmp/desktop-setup"

# TODO: Add flatpak support

def main():
    DEVICE_TYPE = get_device_type()
    PKG_MANAGER = platform_package_manager()
    package_list, repository_dict = load_definitions()

    if not SnapPackageManager.is_present():
        print("Error: Couldn't find snap package manager", file=sys.stderr)
        exit(1)

    # Organized in order of preference
    PKG_MANAGERS = [PKG_MANAGER, SnapPackageManager()]

    for pm in PKG_MANAGERS:
        pm.add_repositories(repository_dict.get(pm.NAME, []))

    package_list = validate_and_match_packages(package_list, DEVICE_TYPE)
    package_list = resolve_dependencies(package_list)

    # Detect circular dependencies
    for entry in package_list:
        if has_circular_dependency(entry):
            print("Error: Circular dependency involving package '%s'" %
                  entry["name"], file=sys.stderr)
            exit(1)

    # Go through each "wave" and install each package
    for wave in packages_to_waves(package_list):
        wave_details = prepare_wave(wave, PKG_MANAGERS)

        run_scripts(wave_details["install_script"])

        for pm in PKG_MANAGERS:
            pm.install_packages(wave_details[pm.NAME])

        run_scripts(wave_details["post_install_scripts"])


def get_device_type():
    return pyip.inputMenu(
        ["Desktop", "Laptop", "Server"],
        prompt="What kind of device is this?\n",
        numbered=True
    ).lower()

def validate_and_match_packages(package_list, device_type):
    matching_pkgs = []

    for entry in package_list:
        # Remove packages that won't be installed on this system because deviceType doesn't match
        if device_type not in entry.get("deviceTypes", [device_type]):
            continue

        if not "packageDefinitions" in entry:
            if not "installScripts" in entry:
                print("Error: Package '%s' needs either installScripts or packageDefinitions" % entry["name"], file=sys.stderr)
                exit(1)
            matching_pkgs.append(entry)
            continue

        if "installScripts" in entry:
            print("Error: Package '%s' can't have both installScripts and packageDefinitions" % entry["name"], file=sys.stderr)
            exit(1)

        # Take intersection of available package managers and managers with packageDefinitions
        matching_pms = [pm for pm in PKG_MANAGERS if pm in entry["packageDefinitions"].keys()]

        if matching_pms:
            matching_pkgs.append(entry)

    return matching_pkgs


def resolve_dependencies(package_list):
    packages = copy.copy(package_list)

    # Resolve names to references in package dependency lists
    for entry in packages[:]:
        if "requires" not in entry:
            continue

        for dependency in entry["requires"]:
            found_package = None
            for package in packages:
                if package["name"] == dependency:
                    found_package = package
                    break
            if not found_package:
                print("Error: Dependency '%s' of '%s' could not be found or won't be installed", file=sys.stderr)
                exit(1)

            print("Found dependency '%s' of '%s'" % (dependency, entry["name"]))
            # Replace name string with reference to dependency
            i = packages.index(entry)
            j = entry["requires"].index(dependency)
            packages[i]["requires"][j] = found_package

    return packages


def run_scripts(scripts):
    for script in scripts:
        # Install scripts run from the directory in which they're located
        cwd = os.path.dirname(script)
        subprocess.run(["/usr/bin/bash", script], cwd=cwd, check=True)


def platform_package_manager():
    if AptPackageManager.is_present():
        return AptPackageManager()
    if PacmanPackageManager.is_present():
        return PacmanPackageManager()
    print("Error: Couldn't determine package manager for platform", file=sys.stderr)
    exit(1)


def load_definitions():
    package_list = []
    repository_dict = {}

    with open("packages.yaml", "r") as file:
        package_list = yaml.safe_load(file)

    with open("repositories.yaml", "r") as file:
        repository_dict = yaml.safe_load(file)

    if not package_list or not repository_dict:
        print("Error: Couldn't load package and repository definitions", file=sys.stderr)
        exit(1)

    return package_list, repository_dict


def prepare_wave(packages, package_managers):
    wave_details = {m: [] for m in package_managers}
    wave_details["install_script"] = []
    wave_details["post_install_script"] = []

    for package in waves[i]:
        if "postInstallScripts" in package:
            wave_details["post_install_scripts"].extend(
                get_scripts_list(package, "postInstallScripts")
            )

        if "installScripts" in package:
            wave_details["install_scripts"].extend(
                get_scripts_list(package, "installScripts")
            )
            continue

        pkg_manager, pkg_definition = best_package_definition(package["packageDefinitions"], package_managers)
        wave_details[pkg_manager] = pkg_definition

    return wave_details


def has_circular_dependency(entry, seen=[]):
    if "requires" not in entry:
        return False
    for dep in entry["requires"]:
        if dep in seen:
            return True
        if has_circular_dependency(dep, seen + [entry]):
            return True


def packages_to_waves(package_list):
    '''
    Organize packages into "waves" to ensure dependencies are installed in the right order
    '''
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
            return waves

        waves.insert(0, prev_wave)


def get_scripts_list(pkg, key):
    cwd = os.getcwd()
    return ["%s/package-files/%s/%s" % (cwd, pkg["name"], s) for s in pkg[key]]


def best_package_definition(package_definitions, package_managers):
    for manager in package_managers:
        if manager in package_definitions.keys():
            return manager, package_definitions[manager]
    return None, None


if __name__ == "__main__":
    main()
