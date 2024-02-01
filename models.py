from clcrypto

@staticmethod
def load_user_by_username(cursor, username):
    sql = "SELECT id, username, hashed_password FROM userr WHERE username=%s"
    cursor.execute(sql, (username,))
    data = cursor.fetchone()
    if data:
        id_, username, hashed_password = data
        loaded_user = User(username)
        loaded_user._id = id_
        loaded_user._hashed_password = hashed_password
        return loaded_user