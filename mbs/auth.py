from os.path import join

class AbstractAuthentication(object):
    def current_user_name(self):
        """obtain current user name from the current request
        current request is obtained from flask request thread local
        object
        """
        raise NotImplementedError

    def login(self, username):
        """login the user, sets whatever request information is necessary
        (usually, session['username'] = username)
        """
        raise NotImplementedError

    def logout(self):
        """logs out the user, sets whatever request information is necessary
        usually, session.pop('username')
        """
        raise NotImplementedError
    def is_admin(self, username):
        """Returns boolean, if the current user is an admin or not
        """
        raise NotImplementedError

    def can_write(self, path, username):
        raise NotImplementedError

class SingleUserAuthenticationBackend(object):
    def __init__(self, admin=False):
        self.admin = admin

    def current_username(self):
        return "defaultuser"

    def is_admin(self, username):
        return self.admin

    def can_write(self, path, username):
        return True
