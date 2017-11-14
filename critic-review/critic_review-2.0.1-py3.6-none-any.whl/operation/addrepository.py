# -*- mode: python; encoding: utf-8 -*-
#
# Copyright 2012 Jens Lindström, Opera Software ASA
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may not
# use this file except in compliance with the License.  You may obtain a copy of
# the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.  See the
# License for the specific language governing permissions and limitations under
# the License.

import subprocess
import os
import signal

import api
import background
import gitutils
import htmlutils
from operation import Operation, OperationResult, OperationFailure, Optional, RestrictedString

class AddRepository(Operation):
    def __init__(self):
        Operation.__init__(self, { "name": RestrictedString(allowed=lambda ch: ch != "/", minlength=1, maxlength=64, ui_name="short name"),
                                   "path": RestrictedString(minlength=1, ui_name="path"),
                                   "mirror": Optional({ "remote_url": RestrictedString(maxlength=256, ui_name="source repository"),
                                                        "remote_branch": str,
                                                        "local_branch": str }) })

    def process(self, db, user, name, path, mirror=None):
        if not user.hasRole(db, "repositories"):
            raise OperationFailure(code="notallowed",
                                   title="Not allowed!",
                                   message="Only users with the 'repositories' role can add new repositories.")
        if name.endswith(".git"):
            raise OperationFailure(code="badsuffix_name",
                                   title="Invalid short name",
                                   message="The short name must not end with .git")

        if name == "r":
            raise OperationFailure(code="invalid_name",
                                   title="Invalid short name",
                                   message="The short name 'r' is not allowed since corresponding /REPOSHORTNAME/{SHA1|BRANCH} URLs would conflict with r/REVIEW_ID URLs.")

        path = path.strip("/").rsplit("/", 1)

        if len(path) == 2: base, repository_name = path
        else: base, repository_name = None, path[0]

        repositories_dir = api.critic.settings().paths.repositories

        if base:
            main_base_path = os.path.join(repositories_dir, base)
        else:
            main_base_path = repositories_dir

        main_path = os.path.join(main_base_path, repository_name + ".git")

        cursor = db.cursor()
        cursor.execute("""SELECT name FROM repositories WHERE path=%s""", (main_path,))
        row = cursor.fetchone()
        if row:
            raise OperationFailure(code="duplicaterepository",
                                   title="Duplicate repository",
                                   message="The specified path is already used by repository %s" % row[0])
        cursor.execute("""SELECT name FROM repositories WHERE name=%s""", (name,))
        row = cursor.fetchone()
        if row:
            raise OperationFailure(code="duplicateshortname",
                                   title="Duplicate short name",
                                   message="The specified short name is already in use, please select a different short name.")

        if not os.path.isdir(main_base_path):
            os.makedirs(main_base_path, mode=0o775)

        settings = api.critic.settings()

        def run_git(arguments, cwd):
            argv = [gitutils.git()] + arguments
            process = subprocess.Popen(argv, stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=cwd)
            stdout, stderr = process.communicate()
            if process.returncode != 0:
                raise gitutils.GitError("unexpected output from '%s': %s" % (" ".join(argv), stderr))

        if mirror:
            try:
                run_git(["ls-remote", mirror["remote_url"]], os.getcwd())
            except gitutils.GitError as error:
                raise OperationFailure(code="failedreadremote",
                                       title="Failed to read source repository",
                                       message="Critic failed to read from the specified source repository. The error reported from git " +
                                               "(when running as the system user '%s') was: <pre>%s</pre>" % (settings.system.username, htmlutils.htmlify(str(error))),
                                       is_html=True)

        run_git(["init", "--bare", "--shared", repository_name + ".git"], cwd=main_base_path)
        run_git(["config", "receive.denyNonFastforwards", "false"], cwd=main_path)
        run_git(["config", "critic.name", name], cwd=main_path)

        if settings.system.is_quickstart:
            run_git(["config", "critic.socket", os.path.join(settings.paths.runtime, "sockets", "githook.unix")], cwd=main_path)

        hook_script = os.path.join(
            api.critic.settings().paths.executables, "pre-post-receive")

        # We install the same hook script as the pre-recieve and post-receive
        # hooks.  The script passes its os.path.basename(sys.argv[0]) on to the
        # githook background service, which chooses what to do based on it.
        os.symlink(hook_script, os.path.join(main_path, "hooks", "pre-receive"))
        os.symlink(hook_script, os.path.join(main_path, "hooks", "post-receive"))

        cursor.execute("""INSERT INTO repositories (name, path)
                               VALUES (%s, %s)
                            RETURNING id""",
                       (name, main_path))
        repository_id = cursor.fetchone()[0]

        if mirror:
            cursor.execute("""INSERT INTO trackedbranches (repository, local_name, remote, remote_name, forced, delay)
                                   VALUES (%s, '*', %s, '*', true, '1 day')""",
                           (repository_id, mirror["remote_url"]))

            cursor.execute("""INSERT INTO trackedbranches (repository, local_name, remote, remote_name, forced, delay)
                                   VALUES (%s, %s, %s, %s, true, '1 day')""",
                           (repository_id, mirror["local_branch"], mirror["remote_url"], mirror["remote_branch"]))

            run_git(["symbolic-ref", "HEAD", "refs/heads/" + mirror["local_branch"]], cwd=main_path)

        db.commit()

        if mirror:
            background.utils.wakeup("branchtracker")

        return OperationResult()
