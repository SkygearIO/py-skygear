class BaseAuthProvider(object):
    def handle_action(self, action, data):
        auth_data = data.get('auth_data', {})
        if action == 'login':
            output = self.login(auth_data)
        elif action == 'logout':
            output = self.logout(auth_data)
        elif action == 'info':
            output = self.info(auth_data)
        return output

    def login(self, auth_data):
        raise NotImplementedError(
            "Subclass of BaseAuthProvider should implement login method.")

    def logout(self, auth_data):
        raise NotImplementedError(
            "Subclass of BaseAuthProvider should implement logout method.")

    def info(self, auth_data):
        raise NotImplementedError(
            "Subclass of BaseAuthProvider should implement info method.")
