#!/usr/bin/env python
"""Upload a file to a Nextcloud instance then share with link."""

import argparse
import getpass
from os.path import basename, exists
from posixpath import join as pjoin

import keyring
import pyperclip

from . import nextcloud

NEXTCLOUD_URL = "https://0x20.eu/nc/"
DEST_DIR = pjoin("xchange", "img")


def main(args=None):
    ap = argparse.ArgumentParser(usage=__doc__.splitlines()[0])
    ap.add_argument(
        "-u", "--url", default=NEXTCLOUD_URL, help="Nextcloud instance URL (default: %(default)s)"
    )
    ap.add_argument(
        "-d",
        "--destdir",
        default=DEST_DIR,
        help="Remote destination directory (default: %(default)s).",
    )
    ap.add_argument("-U", "--user", help="Nextcloud user name (default: local username)")
    ap.add_argument("-P", "--password", help="Nextcloud password (default: use keyring)")
    ap.add_argument(
        "-p", "--preview", action="store_true", help="Add '/preview' suffix to share link"
    )
    ap.add_argument("-v", "--verbose", action="store_true", help="Be more verbose.")
    ap.add_argument("srcfile", help="Local source file.")
    args = ap.parse_args(args)

    if not exists(args.srcfile):
        ap.print_help()
        return "\nFile not found: {}".format(args.srcfile)

    nc = nextcloud.Client(args.url, debug=args.verbose)

    user = args.user if args.user else getpass.getuser()

    password = args.password if args.password else keyring.get_password(args.url, user)

    if not password:
        return "No password found in keyring for '{}' on '{}'.".format(user, args.url)

    nc.login(args.user, password)

    bn = basename(args.srcfile)
    dst = pjoin(args.destdir, bn)
    nc.put_file(dst, args.srcfile)

    link_info = nc.share_file_with_link(dst)
    link_url = link_info.get_link()

    if args.preview:
        link_url += "/preview"

    if args.verbose:
        print("Share link URL: {}".format(link_url))

    pyperclip.copy(link_url)


if __name__ == "__main__":
    import sys

    sys.exit(main() or 0)
