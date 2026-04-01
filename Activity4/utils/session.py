"""
session.py - Manages the active user session and inactivity timeout logic.
"""

import time

# Timeout duration in seconds (e.g., 300 = 5 minutes)
TIMEOUT_SECONDS = 300


class Session:
    """
    Tracks the currently logged-in user and monitors for inactivity.
    Call reset_timer() on any user interaction to prevent timeout.
    """

    def __init__(self):
        self.userID = None
        self.role = None
        self.last_active = None
        self._timeout_callback = None  # Function to call on timeout

    def login(self, userID: str, role: str):
        """Set session data after a successful login."""
        self.userID = userID
        self.role = role
        self.reset_timer()

    def logout(self):
        """Clear session data on logout."""
        self.userID = None
        self.role = None
        self.last_active = None

    def is_logged_in(self) -> bool:
        """Check if a user is currently logged in."""
        return self.userID is not None

    def reset_timer(self):
        """Reset the inactivity timer. Call this on any user interaction."""
        self.last_active = time.time()

    def is_timed_out(self) -> bool:
        """Return True if the session has exceeded the inactivity timeout."""
        if self.last_active is None:
            return False
        return (time.time() - self.last_active) > TIMEOUT_SECONDS

    def set_timeout_callback(self, callback):
        """Register a function to call when the session times out."""
        self._timeout_callback = callback

    def check_timeout(self, app_widget):
        """
        Called repeatedly via widget.after() to check for inactivity.
        Triggers logout and callback if timeout is exceeded.
        """
        if self.is_logged_in() and self.is_timed_out():
            self.logout()
            if self._timeout_callback:
                self._timeout_callback()
        else:
            # Schedule next check in 10 seconds
            app_widget.after(10000, lambda: self.check_timeout(app_widget))


# Global session instance shared across the app
current_session = Session()
