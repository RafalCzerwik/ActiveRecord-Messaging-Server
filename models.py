from clcrypto import hash_password


class User:
    """
    User class representing a user in the system.

    :param str username: user's username
    :param str password: user's password
    :param str salt: user's salt for password hashing
    """
    def __init__(self, username="", password="", salt=""):
        self._id = -1
        self.username = username
        self._hashed_password = hash_password(password, salt)

    @property
    def id(self):
        return self._id

    @property
    def hashed_password(self):
        return self._hashed_password

    def set_password(self, password, salt=""):
        self._hashed_password = hash_password(password, salt)

    @hashed_password.setter
    def hashed_password(self, password):
        self.set_password(password)

    def save_to_db(self, cursor):
        """
        Saves user to the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor

        :rtype: bool
        """
        if self._id == -1:
            sql = """INSERT INTO users(username, hashed_password)
                            VALUES(%s, %s) RETURNING id"""
            values = (self.username, self.hashed_password)
            cursor.execute(sql, values)
            self._id = cursor.fetchone()[0]
            return True
        else:
            sql = """UPDATE Users SET username = %s, hashed_password = %s WHERE id=%s"""
            values = (self.username, self.hashed_password, self.id)
            cursor.execute(sql, values)
            return True

    @staticmethod
    def load_user_by_username(cursor, username):
        """
        Loads user by username from the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor
        :param str username: username to load

        :rtype: User
        """
        sql = "SELECT id, username, hashed_password FROM userr WHERE username=%s"
        cursor.execute(sql, (username,))
        data = cursor.fetchone()
        if data:
            id_, username, hashed_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            loaded_user._hashed_password = hashed_password
            return loaded_user

    @staticmethod
    def load_user_by_id(cursor):
        """
        Loads user by ID from the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor
        :param int id_: user ID to load

        :rtype: User
        """
        sql = "SELECT id, username, hashed_password FROM users WHERE id=%s"
        cursor.execute(sql, (id_))
        data = cursor.fetchone()
        if data:
            id_, username, hash_password = data
            loaded_user = User(username)
            loaded_user._id = id_
            loaded_user._hashed_password = hashed_password
            return loaded_user

    @staticmethod
    def load_all_users(cursor):
        """
        Loads all users from the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor

        :rtype: list[User]
        """
        sql = " SELECT id, username, hashed_password FROM users"
        users = []
        cursor.execute(sql)
        for row in cursor.fetchall():
            id_, username, hashed_password = row
            loaded_user = User()
            loaded_user._id = id_
            loaded_user.username = username
            loaded_user._hashed_password = hashed_password
            users.append(loaded_user)
        return users

    def delete(self, cursor):
        """
        Deletes user from the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor

        :rtype: bool
        """
        sql = "DELETE FROM Users WHERE id=%s"
        cursor.execute(sql, (self.id,))
        self._id = -1
        return True


class Message:
    """
    Message class representing a message in the system.

    :param int from_id: sender's user ID
    :param int to_id: recipient's user ID
    :param str text: message text
    """
    def __init__(self, from_id, to_id, text):
        self._id = -1
        self.from_id = from_id
        self.to_id = to_id
        self.text = text
        self._creation_date = None

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def id(self):
        return self._id

    @staticmethod
    def load_all_messages(cursor, user_id=None):
        """
        Loads all messages from the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor
        :param int user_id: user ID to filter messages (optional)

        :rtype: list[Message]
        """
        if user_id:
            sql = "SELECT id, from_id, to_id, text, creation_date FROM messages WHERE to_id=%s"
            cursor.execute(sql, (user_id,))
        else:
            sql = "SELECT id, from_id, to_id, text, creation_date FROM messages"
            cursor.execute(sql)
            messages = []
            for row in cursor.fetchall():
                id_, from_id, to_id, text, creation_date = row
                loaded_message = Message(from_id, to_id, text)
                loaded_message._id = id_
                loaded_message._creation_date = creation_date
                messages.append(loaded_message)
            return messages

    def save_to_db(self, cursor):
        """
        Saves message to the database.

        :param psycopg2.extensions.cursor cursor: PostgreSQL database cursor

        :rtype: bool
        """
        if self._id == -1:
            sql = """INSERT INTO Messages(from_id, to_id, text)
                            VALUES(%s, %s, %s) RETURNING id, creation_date"""
            values = (self.from_id, self.to_id, self.text)
            self._id, self._creation_date = cursor.fetchone()
            return True
        else:
            sql = """UPDATE Messages SET to_id=%s, from_id=%s, text=%s WHERE id=%s"""
            values = (self.self.from_id, self.to_id, self.text, self.id)
            cursor.execute(sql, values)
            return True