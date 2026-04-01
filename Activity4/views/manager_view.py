"""
manager_view.py - Dashboard view for manager-role users.
Shows full navigation: Dashboard, Sales, Expenses, Merchandise, Employees.
"""

import customtkinter as ctk
import sys, os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.session import current_session

# ── Theme constants ───────────────────────────────────────────────────────────
BG_COLOR      = "#0d1117"
PANEL_COLOR   = "#161b22"
SIDEBAR_COLOR = "#0d1117"
BORDER_COLOR  = "#30363d"
ACCENT_BLUE   = "#1f6feb"
ACCENT_GREEN  = "#3fb950"
ACCENT_RED    = "#f85149"
ACCENT_ORANGE = "#e3b341"
ACCENT_PURPLE = "#bc8cff"
TEXT_PRIMARY  = "#e6edf3"
TEXT_MUTED    = "#8b949e"
FONT_MONO     = ("Courier New", 12)
FONT_TITLE    = ("Courier New", 18, "bold")
FONT_LABEL    = ("Courier New", 11)
FONT_SMALL    = ("Courier New", 10)

# Sidebar navigation items: (label, accent_color)
NAV_ITEMS = [
    ("Dashboard",    ACCENT_BLUE),
    ("Sales",        TEXT_PRIMARY),
    ("Expenses",     TEXT_PRIMARY),
    ("Merchandise",  TEXT_PRIMARY),
    ("Employees",    TEXT_PRIMARY),
]


