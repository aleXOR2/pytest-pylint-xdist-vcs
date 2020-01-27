"""Functions to get information from svn."""
import logging
import os.path
import re
import subprocess


LOG = logging.getLogger('pytest_pylint_xdist_vcs')


def repository_root(path,):
    """Returns the root of the repository as an absolute path."""
    try:
        svn_info = subprocess.check_output('svn info {}'.format(path), shell=True, stderr=subprocess.STDOUT).decode()
        filtered_lines = list(filter_lines(svn_info, r'^(Working Copy Root Path\:)\s+(\S+)$')) # Fixme:no filter output
        if filtered_lines:
            return filtered_lines[1]
    except subprocess.CalledProcessError:
        LOG.warning('Svn is not installed, of unsupported version or working copy is damaged.\n \
          Hint: please run `svn info .` inside working copy to trace rootcause')
    return None


def get_mod_files(root):
    """Returns a list of files that has been modified since the last commit.
    Args:
      root: string representing rootpath of the repository, it has to be an absolute path.
    Returns: a list with unique modified py files
    """
    assert os.path.isabs(root), "Root has to be absolute, got: %s" % root

    svn_status_output = subprocess.check_output('svn diff --summarize -r PREV:COMMITTED ' + root, shell=True).decode()
    filtered_paths = list(filter_lines(svn_status_output, r'^\s*[ AM]+\s+([\/\w\- ]+\.py)$'))
    return filtered_paths


def filter_lines(lines, regex):
    """Filters out the lines not matching the pattern.
    Args:
      lines: list[string]: lines to filter.
      pattern: string: regular expression to filter out lines.
    Returns: list[string]: the list of filtered lines.
    """
    pattern = re.compile(regex, flags=re.MULTILINE)
    matches_iter = re.finditer(pattern, lines)
    for match in matches_iter:
        if match.groups():
            for group in match.groups():
                yield group
        else:
            yield match.group(0)
