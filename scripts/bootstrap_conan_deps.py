#!/usr/bin/env python3

"""
This script intended to fill the local conan cache with the packages required
for building the project. Clean build scenario requires running this script
before running the cmake command. Besides that, it may be also required after
the dependencies updates.

Usage:
    bootstrap_conan_deps.py [nlc_url [dns_libs_url]]

`nlc_url` is the URL of AdGuard's NativeLibsCommon repository
(defaults to https://github.com/AdguardTeam/NativeLibsCommon.git).
`nlc_url` is the URL of AdGuard's DnsLibs repository
(defaults to https://github.com/AdguardTeam/DnsLibs.git).
"""

import os
import re
import shutil
import stat
import subprocess
import sys

work_dir = os.path.dirname(os.path.realpath(__file__))
project_dir = os.path.dirname(work_dir)
nlc_url = sys.argv[1] if len(sys.argv) > 1 else 'https://github.com/AdguardTeam/NativeLibsCommon.git'
nlc_dir_name = "native-libs-common"
dns_libs_url = sys.argv[2] if len(sys.argv) > 2 else 'https://github.com/AdguardTeam/DnsLibs.git'
dns_libs_dir_name = "dns-libs"
nlc_versions = []


def on_rm_tree_error(func, path, _):
    """
    Workaround for Windows behavior, where `shutil.rmtree`
    fails with an access error (read only file).
    So, attempt to add write permission and try again.
    """
    if not os.access(path, os.W_OK):
        os.chmod(path, stat.S_IWUSR)
        func(path)
    else:
        raise


def remove_dir_if_exists(dir_path):
    """Remove a directory if it exists, handling read-only files on Windows."""
    if os.path.exists(dir_path):
        os.chdir(work_dir)
        shutil.rmtree(dir_path, onerror=on_rm_tree_error)


def append_required_version(versions, version):
    if version not in versions:
        versions.append(version)


def append_native_libs_versions_from_conanfile(conanfile_path):
    with open(conanfile_path, "r") as file:
        for line in map(str.strip, file.readlines()):
            if line.startswith('self.requires("native_libs_common/') \
                    and ('@adguard/oss"' in line):
                append_required_version(nlc_versions, line.split('@')[0].split('/')[1])


def revision_for_described_version(version):
    described = re.search(r"-g([0-9a-f]+)$", version)
    if described:
        return described.group(1)
    return "v" + version


def find_legacy_conandata_revision(repo_dir, version):
    if re.match(r"^\d+\.\d+\.\d+$", version) is None:
        return None
    result = subprocess.run(
        [
            "git",
            "-C",
            repo_dir,
            "log",
            "--all",
            "--format=%H",
            "-S",
            '"%s"' % version,
            "--",
            "conandata.yml",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    for revision in result.stdout.splitlines():
        conandata = subprocess.run(
            ["git", "-C", repo_dir, "show", "%s:conandata.yml" % revision],
            capture_output=True,
            text=True,
        )
        if conandata.returncode == 0 and ('"%s"' % version) in conandata.stdout:
            return revision
    return None


def run_shell_script(script_path):
    if os.name == "nt":
        subprocess.run(["bash", script_path], check=True, cwd=os.path.dirname(os.path.dirname(script_path)))
    else:
        subprocess.run([script_path], check=True, cwd=os.path.dirname(os.path.dirname(script_path)))


def checkout_conan_recipe_revision(repo_dir, version):
    revision = find_legacy_conandata_revision(repo_dir, version)
    if revision is not None:
        subprocess.run(["git", "-C", repo_dir, "checkout", revision], check=True)
    else:
        subprocess.run(["git", "-C", repo_dir, "checkout", revision_for_described_version(version)], check=True)


def export_conan_dependency(repo_dir, version):
    python_export = os.path.join(repo_dir, "scripts", "export_conan.py")
    if not os.path.exists(python_export):
        checkout_conan_recipe_revision(repo_dir, version)
        python_export = os.path.join(repo_dir, "scripts", "export_conan.py")

    if os.path.exists(python_export):
        subprocess.run(["python3", python_export, version], check=True)
        return

    run_shell_script(os.path.join(repo_dir, "scripts", "export_conan.sh"))


with open(os.path.join(project_dir, "conanfile.py"), "r") as file:
    for line in map(str.strip, file.readlines()):
        if line.startswith('self.requires("native_libs_common/') \
                and ('@adguard/oss"' in line):
            append_required_version(nlc_versions, line.split('@')[0].split('/')[1])
        elif line.startswith('self.requires("dns-libs/') \
                and ('@adguard/oss"' in line):
            dns_libs_version = line.split('@')[0].split('/')[1]

dns_libs_dir = os.path.join(work_dir, dns_libs_dir_name)
remove_dir_if_exists(dns_libs_dir)
subprocess.run(["git", "clone", dns_libs_url, dns_libs_dir], check=True)
os.chdir(dns_libs_dir)

export_conan_dependency(dns_libs_dir, dns_libs_version)
append_native_libs_versions_from_conanfile(os.path.join(dns_libs_dir, "conanfile.py"))
# Not leaving directory causes used-by-another-process error
os.chdir("..")
remove_dir_if_exists(dns_libs_dir)

os.chdir(work_dir)
nlc_dir = os.path.join(work_dir, nlc_dir_name)
remove_dir_if_exists(nlc_dir)
subprocess.run(["git", "clone", nlc_url, nlc_dir], check=True)
os.chdir(nlc_dir)

for v in nlc_versions: # [k for k in items.keys() if k >= min_nlc_version]:
    try:
        export_conan_dependency(nlc_dir, v)
    except:
        if v in nlc_versions:
            raise
        else:
            # Some native_libs_common versions have broken Conan recipes: ignore them.
            continue

# Not leaving directory causes used-by-another-process error
os.chdir("..")
remove_dir_if_exists(nlc_dir)
