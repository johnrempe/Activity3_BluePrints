"""
main.py - Entry point for the Store Manager GUI application.
Handles app initialization, screen switching, and the inactivity timeout loop.
"""

import customtkinter as ctk
import sys
import os

# Ensure submodules are importable
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from db.database import initialize_db
from utils.session import current_session
from views.login import LoginView
from views.manager_view import ManagerView
from views.employee_view import EmployeeView

# ── App-wide appearance ───────────────────────────────────────────────────────
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


class StoreManagerApp(ctk.CTk):
    """
    Root application window. Manages which view (login/manager/employee)
    is currently displayed, and runs the inactivity timeout check loop.
    """

    def __init__(self):
        super().__init__()
        self.title("Store Manager v1.0")
        self.geometry("1100x700")
        self.minsize(900, 600)
        self.configure(fg_color="#0d1117")

        # Bind all mouse/keyboard events to reset inactivity timer
        self.bind_all("<Motion>",   lambda e: current_session.reset_timer())
        self.bind_all("<KeyPress>", lambda e: current_session.reset_timer())
        self.bind_all("<Button>",   lambda e: current_session.reset_timer())

        # Initialize the database (creates tables + default admin if needed)
        initialize_db()

        # Register timeout callback and start the polling loop
        current_session.set_timeout_callback(self._on_timeout)
        self._start_timeout_loop()

        # Show the login screen on startup
        self._show_login()

    # ── Screen Management ─────────────────────────────────────────────────────

    def _clear_screen(self):
        """Destroy all current widgets before switching screens."""
        for widget in self.winfo_children():
            widget.destroy()

    def _show_login(self):
        """Display the login screen."""
        self._clear_screen()
        LoginView(self, on_login_success=self._on_login_success)

    def _on_login_success(self, userID: str, role: str):
        """
        Called by LoginView after a successful login.
        Routes to the correct view based on the user's role.
        """
        self._clear_screen()

        if role == "manager":
            ManagerView(self, on_logout=self._show_login)
        else:
            EmployeeView(self, on_logout=self._show_login)

        # Start timeout monitoring now that a user is logged in
        self._start_timeout_loop()

    # ── Inactivity Timeout ────────────────────────────────────────────────────

    def _start_timeout_loop(self):
        """Begin the recurring inactivity check (every 10 seconds)."""
        self.after(10000, self._check_timeout)

    def _check_timeout(self):
        """
        Check if the current session has timed out.
        If so, trigger logout. Otherwise, schedule the next check.
        """
        if current_session.is_logged_in() and current_session.is_timed_out():
            self._on_timeout()
        else:
            self.after(10000, self._check_timeout)

    def _on_timeout(self):
        """
        Called when the inactivity timer expires.
        Logs out the user and returns to the login screen.
        """
        if current_session.is_logged_in():
            current_session.logout()

        self._clear_screen()

        # Show timeout notice on the login screen
        LoginView(self, on_login_success=self._on_login_success)
        self._show_timeout_banner()

    def _show_timeout_banner(self):
        """Display a dismissable timeout notification at the top of the screen."""
        banner = ctk.CTkFrame(self, fg_color="#3d1f00", corner_radius=0, height=36)
        banner.place(relx=0, rely=0, relwidth=1)

        ctk.CTkLabel(
            banner,
            text="⏱  Session expired due to inactivity. Please sign in again.",
            font=("Courier New", 11), text_color="#e3b341"
        ).pack(side="left", padx=16)

        ctk.CTkButton(
            banner, text="✕", width=30, height=24,
            fg_color="transparent", hover_color="#5a2d00",
            text_color="#e3b341", font=("Courier New", 12),
            command=banner.destroy
        ).pack(side="right", padx=8)


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    app = StoreManagerApp()
    app.mainloop()
