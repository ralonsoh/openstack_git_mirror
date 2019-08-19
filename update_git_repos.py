#!/usr/bin/python
# -*- coding: utf-8 -*-

from multiprocessing import pool
import os
import subprocess


base_git = 'git://git.openstack.org'
base_dir = '/opt/git_mirror/'
#os.getcwd()
repo_file = base_dir + 'git_repos.txt'


def git_update(directory):
    print('Updating %s' % directory)
    cmds = [['git', 'remote', 'update']]
    for cmd in cmds:
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=directory)
        except subprocess.CalledProcessError as error:
            print('Error during update: %s' % str(error.output))
            raise


def git_clone(directory, repository):
    print('Cloning %s' % repository)
    cmds = [['git', 'clone', '--mirror', repository]]
    for cmd in cmds:
        try:
            subprocess.check_output(cmd, stderr=subprocess.STDOUT, cwd=directory)
        except subprocess.CalledProcessError as error:
            print('Error during clone: %s' % str(error.output))
            raise


print('  --> Updating repositories.')

# Read repo list
repositories = []
with open(repo_file, 'r') as f:
    for line in f:
        line = line.splitlines()[0]
        repo = line.split('/')
        if len(repo) != 2:
            continue
        repo_base = repo[0]
        repo_name = repo[1]
        repositories.append((repo_base, repo_name))

tpool = pool.ThreadPool(MAX_THREADS)
tpool.map(update_or_clone, gen_repos(repositories))

print('  --> Git repositories updated! Process finished.')

