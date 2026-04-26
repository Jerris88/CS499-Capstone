from pymongo import MongoClient
from werkzeug.security import generate_password_hash, check_password_hash


# handles admin login and password security
class AdminAuth:

    def __init__(self, user, pwd, host, port, db, collection="admin_users"):
        self.client = self.connect(user, pwd, host, port, db)
        self.database = self.client[db]
        self.collection = self.database[collection]

    # connect to MongoDB for admin users
    def connect(self, user, pwd, host, port, db):
        if user and pwd:
            return MongoClient(
                f"mongodb://{user}:{pwd}@{host}:{port}/?authSource={db}"
            )

        return MongoClient(f"mongodb://{host}:{port}/")

    # find admin account by username
    def find_user(self, username):
        return self.collection.find_one({"username": username})

    # create a new admin account with a hashed password
    def create_admin_user(self, username, password):
        if self.find_user(username):
            return False

        admin_record = {
            "username": username,
            "password_hash": generate_password_hash(password),
            "role": "admin",
        }

        self.collection.insert_one(admin_record)
        return True

    # check login password against saved hash
    def verify_admin_user(self, username, password):
        user_record = self.find_user(username)

        if not user_record:
            return False

        stored_hash = user_record.get("password_hash")

        if not stored_hash:
            return False

        return check_password_hash(stored_hash, password)

    # replace saved password hash for an admin account
    def update_admin_password(self, username, new_password):
        if not self.find_user(username):
            return False

        result = self.collection.update_one(
            {"username": username},
            {"$set": {"password_hash": generate_password_hash(new_password)}},
        )

        return result.acknowledged

    # delete admin account if it exists
    def delete_admin_user(self, username):
        result = self.collection.delete_one({"username": username})
        return result.deleted_count > 0