import argparse

from psycopg2 import connect, OperationalError

from clcrypto import check_password
from models import User, Message

parser = argparse.ArgumentParser()
parser.add_argument("-u", "--username", help="username")
parser.add_argument("-p", "--password", help="password (min 8 characters)")
parser.add_argument("-l", "--list", help="list all messages", action="store_true")
parser.add_argument("-t", "--to", help="to")
parser.add_argument("-s", "--send", help="text message to send")

args = parser.parse_args()


def print_user_messages(cur, user):
    """
    Prints messages for a specific user.

    :param psycopg2.extensions.cursor cur: PostgreSQL database cursor
    :param User user: User object

    :rtype: None
    """
    messages = Message.load_all_messages(cur, user.id)
    for message in messages:
        from_ = User.load_user_by_id(cur, message.from_id)
        print(20 * "-")
        print(f'from: {from_.username}')
        print(f'data: {message.creation_date}')
        print(message.text)
        print(20 * "-")


def send_message(cur, from_id, recipient_name, text):
    """
    Sends a message from one user to another.

    :param psycopg2.extensions.cursor cur: PostgreSQL database cursor
    :param int from_id: sender's user ID
    :param str recipient_name: recipient's username
    :param str text: message text

    :rtype: None
    """
    if len(text) > 255:
        print('Message is too long!')
        return
    to = User.load_user_by_username(cur, recipient_name)
    if to:
        message = Message(from_id, to.id, text=text)
        message.save_to_db(cur)
        print('Message send successfully!')
    else:
        print('Recipient does not exist!')


if __name__ == "__main__":
    try:
        cnx = connect(database="workshop_db", user="postgres", password="tracer", host="127.0.0.1")
        cnx.autocommit = True
        cursor = cnx.cursor()
        if args.username and args.password:
            user = User.load_user_by_username(cursor, args.username)
            if check_password(args.password, user.hashed_password):
                if args.list:
                    print_user_messages(cursor, user)
                elif args.to and args.send:
                    send_message(cursor, user.id, args.to, args.send)
                else:
                    parser.print_help()
            else:
                print("Incorrect password or User does not exists!")
        else:
            print("username and password are required")
            parser.print_help()
        cnx.close()
    except OperationalError as err:
        print("Connection Error: ", err)