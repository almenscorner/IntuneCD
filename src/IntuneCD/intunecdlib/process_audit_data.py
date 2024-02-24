#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This module processes the audit data from Intune.
"""

import subprocess

from .logger import log


def _git_installed():
    cmd = ["git", "--version"]
    log("_git_installed", "Running command git --version to check if git is installed.")
    git_version = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if git_version.returncode != 0:
        log("_git_installed", "Git is not installed.")
        return False

    log("_git_installed", "Git is installed.")
    return True


def _configure_git(audit_data, path):
    cmd = [
        "git",
        "-C",
        path,
        "config",
        "--local",
        "user.email",
        f"{audit_data['actor']}",
    ]
    log(
        "_configure_git",
        f"Running command {cmd} to configure git user email to {audit_data['actor']}.",
    )
    subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )

    # configure the user name for git commits
    cmd = [
        "git",
        "-C",
        path,
        "config",
        "--local",
        "user.name",
        f"{audit_data['actor']}",
    ]
    log("_configure_git", f"Running command {cmd} to configure git user name.")
    subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )


def _check_if_git_repo(path, file):
    cmd = ["git", "-C", path, "rev-parse", "--is-inside-work-tree"]
    log("_check_if_git_repo", f"Path is set to {path} and file is set to {file}.")
    log(
        "_check_if_git_repo",
        f"Running command git command {cmd} to determine if the path is a git repo.",
    )
    git_status = subprocess.run(cmd, capture_output=True, text=True, check=False)

    if git_status.stdout.strip() == "true":
        log("_check_if_git_repo", "Path is a git repo.")
        return True

    log("_check_if_git_repo", "Path is not a git repo.")
    return False


def _git_check_modified(path, file):
    cmd = ["git", "-C", path, "diff", "--name-only", f"{file}"]
    log(
        "_git_check_modified",
        f"Running command {cmd} to check if {file} has been modified.",
    )
    result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    return result.stdout


def _git_check_new_file(path, file):
    # check if it is a new file
    cmd = ["git", "-C", path, "ls-files", "--error-unmatch", f"{file}"]
    log(
        "_git_check_new_file",
        f"Running command {cmd} to check if {file} is a new file.",
    )
    new_file_result = subprocess.run(cmd, capture_output=True, text=True, check=False)
    # check if "did not match any file(s) known to git" is in the stderr
    if "did not match any file(s) known to git" in new_file_result.stderr:
        return True

    return False


def _git_commit_changes(audit_data, path, file):
    # commit the changes
    cmd = ["git", "-C", path, "add", f"{file}"]
    log("_git_commit_changes", f"Running command {cmd} to add {file} to the git repo.")
    subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )
    log("_git_commit_changes", f"Committing the changes to {file}.")
    cmd = [
        "git",
        "-C",
        path,
        "commit",
        "-m",
        (
            f"Updated by {audit_data['actor']} on {audit_data['activityDateTime']}, "
            f"change type: {audit_data['activityOperationType']}, result: {audit_data['activityResult']}"
        ),
    ]

    commit = subprocess.run(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
    )

    if commit.returncode == 0:
        log("_git_commit_changes", "Commit was successful.")
    else:
        log("_git_commit_changes", f"Commit was not successful, error: {commit.stderr}")


def process_audit_data(audit_data, path, file):
    """
    Processes the audit data from Intune.

    :param audit_data: The audit data to process.
    :return: The processed audit data.
    """

    log("process_audit_data", f"Processing audit data for {file} in path {path}.")
    # determine if the path we are using is a git repo
    git_repo = _check_if_git_repo(path, file)

    # Commit the changes
    if git_repo:
        # check if git is installed
        if not _git_installed():
            return
        # configure git
        _configure_git(audit_data, path)
        # check if file has been modified
        result = _git_check_modified(path, file)

        if not result:
            file_not_found = _git_check_new_file(path, file)

        if result or file_not_found:
            # commit the changes
            _git_commit_changes(audit_data, path, file)
        else:
            log(
                "process_audit_data",
                f"{file} has not been modified, no changes to commit.",
            )

    log("process_audit_data", "Audit data has been processed.")
