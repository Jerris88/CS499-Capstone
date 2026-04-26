from admin.create_callbacks import register_create_callbacks
from admin.edit_callbacks import register_edit_callbacks
from admin.security_callbacks import register_security_callbacks


# groups all admin-related callbacks into one place
def register_admin_callbacks(app, shelter, admin_auth):
    register_create_callbacks(app, shelter)
    register_edit_callbacks(app, shelter)
    register_security_callbacks(app, admin_auth)