#!/usr/bin/env python3

import getpass
import argparse

from vkasync import VKSyncManager


def main():

    parser = argparse.ArgumentParser(prog='vkasync')
    subparsers = parser.add_subparsers(help='actions')

    # Download audios
    get_parser = subparsers.add_parser('get', help='download audios')
    get_parser.set_defaults(used='get')

    get_parser.add_argument('-l', '--login', type=str, required=True,
                            help='Email or phone number')
    get_parser.add_argument('-p', '--path', type=str,
                            help='Path where to save audios')
    get_parser.add_argument('--rewrite', action='store_true', default=False,
                            help='Rewrite audio file if already exists')

    get_parser.add_argument('-u', '--uid', type=str,
                            help='User\'s page id or name')
    get_parser.add_argument('-g', '--gid', type=str,
                            help='Group\'s page id or name')
#    get_parser.add_argument('-r', '--remove', action='store_true',
#                             default=False,
#                             help='remove audios from vk after download')

    # Manage access tokens
    tk_parser = subparsers.add_parser('token', help='manage tokens')
    tk_parser.set_defaults(used='token')

    tk_parser.add_argument('-a', '--add', action='store_true', default=False)
    tk_parser.add_argument('-r', '--remove', action='store_true',
                           default=False)

    tk_parser.add_argument('-l', '--login', type=str, required=True,
                           help='Email or phone number')

    args = parser.parse_args()

    if 'used' not in args:
        return

    manager = VKSyncManager()

    # Download audios
    if args.used == 'get':
        page_id = args.gid or args.uid
        group_page = bool(args.gid)

        session = manager.open_vksession(args.login)
        if session is None:
            print('Autorization error')
            return

        page_id = manager.name2id(page_id, group_page)
        if page_id is None:
            print('Invalid page name/id')

        errors = manager.get_audios(page_id, args.path, rewrite=args.rewrite)
        print('Process complete with %d errors' % errors)

        if errors:
            print('See %s for details' % manager.log_path)

    # Add new token
    elif args.used == 'token' and args.add:
        if manager.check_login(args.login):
            print('Login already added')
            return

        passwd = getpass.getpass()
        res = manager.add_login(args.login, passwd)
        if res is None:
            print('Autorization error')
        else:
            print('Success')

    # Remove token
    elif args.used == 'token' and args.remove:
        manager.rm_login(args.login)

    manager.disconnect()

if __name__ == '__main__':
    main()
