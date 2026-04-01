"""
login.py - Login screen for the Store Manager application.
Features: credential verification, username autocomplete, role-based routing,
and a manager-only account creation dialog.
"""
 
import customtkinter as ctk
from tkinter import StringVar
import sys
import os
 
# Add project root to path so sibling modules can be imported
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
 
from db.database import verify_login, create_user, record_login, get_login_history
from utils.session import current_session
 
# ── Theme constants matching the dark blueprint ──────────────────────────────
BG_COLOR        = "#0d1117"
PANEL_COLOR     = "#161b22"
BORDER_COLOR    = "#30363d"
ACCENT_BLUE     = "#1f6feb"
ACCENT_GREEN    = "#3fb950"
ACCENT_RED      = "#f85149"
TEXT_PRIMARY    = "#e6edf3"
TEXT_MUTED      = "#8b949e"
FONT_MONO       = ("Courier New", 12)
FONT_TITLE      = ("Courier New", 22, "bold")
FONT_LABEL      = ("Courier New", 11)
FONT_SMALL      = ("Courier New", 10)
 
 
class LoginView(ctk.CTkFrame):
    """
    The login screen frame. Handles user authentication and routes
    to the appropriate view based on the user's role.
    """
 
    def __init__(self, master, on_login_success):
        """
        Args:
            master: The parent CTk window.
            on_login_success: Callback(userID, role) called after a valid login.
        """
        super().__init__(master, fg_color=BG_COLOR)
        self.master = master
        self.on_login_success = on_login_success
        self.login_history = get_login_history()  # For autocomplete
        self.suggestion_buttons = []              # Autocomplete dropdown widgets
 
        self._build_ui()
 
    # ── UI Construction ───────────────────────────────────────────────────────
 
    def _build_ui(self):
        """Construct all login screen widgets."""
        self.pack(fill="both", expand=True)
 
        # Center container
        container = ctk.CTkFrame(self, fg_color=PANEL_COLOR, corner_radius=8,
                                  border_width=1, border_color=BORDER_COLOR,
                                  width=420, height=480)
        container.place(relx=0.5, rely=0.5, anchor="center")
 
        # ── Header ────────────────────────────────────────────────────────────
        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(pady=(30, 10), padx=30, fill="x")
 
        ctk.CTkLabel(header, text="STORE MANAGER", font=FONT_TITLE,
                     text_color=ACCENT_BLUE).pack(anchor="w")
        ctk.CTkLabel(header, text="v1.0  ·  Sign in to continue",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
 
        # Divider
        ctk.CTkFrame(container, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=30, pady=(10, 20))
 
        # ── Username field ────────────────────────────────────────────────────
        form = ctk.CTkFrame(container, fg_color="transparent")
        form.pack(padx=30, fill="x")
 
        ctk.CTkLabel(form, text="USER ID", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
 
        self.userID_var = StringVar()
        self.userID_var.trace_add("write", self._on_userID_change)
 
        self.userID_entry = ctk.CTkEntry(
            form, textvariable=self.userID_var,
            placeholder_text="Enter your user ID",
            font=FONT_MONO, fg_color="#0d1117",
            border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=40
        )
        self.userID_entry.pack(fill="x")
        self.userID_entry.bind("<Return>", lambda e: self.password_entry.focus())
        self.userID_entry.bind("<FocusOut>", lambda e: self._hide_suggestions())
 
        # Autocomplete dropdown container (shown below the userID field)
        self.suggestion_frame = ctk.CTkFrame(form, fg_color=PANEL_COLOR,
                                              border_width=1, border_color=ACCENT_BLUE,
                                              corner_radius=4)
 
        # ── Password field ────────────────────────────────────────────────────
        ctk.CTkLabel(form, text="PASSWORD", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(16, 4))
 
        self.password_entry = ctk.CTkEntry(
            form, placeholder_text="Enter your password",
            font=FONT_MONO, fg_color="#0d1117", show="●",
            border_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
            height=40
        )
        self.password_entry.pack(fill="x")
        self.password_entry.bind("<Return>", lambda e: self._attempt_login())
 
        # ── Error message label ───────────────────────────────────────────────
        self.error_label = ctk.CTkLabel(form, text="", font=FONT_SMALL,
                                         text_color=ACCENT_RED)
        self.error_label.pack(anchor="w", pady=(6, 0))
 
        # ── Login button ──────────────────────────────────────────────────────
        ctk.CTkButton(
            container, text="SIGN IN", font=("Courier New", 13, "bold"),
            fg_color=ACCENT_BLUE, hover_color="#388bfd",
            text_color="white", height=44, corner_radius=6,
            command=self._attempt_login
        ).pack(padx=30, pady=(4, 10), fill="x")
 
        # ── Create account link (manager-only dialog trigger) ─────────────────
        ctk.CTkButton(
            container, text="Create Account (Managers Only)",
            font=FONT_SMALL, fg_color="transparent",
            hover_color=PANEL_COLOR, text_color=TEXT_MUTED,
            height=28, command=self._open_create_account_dialog
        ).pack(pady=(0, 20))
 
        # ── Footer status bar ─────────────────────────────────────────────────
        footer = ctk.CTkFrame(container, fg_color="#0d1117", corner_radius=0,
                               height=36)
        footer.pack(side="bottom", fill="x")
        ctk.CTkLabel(footer, text="System Status: ONLINE  ·  DB Connection: ✓",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(side="left", padx=12)
 
    # ── Autocomplete Logic ────────────────────────────────────────────────────
 
    def _on_userID_change(self, *args):
        """
        Triggered on every keystroke in the userID field.
        Filters login history and shows matching suggestions.
        """
        typed = self.userID_var.get().lower()
        self._clear_suggestions()
 
        if not typed:
            return
 
        matches = [uid for uid in self.login_history if uid.lower().startswith(typed)]
 
        if matches:
            self.suggestion_frame.pack(fill="x", pady=(2, 0))
            for uid in matches[:5]:  # Show max 5 suggestions
                btn = ctk.CTkButton(
                    self.suggestion_frame, text=uid,
                    font=FONT_MONO, fg_color="transparent",
                    hover_color=BORDER_COLOR, text_color=TEXT_PRIMARY,
                    height=32, anchor="w",
                    command=lambda u=uid: self._select_suggestion(u)
                )
                btn.pack(fill="x", padx=4, pady=1)
                self.suggestion_buttons.append(btn)
 
    def _select_suggestion(self, userID: str):
        """Fill the userID field with the selected suggestion."""
        self.userID_var.set(userID)
        self._hide_suggestions()
        self.password_entry.focus()
 
    def _clear_suggestions(self):
        """Remove all suggestion buttons from the dropdown."""
        for btn in self.suggestion_buttons:
            btn.destroy()
        self.suggestion_buttons = []
 
    def _hide_suggestions(self):
        """Hide the autocomplete dropdown."""
        self._clear_suggestions()
        self.suggestion_frame.pack_forget()
 
    # ── Authentication Logic ──────────────────────────────────────────────────
 
    def _attempt_login(self):
        """
        Validate input fields and verify credentials against the database.
        On success: record login, update session, call on_login_success.
        On failure: show an error message.
        """
        userID = self.userID_var.get().strip()
        password = self.password_entry.get().strip()
 
        # Input validation
        if not userID:
            self._show_error("User ID cannot be empty.")
            return
        if not password:
            self._show_error("Password cannot be empty.")
            return
 
        # Database credential check
        user = verify_login(userID, password)
 
        if user:
            record_login(userID)
            current_session.login(userID, user["role"])
            self._show_error("")  # Clear any previous error
            self.on_login_success(userID, user["role"])
        else:
            self._show_error("Invalid user ID or password.")
            self.password_entry.delete(0, "end")
 
    def _show_error(self, message: str):
        """Display or clear the error message below the password field."""
        self.error_label.configure(text=message)
 
    # ── Create Account Dialog ─────────────────────────────────────────────────
 
    def _open_create_account_dialog(self):
        """
        Open a modal dialog to create a new account.
        Requires the current user to enter THEIR OWN manager credentials first.
        """
        dialog = CreateAccountDialog(self.master)
        self.master.wait_window(dialog)
 
        # Refresh autocomplete history after potential new account creation
        self.login_history = get_login_history()
 
 
class CreateAccountDialog(ctk.CTkToplevel):
    """
    Modal dialog for creating a new user account.
    Requires manager credentials to authorize the action.
    """
 
    def __init__(self, master):
        super().__init__(master)
        self.title("Create New Account")
        self.geometry("400x520")
        self.resizable(False, False)
        self.configure(fg_color=BG_COLOR)
        self.grab_set()  # Make modal
        self._build_ui()
 
    def _build_ui(self):
        """Build the create account form."""
        ctk.CTkLabel(self, text="CREATE ACCOUNT", font=FONT_TITLE,
                     text_color=ACCENT_GREEN).pack(pady=(24, 4), padx=24, anchor="w")
        ctk.CTkLabel(self, text="Manager authorization required",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(padx=24, anchor="w")
 
        ctk.CTkFrame(self, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=24, pady=(12, 16))
 
        form = ctk.CTkFrame(self, fg_color="transparent")
        form.pack(padx=24, fill="x")
 
        # ── Manager auth fields ───────────────────────────────────────────────
        ctk.CTkLabel(form, text="YOUR MANAGER ID", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.mgr_id = ctk.CTkEntry(form, font=FONT_MONO, fg_color="#0d1117",
                                    border_color=BORDER_COLOR,
                                    text_color=TEXT_PRIMARY, height=36)
        self.mgr_id.pack(fill="x")
 
        ctk.CTkLabel(form, text="YOUR MANAGER PASSWORD", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(12, 4))
        self.mgr_pw = ctk.CTkEntry(form, font=FONT_MONO, fg_color="#0d1117",
                                    border_color=BORDER_COLOR, show="●",
                                    text_color=TEXT_PRIMARY, height=36)
        self.mgr_pw.pack(fill="x")
 
        ctk.CTkFrame(form, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", pady=(16, 16))
 
        # ── New account fields ────────────────────────────────────────────────
        ctk.CTkLabel(form, text="NEW USER ID", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(0, 4))
        self.new_id = ctk.CTkEntry(form, font=FONT_MONO, fg_color="#0d1117",
                                    border_color=BORDER_COLOR,
                                    text_color=TEXT_PRIMARY, height=36)
        self.new_id.pack(fill="x")
 
        ctk.CTkLabel(form, text="NEW PASSWORD", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(12, 4))
        self.new_pw = ctk.CTkEntry(form, font=FONT_MONO, fg_color="#0d1117",
                                    border_color=BORDER_COLOR, show="●",
                                    text_color=TEXT_PRIMARY, height=36)
        self.new_pw.pack(fill="x")
 
        ctk.CTkLabel(form, text="ROLE", font=FONT_LABEL,
                     text_color=TEXT_MUTED).pack(anchor="w", pady=(12, 4))
        self.role_var = StringVar(value="employee")
        role_menu = ctk.CTkOptionMenu(form, values=["employee", "manager"],
                                       variable=self.role_var,
                                       fg_color="#0d1117", button_color=ACCENT_BLUE,
                                       font=FONT_MONO, text_color=TEXT_PRIMARY)
        role_menu.pack(fill="x")
 
        # ── Feedback label ────────────────────────────────────────────────────
        self.msg_label = ctk.CTkLabel(form, text="", font=FONT_SMALL,
                                       text_color=ACCENT_RED, wraplength=340)
        self.msg_label.pack(anchor="w", pady=(8, 0))
 
        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(padx=24, pady=16, fill="x")
 
        ctk.CTkButton(btn_row, text="CREATE", font=("Courier New", 12, "bold"),
                      fg_color=ACCENT_GREEN, hover_color="#2ea043",
                      text_color="white", height=38,
                      command=self._submit).pack(side="left", expand=True,
                                                  fill="x", padx=(0, 6))
        ctk.CTkButton(btn_row, text="CANCEL", font=("Courier New", 12),
                      fg_color=BORDER_COLOR, hover_color="#484f58",
                      text_color=TEXT_PRIMARY, height=38,
                      command=self.destroy).pack(side="left", expand=True, fill="x")
 
    def _submit(self):
        """
        Validate manager credentials, then create the new account if authorized.
        """
        mgr_id = self.mgr_id.get().strip()
        mgr_pw = self.mgr_pw.get().strip()
        new_id = self.new_id.get().strip()
        new_pw = self.new_pw.get().strip()
        role   = self.role_var.get()
 
        # Verify that the authorizing user is actually a manager
        manager = verify_login(mgr_id, mgr_pw)
        if not manager:
            self._show_msg("Manager credentials are incorrect.", ACCENT_RED)
            return
        if manager["role"] != "manager":
            self._show_msg("Only managers can create accounts.", ACCENT_RED)
            return
 
        # Attempt account creation
        success, message = create_user(new_id, new_pw, role)
        if success:
            self._show_msg(message, ACCENT_GREEN)
            self.after(1500, self.destroy)  # Auto-close on success
        else:
            self._show_msg(message, ACCENT_RED)
 
    def _show_msg(self, text: str, color: str):
        """Display a feedback message in the given color."""
        self.msg_label.configure(text=text, text_color=color)