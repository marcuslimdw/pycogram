import json
import os
from argparse import ArgumentParser
from crypt import mksalt
from getpass import getpass
from secrets import compare_digest

from pycogram import PycoStore, make_checksum, format_key_tree, HASH_METHOD

parser = ArgumentParser('pycogram', 'Simple password manager.')

with open('argument_spec.json') as f:
    arguments = json.load(f)
    for argument in arguments:
        parser.add_argument(*argument['command'], **argument['options'])

args = parser.parse_args()

if args.new:
    new_name = args.new
    if os.path.exists(new_name):
        raise ValueError(f'{new_name} already exists.')

    while True:
        print('Please enter the master key for your new password store twice.')
        master_key = getpass('Master key: ')
        dupe_master_key = getpass('Confirm: ')
        if not compare_digest(master_key, dupe_master_key):
            print('The entered master keys do not match. Please try again.')

        else:
            # Using `if not` in this way does look weird, but I think it is, in general, better practice to have the
            # break at the end.
            break

    salt = mksalt(HASH_METHOD)
    checksum = make_checksum(master_key, salt)

    try:
        with open(new_name, 'w') as f:
            json.dump({'checksum': checksum,
                       'salt': salt,
                       'data': {}}, f)

        print(f'{new_name} successfully created.')

    except PermissionError:
        raise RuntimeError(f'Unable to create {new_name} due to a lack of permissions.')

    # I wonder what this raises on Windows.
    except Exception:
        raise RuntimeError(f'Unable to create {new_name} due to an unknown error.')

else:
    print('Please enter your master key.')
    master_key = getpass('Master key: ')
    original_store = PycoStore.load(args.path, master_key)
    store = original_store
    checksum = store.checksum

    if args.interactive:
        # TODO: interactive mode
        raise NotImplementedError('Interactive mode is not yet supported.')

    else:
        if args.add:
            for group_name in args.add:
                print(f'Please enter the key you wish to create in group {group_name}.')
                key = input('Key: ')
                print(f'Please enter the password you wish to associate with the key {key}.')
                password = getpass('Password: ')
                store = store.add(group_name, key, password)

        if args.extract:
            for group_name in args.extract:
                while True:
                    print(f'Please enter the key in group {group_name} associated with the desired password.')
                    key = input('Key: ')
                    try:
                        print(f'The associated password is: {store[group_name].unlock(key, checksum)}')

                    except KeyError:
                        print(f'The key {key} does not exist in group {group_name}.')
                        print(f'List of keys in {group_name}: {store[group_name].keys()}')

                    else:
                        break

        if args.list is not False:
            if args.list:
                print(format_key_tree(args.path, [group for group in store if group in args.list]))

            else:
                print(format_key_tree(args.path, [group for group in store]))

        if store is not original_store:
            store.save(args.path)
            print(f'Changes written to {args.path} successfully.')
