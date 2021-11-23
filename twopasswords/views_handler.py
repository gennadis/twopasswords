from py_cui import PyCUI

from twopasswords.views import view_auth, view_main, view_reg


class ViewsHandler:
    def __init__(self):
        self.registration_view_window = None
        self.authentication_view_window = None
        self.main_view_window = None

    def create_view(self):
        view = PyCUI(8, 8)
        view.toggle_unicode_borders()
        view.set_title("TwoPasswords")

        return view

    def open_view_registration(self):
        """
        Start Registration instance
        """
        self.registration_view_window = self.create_view()
        view_reg.RegistrationView(self.registration_view_window)
        self.registration_view_window.start()

    def close_view_registration(self):
        if self.registration_view_window is None:
            return
        self.registration_view_window.stop()

    def open_view_authentication(self):
        self.authentication_view_window = self.create_view()
        view_auth.AuthenticationView(self.authentication_view_window)
        self.authentication_view_window.start()

    def close_view_authentication(self):
        if self.authentication_view_window is None:
            return
        self.authentication_view_window.stop()

    def open_view_main(self, pragma):
        self.close_view_registration()
        self.close_view_authentication()
        self.main_view_window = self.create_view()
        view_main.MainView(self.main_view_window, pragma)
        self.main_view_window.start()

    def close_view_main(self):
        if self.main_view_window is None:
            return
        self.main_view_window.stop()

    def from_reg_to_main(self):
        self.close_view_registration()
        self.registration_view_window = None
        self.open_view_main(self)
        # self.main_view_window._stopped = False
        # self.main_view_window.start()

    def from_auth_to_main(self, pragma):
        self.close_view_authentication()
        self.open_view_main(self, pragma)


VIEWS_HANDLER = ViewsHandler()
