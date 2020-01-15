Local git mirror for OpenStack projects.
========================================

This project contains a small script to replicate locally the needed OpenStack
git repositories. This script can be executed periodically to update the
repository list (file "git_repos.txt").

The OpenStack repositories will be stored in the same directory of this
project, where the Python script and the repository list are located.

Crontab example:
```
  # Update git repos
  30 2 * * * root python /opt/git_mirror/update_git_repos.py
```

In Devstack, "local.conf" should contain the location of this git mirror
server:
```
  [local|localrc]]
  GIT_BASE=ssh://<user>@<server_ip>:<git_mirror_directory>
```

