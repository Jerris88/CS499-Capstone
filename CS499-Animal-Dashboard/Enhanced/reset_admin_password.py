from config.app_config import AppConfig
from database.admin_auth import AdminAuth


# reset admin password


# set up admin auth connection
admin_auth = AdminAuth(
    user=AppConfig.USERNAME,
    pwd=AppConfig.PASSWORD,
    host=AppConfig.HOST,
    port=AppConfig.PORT,
    db=AppConfig.DB_NAME,
    collection=AppConfig.ADMIN_COLLECTION,
)

username = "admin"
new_password = "AdminSecure2026!"

# update password
password_updated = admin_auth.update_admin_password(username, new_password)

if password_updated:
    print(f"Password updated successfully for user: {username}")
else:
    print(f"Password update failed for user: {username}")

