# -*- coding: utf-8 -*-
import subprocess

from .IntuneCDBase import IntuneCDBase


class ProcessAuditData(IntuneCDBase):
    """A class used to process the audit data from Intune."""

    def _git_installed(self):
        """
        Checks if git is installed.
        """
        cmd = ["git", "--version"]
        self.log(
            function="_git_installed",
            msg="Running command git --version to check if git is installed.",
        )
        git_version = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if git_version.returncode != 0:
            self.log(function="_git_installed", msg="Git is not installed.")
            return False

        self.log(function="_git_installed", msg="Git is installed.")
        return True

    def _configure_git(self, audit_record, path):
        """
        Configures git with the user email and name.

        :param audit_record: The audit record to use for the configuration.
        :param path: The path to the git repo.
        """
        cmd = [
            "git",
            "-C",
            path,
            "config",
            "--local",
            "user.email",
            f"{audit_record['actor']}",
        ]
        self.log(
            function="_configure_git",
            msg=f"Running command {cmd} to configure git user email to {audit_record['actor']}.",
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
            f"{audit_record['actor']}",
        ]
        self.log(
            function="_configure_git",
            msg=f"Running command {cmd} to configure git user name.",
        )
        subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

    def _check_if_git_repo(self, path, file):
        """
        Checks if the path is a git repo.

        :param path: The path to check.
        :param file: The file to check.
        """
        cmd = ["git", "-C", path, "rev-parse", "--is-inside-work-tree"]
        self.log(
            function="_check_if_git_repo",
            msg=f"Path is set to {path} and file is set to {file}.",
        )
        self.log(
            function="_check_if_git_repo",
            msg=f"Running command git command {cmd} to determine if the path is a git repo.",
        )
        git_status = subprocess.run(cmd, capture_output=True, text=True, check=False)

        if git_status.stdout.strip() == "true":
            self.log(function="_check_if_git_repo", msg="Path is a git repo.")
            return True

        self.log(function="_check_if_git_repo", msg="Path is not a git repo.")
        return False

    def _git_check_modified(self, path, file):
        """
        Checks if the file has been modified.

        :param path: The path to the git repo.
        :param file: The file to check.
        """
        cmd = ["git", "-C", path, "diff", "--name-only", f"{file}"]
        self.log(
            function="_git_check_modified",
            msg=f"Running command {cmd} to check if {file} has been modified.",
        )
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        return result.stdout

    def _git_check_new_file(self, path, file):
        """
        Checks if the file is a new file.

        :param path: The path to the git repo.
        :param file: The file to check.
        """
        # check if it is a new file
        cmd = ["git", "-C", path, "ls-files", "--error-unmatch", f"{file}"]
        self.log(
            function="_git_check_new_file",
            msg=f"Running command {cmd} to check if {file} is a new file.",
        )
        new_file_result = subprocess.run(
            cmd, capture_output=True, text=True, check=False
        )
        # check if "did not match any file(s) known to git" is in the stderr
        if "did not match any file(s) known to git" in new_file_result.stderr:
            return True

        return False

    def _git_commit_changes(self, audit_record, path, file):
        """
        Commits the changes to the git repo.

        :param audit_record: The audit record to use for the commit.
        :param path: The path to the git repo.
        :param file: The file to commit.
        """
        # commit the changes
        cmd = ["git", "-C", path, "add", f"{file}"]
        self.log(
            function="_git_commit_changes",
            msg=f"Running command {cmd} to add {file} to the git repo.",
        )
        subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )
        self.log(
            function="_git_commit_changes", msg=f"Committing the changes to {file}."
        )
        cmd = [
            "git",
            "-C",
            path,
            "commit",
            "-m",
            (
                f"{audit_record['auditResourceType']} {audit_record['activityOperationType']} by {audit_record['actor']}\n"
                f"Date: {audit_record['activityDateTime']}\n"
                f"result: {audit_record['activityResult']}"
            ),
        ]

        commit = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=False
        )

        if commit.returncode == 0:
            self.log(function="_git_commit_changes", msg="Commit was successful.")
        else:
            self.log(
                function="_git_commit_changes",
                tag="error",
                msg=f"Commit was not successful, error: {commit.stderr[:200] or commit.stdout[:200]}",
            )

    def _get_payload_from_audit_data(self, audit_data, compare_data):
        """
        Gets the payload from the audit data.

        :param audit_data: The audit data to get the payload from.
        :param compare_data: The data to compare the audit data to.
        """

        records = []
        for record in audit_data:
            if record[compare_data["type"]] == compare_data["value"]:
                records.append(record)

        if records:
            # sort the records by activityDateTime
            records.sort(key=lambda x: x["activityDateTime"], reverse=True)
            records = records[0]

        return records

    def process_audit_data(self, audit_data, compare_data, path, file):
        """
        Processes the audit data from Intune.

        :param audit_data: The audit data to process.
        :param compare_data: The data to compare the audit data to.
        :param path: The path to the file.
        :param file: The file to process.
        """

        self.log(
            function="process_audit_data",
            msg=f"Processing audit data for {file} in path {path}.",
        )
        # determine if the path we are using is a git repo
        git_repo = self._check_if_git_repo(path, file)

        # Commit the changes
        if git_repo:
            record = self._get_payload_from_audit_data(audit_data, compare_data)
            if not record:
                self.log(
                    function="process_audit_data",
                    msg=f"No audit data found for {file}.",
                )
                return False
            # check if git is installed
            if not self._git_installed():
                return
            # configure git
            self._configure_git(record, path)
            # check if file has been modified
            result = self._git_check_modified(path, file)

            if not result:
                file_not_found = self._git_check_new_file(path, file)

            if result or file_not_found:
                # commit the changes
                self._git_commit_changes(record, path, file)
            else:
                self.log(
                    function="process_audit_data",
                    msg=f"{file} has not been modified, no changes to commit.",
                )

        self.log(function="process_audit_data", msg="Audit data has been processed.")
