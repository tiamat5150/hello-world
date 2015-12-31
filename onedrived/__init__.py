# encoding: utf-8

import os
import pkgutil
from pwd import getpwnam, getpwuid


__project__ = 'onedrived'
__author__ = 'Xiangyu Bu'
__email__ = 'xybu92@live.com'
__version__ = '2.0.0'
__homepage__ = 'https://github.com/xybu/onedrive-d'


def get_current_os_user():
    """
    Find the real user who runs the current process. Return a tuple of uid, username, homedir.
    :rtype: (int, str, str, int)
    """
    user_name = os.getenv('SUDO_USER')
    if not user_name:
        user_name = os.getenv('USER')
    if user_name:
        pw = getpwnam(user_name)
        user_uid = pw.pw_uid
    else:
        # If cannot find the user, use ruid instead.
        user_uid = os.getresuid()[0]
        pw = getpwuid(user_uid)
        user_name = pw.pw_name
    user_gid = pw.pw_gid
    user_home = pw.pw_dir
    return user_uid, user_name, user_home, user_gid


OS_USER_ID, OS_USER_NAME, OS_USER_HOME, OS_USER_GID = get_current_os_user()
OS_HOSTNAME = os.uname()[1]


def get_content(file_name, pkg_name='onedrived', is_text=True):
    """
    Read a resource file in data/.
    :param str file_name:
    :param str pkg_name:
    :param True | False is_text: True to indicate the text is UTF-8 encoded.
    :return str | bytes: Content of the file.
    """
    content = pkgutil.get_data(pkg_name, 'data/' + file_name)
    if is_text:
        content = content.decode('utf-8')
    return content


def mkdir(path):
    os.makedirs(path, mode=0o700)
    os.chown(path, OS_USER_ID, OS_USER_GID)
