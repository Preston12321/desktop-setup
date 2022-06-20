import re

def validate_package_names(name_list):
    for name in name_list:
        if not re.match(r'[a-z0-9_-]+', name):
            print("Error: Invalid package name '%s'" % name, file=sys.stderr)
