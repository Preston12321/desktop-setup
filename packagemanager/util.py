import re
import subprocess

def validate_package_names(name_list):
    for name in name_list:
        if not re.match(r'[a-z0-9_-]+', name):
            print("Error: Invalid package name '%s'" % name, file=sys.stderr)


def pm_run(cmd_line_args):
    # TODO: Maybe do fancy logging & output stuff instead passing stdin/stderr through as-is
    return subprocess.run(cmd_line_args, check=True)
