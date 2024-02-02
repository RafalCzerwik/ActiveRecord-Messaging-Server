import argparse

from psycopg2 import connect, OperationalError
from psycopg2.errors import UniqueViolation

from clcrypto import check_password
from models import User

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="username")
parser.add_argument("-p", "--password", help="password (min 8 characters)")
parser.add_argument("-n", "--new_pass", help="new password (min 8 characters)")
parser.add_argument("-l", "--list", help="list all users", action="store_true")
parser.add_argument("-d", "--delete", help="delete user", action="store_true")
parser.add_argument("-e", "--edit", help="edit user", action="store_true")

args = parser.parse_args()


def edit_user(cur, username, password, new_pass):
    """
    Edits user information.
    The function performs the following actions:
        - Loads user information by username from the database,
        - Checks if the user exists,
        - Compares the provided password with the hashed password stored in the database,
        - Updates the user's hashed password if the password is correct and meets the length requirement.

    :param cur: Database cursor
    :param str username: User's username
    :param str password: Current password
    :param str new_pass: New password

    :rtype: None
    :return: Prints messages indicating the outcome of the operation
    """
    user = User.load_user_by_username(cur, username)
    if not user:
        print('User does not exist!!!')
    elif check_password(password, user.hashed_password):
        if len(new_pass) < 8:
            print('Password is to short! It should have minimum 8 characters.')
        else:
            user.hashed_password = new_pass
            user.save_to_db(cur)
            print('Password has benn changed.')
    else:
        print('Incorrect password!')


def delete_user(cur, username, password):
    """
    Deletes a user.
    The function performs the following actions:
        - Loads user information by username from the database,
        - Checks if the user exists,
        - Compares the provided password with the hashed password stored in the database,
        - Deletes the user if the password is correct.

    :param cur: Database cursor
    :param str username: User's username
    :param str password: User's password

    :rtype: None
    :return: Prints messages indicating the outcome of the operation
    """
    user = User.load_user_by_username(cur, username)
    if not user:
        print('User does not exist!!!')
    elif check_password(password, user.hashed_password):
        user.delete(cur)
        print('User successfully deleted!')
    else:
        print('Incorrect password!')


def create_user(cur, username, password):
    """
    Creates a new user.
    The function performs the following actions:
        - Checks if the provided password meets the length requirement,
        - Attempts to create a new user in the database and prints an error message if the user already exists.

    :param cur: Database cursor
    :param str username: User's username
    :param str password: User's password

    :rtype: None
    :return: Prints messages indicating the outcome of the operation
    """
    if len(password) < 8:
        print('Password is too short! It should have minimum 8 characters.')
    else:
        try:
            user = User(username=username, password=password)
            user.save_to_db(cur)
            print('User created successfully!')
        except UniqueViolation as e:
            print('User already exist! ', e)


def list_user(cur):
    """
    Lists all users.
    The function loads all user information from the database and prints their usernames.

    :param cur: Database cursor

    :rtype: None
    :return: Prints usernames of all users
    """
    users = User.load_all_users(cur)
    for user in users:
        print(user.username)


if __name__ == "__main__":
    try:
        cnx = connect(database="workshop_db", user="postgres", password="tracer", host="127.0.0.1")
        cnx.autocommit = True
        cursor = cnx.cursor()
        if args.username and args.password and args.edit and args.new_pass:
            edit_user(cursor, args.username, args.password, args.new_pass)
        elif args.username and args.password and args.delete:
            delete_user(cursor, args.username, args.password)
        elif args.username and args.password:
            create_user(cursor, args.username, args.password)
        elif args.list:
            list_user(cursor)
        else:
            parser.print_help()
        cnx.close()
    except OperationalError as err:
        print('Connection Error: ', err)
