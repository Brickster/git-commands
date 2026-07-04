import os
import sys


def check(min_version: tuple[int, ...] = (3, 10)) -> None:
    if sys.version_info < min_version:
        cmd = os.path.basename(sys.argv[0]).replace('git-', 'git ')
        version = f'{sys.version_info.major}.{sys.version_info.minor}'
        required = '.'.join(str(v) for v in min_version)
        sys.exit(f'error: {cmd} requires Python {required} or later (found {version})')
