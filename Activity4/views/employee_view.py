"""
employee_view.py - Dashboard view for employee-role users.
Shows limited navigation: Dashboard, Sales, Merchandise only.
Employees cannot access Expenses or Employees screens.
"""

import customtkinter as ctk
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.session import current_session

# ── Theme constants ───────────────────────────────────────────────────────────
BG_COLOR      = "#0d1117"
PANEL_COLOR   = "#161b22"
BORDER_COLOR  = "#30363d"
ACCENT_BLUE   = "#1f6feb"
ACCENT_GREEN  = "#3fb950"
ACCENT_RED    = "#f85149"
ACCENT_PURPLE = "#bc8cff"
TEXT_PRIMARY  = "#e6edf3"
TEXT_MUTED    = "#8b949e"
FONT_MONO     = ("Courier New", 12)
FONT_TITLE    = ("Courier New", 18, "bold")
FONT_LABEL    = ("Courier New", 11)
FONT_SMALL    = ("Courier New", 10)

# Employees only get access to these sections
NAV_ITEMS = [
    ("Dashboard",   ACCENT_BLUE),
    ("Sales",       TEXT_PRIMARY),
    ("Merchandise", TEXT_PRIMARY),
]


class EmployeeView(ctk.CTkFrame):
    """
    Limited-access dashboard for employee users.
    Does NOT include Expenses or Employees sections.
    """

    def __init__(self, master, on_logout):
        """
        Args:
            master: Parent CTk window.
            on_logout: Callback to invoke when the user logs out.
        """
        super().__init__(master, fg_color=BG_COLOR)
        self.on_logout = on_logout
        self.active_section = "Dashboard"
        self._build_ui()

    def _build_ui(self):
        """Construct sidebar + main content area."""
        self.pack(fill="both", expand=True)

        # ── Sidebar ───────────────────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, fg_color=BG_COLOR, width=240,
                                border_width=1, border_color=BORDER_COLOR,
                                corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        ctk.CTkLabel(sidebar, text="STORE MANAGER", font=("Courier New", 14, "bold"),
                     text_color=ACCENT_BLUE).pack(padx=20, pady=(20, 2), anchor="w")
        ctk.CTkLabel(sidebar, text=f"v1.0  ·  Employee  |  {current_session.userID}",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(padx=20, anchor="w")
        ctk.CTkFrame(sidebar, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=20, pady=(12, 8))

        self.nav_buttons = {}
        for label, color in NAV_ITEMS:
            btn = ctk.CTkButton(
                sidebar, text=f"  {label}",
                font=FONT_MONO, anchor="w",
                fg_color=ACCENT_BLUE if label == "Dashboard" else "transparent",
                hover_color="#21262d",
                text_color="white" if label == "Dashboard" else color,
                height=42, corner_radius=6,
                command=lambda l=label: self._navigate(l)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[label] = btn

        # Locked items shown as disabled so employee knows they exist but can't access them
        for label in ["Expenses", "Employees"]:
            ctk.CTkButton(
                sidebar, text=f"  {label}  🔒",
                font=FONT_MONO, anchor="w",
                fg_color="transparent", hover_color="transparent",
                text_color=BORDER_COLOR, height=42, state="disabled"
            ).pack(fill="x", padx=12, pady=2)

        ctk.CTkFrame(sidebar, fg_color="transparent").pack(expand=True)
        ctk.CTkButton(sidebar, text="  Logout", font=FONT_MONO, anchor="w",
                      fg_color="transparent", hover_color="#21262d",
                      text_color=ACCENT_RED, height=38,
                      command=self._logout).pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(sidebar, text="System Status: ONLINE\nDB Connection: ✓",
                     font=FONT_SMALL, text_color=TEXT_MUTED,
                     justify="left").pack(padx=20, pady=(4, 16), anchor="w")

        # ── Content area ──────────────────────────────────────────────────────
        self.content_area = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)
        self._show_dashboard()

    def _navigate(self, section: str):
        """Switch active section and update sidebar."""
        self.active_section = section
        for label, btn in self.nav_buttons.items():
            if label == section:
                btn.configure(fg_color=ACCENT_BLUE, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)

        for widget in self.content_area.winfo_children():
            widget.destroy()

        if section == "Dashboard":
            self._show_dashboard()
        else:
            self._show_placeholder()

    def _show_dashboard(self):
        """Employee dashboard — shows sales and merchandise quick links only."""
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(header, text="DASHBOARD / HOME SCREEN",
                     font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text=f"Welcome, {current_session.userID}",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkFrame(self.content_area, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=30, pady=(10, 20))

        ctk.CTkLabel(self.content_area, text="NAVIGATION LINKS",
                     font=("Courier New", 11, "bold"), text_color=ACCENT_BLUE
                     ).pack(anchor="w", padx=30)

        nav_grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        nav_grid.pack(fill="x", padx=30, pady=8)

        nav_links = [
            ("Sales",       "Dashboard → Sales",       ACCENT_BLUE),
            ("Merchandise", "Dashboard → Merchandise", ACCENT_PURPLE),
        ]

        for i, (label, desc, color) in enumerate(nav_links):
            card = ctk.CTkFrame(nav_grid, fg_color=PANEL_COLOR, corner_radius=8,
                                 border_width=1, border_color=BORDER_COLOR,
                                 height=64, cursor="hand2")
            card.grid(row=0, column=i, padx=8, pady=6, sticky="ew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=f"  {label}  →", font=("Courier New", 13, "bold"),
                         text_color=color).place(x=12, y=10)
            ctk.CTkLabel(card, text=f"  TRANSITION: {desc}",
                         font=FONT_SMALL, text_color=TEXT_MUTED).place(x=12, y=36)
            card.bind("<Button-1>", lambda e, l=label: self._navigate(l))

        nav_grid.columnconfigure(0, weight=1)
        nav_grid.columnconfigure(1, weight=1)

        # Access denied notice
        ctk.CTkFrame(self.content_area, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=30, pady=(20, 12))
        ctk.CTkLabel(
            self.content_area,
            text="🔒  Expenses and Employees sections require manager access.",
            font=FONT_SMALL, text_color=TEXT_MUTED
        ).pack(anchor="w", padx=30)

    def _show_placeholder(self):
        ctk.CTkLabel(
            self.content_area,
            text=f"{self.active_section.upper()} SCREEN\n\nComing in future activities.",
            font=FONT_TITLE, text_color=TEXT_MUTED, justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

    def _logout(self):
        current_session.logout()
        self.on_logout()
