#!/usr/bin/python
# -*- coding: utf-8 -*-

import functools
import multiprocessing
from multiprocessing import pool
import os
import subprocess


# BASE_GIT = 'git://git.openstack.org'  # DEPRECATED
BASE_GIT = 'https://opendev.org'
# Where the repositories are stored.
BASE_DIR, _ = os.path.split(os.path.abspath(__file__))
BASE_DIR += '/'
REPO_FILE = BASE_DIR + 'git_repos.txt'
MAX_THREADS = 2


def _execute_commands(cmds, directory, action):
    for cmd in cmds:
        try:
            # 10 mins max.
            return subprocess.check_output(
                cmd, stderr=subprocess.STDOUT, cwd=directory, timeout=600)
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as \
                error:
            print('Error during %s: %s' % (action, str(error.output)))
            return False


def _git_update(repo_dir):
    print('--> Updating %s' % repo_dir)
    cmds = [['git', 'fetch', 'origin']]
    return _execute_commands(cmds, repo_dir, 'update')


def _git_clone(repo_base_dir, repository):
    print('--> Cloning %s' % repository)
    cmds = [['git', 'clone', '--mirror', repository]]
    return _execute_commands(cmds, repo_base_dir, 'clone')


def _remove_directory(repo_dir):
    print('--> Removing %s' % repo_dir)
    cmds = [['rm', '-fr', repo_dir]]
    return _execute_commands(cmds, None, 'clone')


def update_or_clone(_lock, *repo_tuple):
    repository, repo_base_dir, repo_dir = tuple(*repo_tuple)
    res = None
    if os.path.exists(repo_dir):
        res = _git_update(repo_dir)

    if res is False:
        _remove_directory(repo_dir)

    if not os.path.exists(repo_dir):
        with _lock:
            if not os.path.exists(repo_base_dir):
                os.mkdir(repo_base_dir)
        _git_clone(repo_base_dir, repository)


def gen_repos(repositories):
    for repo in repositories:
        repo_base_dir = BASE_DIR + repo[0] + '/'
        repo_dir = repo_base_dir + repo[1] + '/'
        repository = BASE_GIT + '/' + repo[0] + '/' + repo[1]
        yield repository, repo_base_dir, repo_dir


print('Updating/cloning repositories.')

# Read repo list
repositories = []
with open(REPO_FILE, 'r') as f:
    for line in f:
        line = line.splitlines()[0]
        if line.startswith('#'):
            continue
        repo = line.split('/')
        if len(repo) != 2:
            continue
        repo_base = repo[0]
        repo_name = repo[1]
        repositories.append((repo_base, repo_name))

_lock = multiprocessing.Lock()
tpool = pool.ThreadPool(MAX_THREADS)
_update_or_clone = functools.partial(update_or_clone, _lock)
tpool.map(_update_or_clone, gen_repos(repositories))

print('Git repositories updated! Process finished.')