class ManagerView(ctk.CTkFrame):
    """
    Full-access dashboard for manager users.
    Includes sidebar navigation and a content area.
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
        sidebar = ctk.CTkFrame(self, fg_color=SIDEBAR_COLOR, width=240,
                                border_width=1, border_color=BORDER_COLOR,
                                corner_radius=0)
        sidebar.pack(side="left", fill="y")
        sidebar.pack_propagate(False)

        # App title
        ctk.CTkLabel(sidebar, text="STORE MANAGER", font=("Courier New", 14, "bold"),
                     text_color=ACCENT_BLUE).pack(padx=20, pady=(20, 2), anchor="w")
        ctk.CTkLabel(sidebar, text="v1.0  ·  Manager", font=FONT_SMALL,
                     text_color=TEXT_MUTED).pack(padx=20, anchor="w")
        ctk.CTkFrame(sidebar, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=20, pady=(12, 8))

        # Navigation buttons
        self.nav_buttons = {}
        for label, color in NAV_ITEMS:
            btn = ctk.CTkButton(
                sidebar, text=f"  {label}",
                font=FONT_MONO, anchor="w",
                fg_color=ACCENT_BLUE if label == "Dashboard" else "transparent",
                hover_color="#21262d",
                text_color=color if label != "Dashboard" else "white",
                height=42, corner_radius=6,
                command=lambda l=label: self._navigate(l)
            )
            btn.pack(fill="x", padx=12, pady=2)
            self.nav_buttons[label] = btn

        # Logout + status at bottom
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(expand=True)
        ctk.CTkButton(sidebar, text="  Logout", font=FONT_MONO, anchor="w",
                      fg_color="transparent", hover_color="#21262d",
                      text_color=ACCENT_RED, height=38,
                      command=self._logout).pack(fill="x", padx=12, pady=4)
        ctk.CTkLabel(sidebar, text="System Status: ONLINE\nDB Connection: ✓",
                     font=FONT_SMALL, text_color=TEXT_MUTED,
                     justify="left").pack(padx=20, pady=(4, 16), anchor="w")

        # ── Main content area ─────────────────────────────────────────────────
        self.content_area = ctk.CTkFrame(self, fg_color=BG_COLOR, corner_radius=0)
        self.content_area.pack(side="left", fill="both", expand=True)

        self._show_dashboard()

    # ── Navigation ────────────────────────────────────────────────────────────

    def _navigate(self, section: str):
        """Switch the active section and update sidebar highlight."""
        self.active_section = section

        # Update sidebar button styles
        for label, btn in self.nav_buttons.items():
            if label == section:
                btn.configure(fg_color=ACCENT_BLUE, text_color="white")
            else:
                btn.configure(fg_color="transparent", text_color=TEXT_PRIMARY)

        # Clear content area and load section
        for widget in self.content_area.winfo_children():
            widget.destroy()

        section_map = {
            "Dashboard":   self._show_dashboard,
            "Sales":       self._show_placeholder,
            "Expenses":    self._show_placeholder,
            "Merchandise": self._show_placeholder,
            "Employees":   self._show_placeholder,
        }
        section_map.get(section, self._show_dashboard)()

    def _show_dashboard(self):
        """Render the dashboard home screen with summary widgets."""
        # Header
        header = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(24, 0))

        ctk.CTkLabel(header, text="DASHBOARD / HOME SCREEN",
                     font=FONT_TITLE, text_color=TEXT_PRIMARY).pack(anchor="w")
        ctk.CTkLabel(header, text="Main Navigation & Summary Widgets",
                     font=FONT_SMALL, text_color=TEXT_MUTED).pack(anchor="w")
        ctk.CTkFrame(self.content_area, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=30, pady=(10, 20))

        # Summary widgets grid
        ctk.CTkLabel(self.content_area, text="QUICK SUMMARY WIDGETS",
                     font=("Courier New", 11, "bold"), text_color=ACCENT_BLUE
                     ).pack(anchor="w", padx=30)

        grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=(8, 0))

        widgets = [
            ("Total Sales",        "$0.00",  ACCENT_BLUE),
            ("Total Profit",       "$0.00",  ACCENT_GREEN),
            ("Total Expenses",     "$0.00",  ACCENT_RED),
            ("Number of Employees","0",      ACCENT_PURPLE),
        ]

        for i, (title, value, color) in enumerate(widgets):
            card = ctk.CTkFrame(grid, fg_color=PANEL_COLOR, corner_radius=8,
                                 border_width=1, border_color=BORDER_COLOR,
                                 width=240, height=110)
            card.grid(row=i//2, column=i%2, padx=8, pady=8, sticky="nsew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text="WIDGET", font=FONT_SMALL,
                         text_color=TEXT_MUTED).place(relx=1.0, x=-12, y=12, anchor="ne")
            ctk.CTkLabel(card, text=title, font=FONT_LABEL,
                         text_color=TEXT_MUTED).place(x=16, y=40)
            ctk.CTkLabel(card, text=value, font=("Courier New", 22, "bold"),
                         text_color=color).place(x=16, y=62)

        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # Navigation links
        ctk.CTkFrame(self.content_area, fg_color=BORDER_COLOR, height=1).pack(
            fill="x", padx=30, pady=(20, 12))
        ctk.CTkLabel(self.content_area, text="NAVIGATION LINKS",
                     font=("Courier New", 11, "bold"), text_color=ACCENT_BLUE
                     ).pack(anchor="w", padx=30)

        nav_grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        nav_grid.pack(fill="x", padx=30, pady=8)

        nav_links = [
            ("Sales",       "Dashboard → Sales",       ACCENT_BLUE),
            ("Merchandise", "Dashboard → Merchandise", ACCENT_PURPLE),
            ("Employees",   "Dashboard → Employees",   ACCENT_GREEN),
            ("Expenses",    "Dashboard → Expenses",    ACCENT_RED),
        ]

        for i, (label, desc, color) in enumerate(nav_links):
            card = ctk.CTkFrame(nav_grid, fg_color=PANEL_COLOR, corner_radius=8,
                                 border_width=1, border_color=BORDER_COLOR,
                                 height=64, cursor="hand2")
            card.grid(row=i//2, column=i%2, padx=8, pady=6, sticky="ew")
            card.grid_propagate(False)
            ctk.CTkLabel(card, text=f"  {label}  →", font=("Courier New", 13, "bold"),
                         text_color=color).place(x=12, y=10)
            ctk.CTkLabel(card, text=f"  TRANSITION: {desc}",
                         font=FONT_SMALL, text_color=TEXT_MUTED).place(x=12, y=36)
            card.bind("<Button-1>", lambda e, l=label: self._navigate(l))

        nav_grid.columnconfigure(0, weight=1)
        nav_grid.columnconfigure(1, weight=1)

    def _show_placeholder(self):
        """Placeholder for sections not yet implemented in this activity."""
        ctk.CTkLabel(
            self.content_area,
            text=f"{self.active_section.upper()} SCREEN\n\nComing in future activities.",
            font=FONT_TITLE, text_color=TEXT_MUTED, justify="center"
        ).place(relx=0.5, rely=0.5, anchor="center")

    # ── Logout ────────────────────────────────────────────────────────────────

    def _logout(self):
        """Log out the current session and trigger the logout callback."""
        current_session.logout()
        self.on_logout()
