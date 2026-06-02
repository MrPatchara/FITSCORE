"""
AthletePage — Main athlete management page widget.
Displays athlete list with search, filter, CRUD actions, and group management.
All UI text is in Thai.
"""
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QTableWidget, QTableWidgetItem, QHeaderView, QCheckBox,
    QAbstractItemView, QMessageBox, QFrame, QSizePolicy,
    QDialog,
)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QFont, QIcon

from app.services.athlete_service import AthleteService
from app.views.athlete_dialogs import (
    AthleteFormDialog, GroupManagerDialog, MoveToGroupDialog,
    CustomConfirmDialog,
)

import os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
arrow_path = os.path.normpath(os.path.join(CURRENT_DIR, "..", "resources", "arrow_down.png")).replace("\\", "/")
checkmark_path = os.path.normpath(os.path.join(CURRENT_DIR, "..", "resources", "checkmark.svg")).replace("\\", "/")

# ─── Design System (mirrors main_window constants) ────────────────────────────
COL_BG_PRIMARY   = "#f1f5f9"
COL_BG_WHITE     = "#ffffff"
COL_TEXT_PRIMARY  = "#0f172a"
COL_TEXT_BODY     = "#334155"
COL_TEXT_MUTED    = "#64748b"
COL_TEXT_LIGHT    = "#94a3b8"
COL_ACCENT_BLUE  = "#2563eb"
COL_ACCENT_NAVY  = "#1e3a8a"
COL_BORDER       = "#e2e8f0"
COL_GREEN        = "#059669"
COL_GREEN_BG     = "#ecfdf5"
COL_RED          = "#dc2626"
COL_RED_BG       = "#fef2f2"
COL_BLUE_BG      = "#eff6ff"
COL_ORANGE       = "#d97706"
COL_ORANGE_BG    = "#fffbeb"
COL_PURPLE       = "#7c3aed"
COL_PURPLE_BG    = "#f5f3ff"


class AthletePage(QWidget):
    """Full-featured athlete management page."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.service = AthleteService()
        self._search_timer = QTimer()
        self._search_timer.setSingleShot(True)
        self._search_timer.setInterval(300)
        self._search_timer.timeout.connect(self._reload_table)

        self._build_ui()
        self._reload_table()

    # ═══════════════════════════════════════════════════════════════════════════
    # BUILD UI
    # ═══════════════════════════════════════════════════════════════════════════

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 16, 24, 8)  # Tighten margins
        layout.setSpacing(10)  # Tighten gap spacing between widgets to expand the table area

        # ── Header ──
        self._build_header(layout)

        # ── Stats cards row ──
        self._build_stat_cards(layout)

        # ── Toolbar + Filter bar ──
        self._build_toolbar(layout)

        # ── Table ──
        self._build_table(layout)

        # ── Footer status ──
        self._build_footer(layout)

    # ── Header ────────────────────────────────────────────────────────────────
    def _build_header(self, parent_layout):
        hdr = QLabel("ข้อมูลผู้ทดสอบ")
        hdr.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        parent_layout.addWidget(hdr)

        sub = QLabel("จัดการประวัติผู้ทดสอบ ข้อมูลทั่วไป กลุ่มสังกัด เพิ่ม แก้ไข ลบ และจัดกลุ่มผู้ทดสอบ")
        sub.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED}; margin-top: -4px;")
        parent_layout.addWidget(sub)

    # ── Stat Cards ────────────────────────────────────────────────────────────
    def _build_stat_cards(self, parent_layout):
        self.stats_row = QHBoxLayout()
        self.stats_row.setSpacing(12)
        self.stats_row.setContentsMargins(2, 2, 2, 10)  # Prevent shadow clipping
        parent_layout.addLayout(self.stats_row)
        # Actual stat widgets built in _update_stat_cards
        self._stat_widgets = []

    def _update_stat_cards(self):
        # Remove old widgets
        for w in self._stat_widgets:
            self.stats_row.removeWidget(w)
            w.deleteLater()
        self._stat_widgets.clear()

        all_athletes = self.service.get_all_athletes()
        total = len(all_athletes)
        males = sum(1 for a in all_athletes if a.gender == "Male")
        females = sum(1 for a in all_athletes if a.gender == "Female")
        groups = self.service.get_all_groups()
        no_group = sum(1 for a in all_athletes if a.group_id is None)

        stats = [
            ("ผู้ทดสอบทั้งหมด", str(total), "👤", COL_ACCENT_BLUE, COL_BLUE_BG),
            ("ชาย", str(males), "🚹", COL_ACCENT_NAVY, COL_BLUE_BG),
            ("หญิง", str(females), "🚺", COL_PURPLE, COL_PURPLE_BG),
            ("จำนวนกลุ่ม", str(len(groups)), "📁", COL_ORANGE, COL_ORANGE_BG),
            ("ไม่ระบุกลุ่ม", str(no_group), "📌", COL_RED, COL_RED_BG),
        ]

        for label, value, icon, accent, bg in stats:
            card = self._make_stat_card(label, value, icon, accent, bg)
            self.stats_row.addWidget(card)
            self._stat_widgets.append(card)

    def _make_stat_card(self, label, value, icon, accent, bg):
        from PySide6.QtWidgets import QGraphicsDropShadowEffect
        from PySide6.QtGui import QColor

        card = QFrame()
        card.setObjectName("StatCard")
        card.setStyleSheet(f"""
            QFrame#StatCard {{
                background-color: {COL_BG_WHITE};
                border: 1px solid {COL_BORDER};
                border-radius: 10px;
            }}
            QFrame#StatCard:hover {{
                background-color: #fafbfc;
                border: 1px solid {accent};
            }}
        """)
        card.setFixedHeight(54)

        # Apply premium drop shadow
        shadow = QGraphicsDropShadowEffect(card)
        shadow.setBlurRadius(8)
        shadow.setColor(QColor(0, 0, 0, 12))  # Ultra-subtle black shadow
        shadow.setOffset(0, 1)
        card.setGraphicsEffect(shadow)

        lay = QHBoxLayout(card)
        lay.setContentsMargins(10, 8, 12, 8)
        lay.setSpacing(8)

        # 1. Accent Indicator Strip (Vertical capsule)
        accent_bar = QFrame()
        accent_bar.setFixedWidth(3)
        accent_bar.setFixedHeight(22)
        accent_bar.setStyleSheet(f"""
            background-color: {accent};
            border-radius: 1.5px;
            border: none;
        """)
        lay.addWidget(accent_bar)

        # 2. Icon Label (Circular container)
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(30, 30)
        icon_lbl.setAlignment(Qt.AlignCenter)
        border_color = f"{accent}22"
        icon_lbl.setStyleSheet(f"""
            font-size: 14px;
            background-color: {bg};
            border-radius: 15px;
            border: 1px solid {border_color};
        """)
        lay.addWidget(icon_lbl)

        # 3. Combined Text + Value Label (Single line, smaller size)
        txt_lbl = QLabel()
        txt_lbl.setStyleSheet("background: transparent; border: none;")
        # Set number (value) followed by text/label
        txt_lbl.setText(f"<span style='font-size: 14px; font-weight: 700; color: {COL_TEXT_PRIMARY};'>{value}</span>&nbsp;&nbsp;<span style='font-size: 11px; color: {COL_TEXT_MUTED}; font-weight: 600;'>{label}</span>")
        lay.addWidget(txt_lbl)

        lay.addStretch()
        return card

    # ── Toolbar + Filter Bar ──────────────────────────────────────────────────
    def _build_toolbar(self, parent_layout):
        toolbar_card = QFrame()
        toolbar_card.setStyleSheet(f"""
            QFrame {{
                background-color: {COL_BG_WHITE};
                border: 1px solid {COL_BORDER};
                border-radius: 10px;
            }}
        """)
        
        # Use QHBoxLayout directly to place everything in a single row
        toolbar_lay = QHBoxLayout(toolbar_card)
        toolbar_lay.setContentsMargins(14, 8, 14, 8)
        toolbar_lay.setSpacing(10)

        # ── Left: Action Buttons ──
        btn_add = QPushButton("➕ เพิ่มผู้ทดสอบ")
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.setStyleSheet(f"""
            QPushButton {{
                background-color: {COL_ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: #1d4ed8; }}
        """)
        btn_add.clicked.connect(self._on_add_athlete)
        toolbar_lay.addWidget(btn_add)

        btn_groups = QPushButton("📁 จัดการกลุ่ม")
        btn_groups.setCursor(Qt.PointingHandCursor)
        btn_groups.setStyleSheet(f"""
            QPushButton {{
                background-color: {COL_ORANGE_BG};
                color: {COL_ORANGE};
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COL_ORANGE}; color: white; border-color: {COL_ORANGE}; }}
        """)
        btn_groups.clicked.connect(self._on_manage_groups)
        toolbar_lay.addWidget(btn_groups)

        self.btn_move_group = QPushButton("↔ ย้ายเข้ากลุ่ม")
        self.btn_move_group.setCursor(Qt.PointingHandCursor)
        self.btn_move_group.setEnabled(False)
        self.btn_move_group.setStyleSheet(f"""
            QPushButton {{
                background-color: {COL_PURPLE_BG};
                color: {COL_PURPLE};
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COL_PURPLE}; color: white; border-color: {COL_PURPLE}; }}
            QPushButton:disabled {{ background-color: {COL_BG_PRIMARY}; color: {COL_TEXT_LIGHT}; border-color: {COL_BORDER}; }}
        """)
        self.btn_move_group.clicked.connect(self._on_move_to_group)
        toolbar_lay.addWidget(self.btn_move_group)

        self.btn_delete_selected = QPushButton("🗑️")
        self.btn_delete_selected.setToolTip("ลบผู้ทดสอบที่เลือก")
        self.btn_delete_selected.setCursor(Qt.PointingHandCursor)
        self.btn_delete_selected.setEnabled(False)
        self.btn_delete_selected.setStyleSheet(f"""
            QPushButton {{
                background-color: {COL_RED_BG};
                color: {COL_RED};
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 7px 14px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{ background-color: {COL_RED}; color: white; border-color: {COL_RED}; }}
            QPushButton:disabled {{ background-color: {COL_BG_PRIMARY}; color: {COL_TEXT_LIGHT}; border-color: {COL_BORDER}; }}
        """)
        self.btn_delete_selected.clicked.connect(self._on_delete_selected)
        toolbar_lay.addWidget(self.btn_delete_selected)

        # Stretch spacing to separate buttons from filters
        toolbar_lay.addStretch()

        # ── Right: Filter Controls ──
        # Search Box
        self.txt_search = QLineEdit()
        self.txt_search.setPlaceholderText("🔍 ค้นหา")
        self.txt_search.setMinimumWidth(180)
        self.txt_search.setMaximumWidth(240)
        self.txt_search.setStyleSheet(f"""
            QLineEdit {{
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 7px 10px;
                font-size: 13px;
                background-color: {COL_BG_PRIMARY};
                color: {COL_TEXT_PRIMARY};
            }}
            QLineEdit:hover {{
                border-color: {COL_TEXT_MUTED};
            }}
            QLineEdit:focus {{
                border-color: {COL_ACCENT_BLUE};
                background-color: {COL_BG_WHITE};
            }}
        """)
        self.txt_search.textChanged.connect(self._on_search_changed)
        toolbar_lay.addWidget(self.txt_search)

        # Gender Filter
        lbl_gender = QLabel("เพศ:")
        lbl_gender.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED}; font-weight: 600; border: none;")
        toolbar_lay.addWidget(lbl_gender)

        self.cb_filter_gender = QComboBox()
        self.cb_filter_gender.addItems(["ทั้งหมด", "ชาย", "หญิง", "อื่นๆ"])
        self.cb_filter_gender.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 6px 20px 6px 8px;
                font-size: 13px;
                background-color: {COL_BG_PRIMARY};
                min-width: 65px;
                max-width: 80px;
                color: {COL_TEXT_PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {COL_ACCENT_BLUE};
                background-color: {COL_BG_WHITE};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 18px;
                border-left: 1px solid {COL_BORDER};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: #f8fafc;
            }}
            QComboBox::drop-down:hover {{
                background-color: #f1f5f9;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_path});
                width: 8px;
                height: 8px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {COL_BORDER};
                selection-background-color: {COL_ACCENT_BLUE};
                selection-color: white;
                background-color: {COL_BG_WHITE};
            }}
        """)
        self.cb_filter_gender.currentIndexChanged.connect(self._reload_table)
        toolbar_lay.addWidget(self.cb_filter_gender)

        # Group Filter
        lbl_group = QLabel("กลุ่ม:")
        lbl_group.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED}; font-weight: 600; border: none;")
        toolbar_lay.addWidget(lbl_group)

        self.cb_filter_group = QComboBox()
        self._load_group_filter()
        self.cb_filter_group.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 6px 26px 6px 10px;
                font-size: 13px;
                background-color: {COL_BG_PRIMARY};
                min-width: 120px;
                max-width: 180px;
                color: {COL_TEXT_PRIMARY};
            }}
            QComboBox:focus {{
                border-color: {COL_ACCENT_BLUE};
                background-color: {COL_BG_WHITE};
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left: 1px solid {COL_BORDER};
                border-top-right-radius: 6px;
                border-bottom-right-radius: 6px;
                background-color: #f8fafc;
            }}
            QComboBox::drop-down:hover {{
                background-color: #f1f5f9;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_path});
                width: 9px;
                height: 9px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {COL_BORDER};
                selection-background-color: {COL_ACCENT_BLUE};
                selection-color: white;
                background-color: {COL_BG_WHITE};
            }}
        """)
        self.cb_filter_group.currentIndexChanged.connect(self._reload_table)
        toolbar_lay.addWidget(self.cb_filter_group)

        parent_layout.addWidget(toolbar_card)

    # ── Table ─────────────────────────────────────────────────────────────────
    def _build_table(self, parent_layout):
        self.table = QTableWidget()
        self.table.setColumnCount(9)
        self.table.setHorizontalHeaderLabels([
            "☐", "ลำดับ", "ชื่อ-สกุล", "เพศ", "วันเกิด", "อายุ", "กลุ่ม", "หมายเหตุ", "ดำเนินการ"
        ])

        # Column sizing
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.Fixed)       # Checkbox
        header.setSectionResizeMode(1, QHeaderView.Fixed)       # #
        header.setSectionResizeMode(2, QHeaderView.Stretch)     # Name
        header.setSectionResizeMode(3, QHeaderView.Fixed)       # Gender
        header.setSectionResizeMode(4, QHeaderView.Fixed)       # DOB
        header.setSectionResizeMode(5, QHeaderView.Fixed)       # Age
        header.setSectionResizeMode(6, QHeaderView.Stretch)     # Group
        header.setSectionResizeMode(7, QHeaderView.Stretch)     # Notes
        header.setSectionResizeMode(8, QHeaderView.Fixed)       # Actions
        self.table.setColumnWidth(0, 36)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 100)
        self.table.setColumnWidth(5, 55)
        self.table.setColumnWidth(8, 180)

        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setIconSize(QSize(28, 28))
        self.table.setStyleSheet(f"""
            QTableWidget {{
                background-color: {COL_BG_WHITE};
                alternate-background-color: {COL_BG_PRIMARY};
                border: 1px solid {COL_BORDER};
                border-radius: 8px;
                gridline-color: {COL_BORDER};
                font-size: 13px;
                selection-background-color: {COL_BLUE_BG};
                selection-color: {COL_ACCENT_BLUE};
            }}
            QHeaderView::section {{
                background-color: {COL_BG_PRIMARY};
                color: {COL_TEXT_MUTED};
                font-weight: 600;
                font-size: 12px;
                padding: 8px 6px;
                border: none;
                border-bottom: 2px solid {COL_BORDER};
            }}
            QTableWidget::item {{
                padding: 4px 6px;
                border-bottom: 1px solid {COL_BORDER};
            }}
            QTableWidget::item:hover {{
                background-color: #f8fafc;
            }}
            QTableWidget::item:selected {{
                background-color: #e0f2fe;
                color: #0369a1;
                font-weight: 500;
            }}
            QCheckBox {{
                background: transparent;
                border: none;
            }}
            QCheckBox::indicator {{
                width: 15px;
                height: 15px;
                border: 1.5px solid #0f172a; /* Solid dark black-slate border, clearly visible */
                border-radius: 4px;
                background-color: white;
            }}
            QCheckBox::indicator:hover {{
                border-color: {COL_ACCENT_BLUE};
            }}
            QCheckBox::indicator:checked {{
                border-color: {COL_ACCENT_BLUE};
                background-color: {COL_ACCENT_BLUE};
                image: url({checkmark_path});
            }}
            QCheckBox::indicator:disabled {{
                border-color: #cbd5e1;
                background-color: #f1f5f9;
            }}
        """)

        self.table.horizontalHeader().sectionClicked.connect(self._on_header_clicked)
        parent_layout.addWidget(self.table, 1)

    # ── Footer ────────────────────────────────────────────────────────────────
    def _build_footer(self, parent_layout):
        self.lbl_status = QLabel("")
        self.lbl_status.setStyleSheet(f"""
            font-size: 12px;
            color: {COL_TEXT_MUTED};
            padding: 2px 0;
        """)
        parent_layout.addWidget(self.lbl_status)

    # ═══════════════════════════════════════════════════════════════════════════
    # DATA LOADING
    # ═══════════════════════════════════════════════════════════════════════════

    def _load_group_filter(self):
        self.cb_filter_group.blockSignals(True)
        current_data = self.cb_filter_group.currentData()
        self.cb_filter_group.clear()
        self.cb_filter_group.addItem("ทั้งหมด", None)
        self.cb_filter_group.addItem("— ไม่ระบุกลุ่ม —", -1)
        for g in self.service.get_all_groups():
            self.cb_filter_group.addItem(g.name, g.id)
        # Restore selection
        if current_data is not None:
            idx = self.cb_filter_group.findData(current_data)
            if idx >= 0:
                self.cb_filter_group.setCurrentIndex(idx)
        self.cb_filter_group.blockSignals(False)

    def _reload_table(self):
        # Reset header checkbox text
        if self.table.horizontalHeaderItem(0):
            self.table.horizontalHeaderItem(0).setText("☐")

        # Determine filters
        search = self.txt_search.text().strip()
        gender_map = {"ทั้งหมด": "", "ชาย": "Male", "หญิง": "Female", "อื่นๆ": "Other"}
        gender = gender_map.get(self.cb_filter_gender.currentText(), "")
        group_data = self.cb_filter_group.currentData()

        athletes = self.service.get_all_athletes(
            search=search,
            gender_filter=gender,
            group_filter=group_data,
        )

        self.table.setRowCount(len(athletes))
        self._checkboxes = []

        gender_display = {"Male": "ชาย", "Female": "หญิง", "Other": "อื่นๆ"}

        for row, ath in enumerate(athletes):
            # Checkbox
            cb_widget = QWidget()
            cb_widget.setStyleSheet("background-color: transparent; border: none;")
            cb_layout = QHBoxLayout(cb_widget)
            cb_layout.setContentsMargins(0, 0, 0, 0)
            cb_layout.setAlignment(Qt.AlignCenter)
            cb = QCheckBox()
            cb.setProperty("athlete_id", ath.id)
            cb.stateChanged.connect(self._on_checkbox_changed)
            cb_layout.addWidget(cb)
            self.table.setCellWidget(row, 0, cb_widget)
            self._checkboxes.append(cb)

            # Row number
            num_item = QTableWidgetItem(str(row + 1))
            num_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 1, num_item)

            # Full name with profile photo thumbnail
            name_item = QTableWidgetItem(ath.full_name)
            if ath.photo_path:
                import os
                abs_path = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ath.photo_path))
                if os.path.exists(abs_path):
                    name_item.setIcon(QIcon(abs_path))
            self.table.setItem(row, 2, name_item)

            # Gender
            g_item = QTableWidgetItem(gender_display.get(ath.gender, ath.gender))
            g_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 3, g_item)

            # DOB (พ.ศ.)
            dob_str = ath.dob_buddhist_era
            self.table.setItem(row, 4, QTableWidgetItem(dob_str))

            # Age
            age_item = QTableWidgetItem(str(ath.age))
            age_item.setTextAlignment(Qt.AlignCenter)
            self.table.setItem(row, 5, age_item)

            # Group
            group_name = ath.group.name if ath.group else "—"
            group_item = QTableWidgetItem(group_name)
            if not ath.group:
                group_item.setForeground(Qt.gray)
            self.table.setItem(row, 6, group_item)

            # Notes
            self.table.setItem(row, 7, QTableWidgetItem(ath.notes or "—"))

            # Action buttons
            action_widget = QWidget()
            action_layout = QHBoxLayout(action_widget)
            action_layout.setContentsMargins(4, 2, 4, 2)
            action_layout.setSpacing(6)

            btn_edit = QPushButton("✏️ แก้ไข")
            btn_edit.setCursor(Qt.PointingHandCursor)
            btn_edit.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COL_BLUE_BG};
                    color: {COL_ACCENT_BLUE};
                    border: 1px solid #bae6fd;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COL_ACCENT_BLUE};
                    color: white;
                    border-color: {COL_ACCENT_BLUE};
                }}
            """)
            btn_edit.clicked.connect(lambda _=False, aid=ath.id: self._on_edit_athlete(aid))
            action_layout.addWidget(btn_edit)

            btn_del = QPushButton("🗑️ ลบ")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COL_RED_BG};
                    color: {COL_RED};
                    border: 1px solid #fecaca;
                    border-radius: 6px;
                    padding: 5px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
                QPushButton:hover {{
                    background-color: {COL_RED};
                    color: white;
                    border-color: {COL_RED};
                }}
            """)
            btn_del.clicked.connect(lambda _=False, aid=ath.id: self._on_delete_athlete(aid))
            action_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 8, action_widget)
            self.table.setRowHeight(row, 44)

        self._update_stat_cards()
        self.lbl_status.setText(f"แสดง {len(athletes)} รายการ")
        self._update_bulk_buttons()

    # ═══════════════════════════════════════════════════════════════════════════
    # EVENT HANDLERS
    # ═══════════════════════════════════════════════════════════════════════════

    def _on_search_changed(self, text):
        self._search_timer.start()

    def _on_checkbox_changed(self):
        self._update_bulk_buttons()
        # Update header checkmark icon text dynamically
        if hasattr(self, "_checkboxes") and self._checkboxes:
            all_checked = all(cb.isChecked() for cb in self._checkboxes)
            self.table.horizontalHeaderItem(0).setText("☑" if all_checked else "☐")

    def _get_selected_ids(self) -> list[int]:
        selected = []
        for cb in self._checkboxes:
            if cb.isChecked():
                aid = cb.property("athlete_id")
                if aid is not None:
                    selected.append(aid)
        return selected

    def _update_bulk_buttons(self):
        count = len(self._get_selected_ids())
        enabled = count > 0
        self.btn_move_group.setEnabled(enabled)
        self.btn_delete_selected.setEnabled(enabled)
        if count > 0:
            self.btn_move_group.setText(f"↔ ย้ายเข้ากลุ่ม ({count})")
            self.btn_delete_selected.setText(f"🗑️ ({count})")
        else:
            self.btn_move_group.setText("↔ ย้ายเข้ากลุ่ม")
            self.btn_delete_selected.setText("🗑️")

    def _on_header_clicked(self, logical_index):
        if logical_index == 0:
            if not hasattr(self, "_checkboxes") or not self._checkboxes:
                return
            any_unchecked = any(not cb.isChecked() for cb in self._checkboxes)
            for cb in self._checkboxes:
                cb.setChecked(any_unchecked)
            # Update header checkmark icon text
            self.table.horizontalHeaderItem(0).setText("☑" if any_unchecked else "☐")

    # ── Add ───────────────────────────────────────────────────────────────────
    def _on_add_athlete(self):
        dlg = AthleteFormDialog(self, service=self.service)
        if dlg.exec():
            self._reload_table()

    # ── Edit ──────────────────────────────────────────────────────────────────
    def _on_edit_athlete(self, athlete_id):
        athlete = self.service.get_athlete_by_id(athlete_id)
        if not athlete:
            QMessageBox.warning(self, "ข้อผิดพลาด", "ไม่พบข้อมูลผู้ทดสอบ")
            return
        dlg = AthleteFormDialog(self, athlete=athlete, service=self.service)
        if dlg.exec():
            self._reload_table()

    # ── Delete single ─────────────────────────────────────────────────────────
    def _on_delete_athlete(self, athlete_id):
        athlete = self.service.get_athlete_by_id(athlete_id)
        if not athlete:
            return
        msg = f"ต้องการลบผู้ทดสอบ \"{athlete.full_name}\" หรือไม่?\n\nข้อมูลการทดสอบทั้งหมดของผู้ทดสอบคนนี้จะถูกลบไปด้วย"
        dlg = CustomConfirmDialog(self, title="ยืนยันการลบผู้ทดสอบ", message=msg, yes_text="ลบข้อมูล", no_text="ยกเลิก", is_danger=True)
        if dlg.exec() == QDialog.Accepted:
            self.service.delete_athlete(athlete_id)
            self._reload_table()

    # ── Delete selected ───────────────────────────────────────────────────────
    def _on_delete_selected(self):
        ids = self._get_selected_ids()
        if not ids:
            return
        msg = f"ต้องการลบผู้ทดสอบ {len(ids)} คนที่เลือกหรือไม่?\n\nข้อมูลการทดสอบทั้งหมดของผู้ทดสอบเหล่านี้จะถูกลบไปด้วย"
        dlg = CustomConfirmDialog(self, title="ยืนยันการลบผู้ทดสอบ", message=msg, yes_text="ลบข้อมูล", no_text="ยกเลิก", is_danger=True)
        if dlg.exec() == QDialog.Accepted:
            for aid in ids:
                self.service.delete_athlete(aid)
            self._reload_table()

    # ── Manage groups ─────────────────────────────────────────────────────────
    def _on_manage_groups(self):
        dlg = GroupManagerDialog(self, service=self.service)
        dlg.groups_changed.connect(self._on_groups_changed)
        dlg.exec()

    def _on_groups_changed(self):
        self._load_group_filter()
        self._reload_table()

    # ── Move to group ─────────────────────────────────────────────────────────
    def _on_move_to_group(self):
        ids = self._get_selected_ids()
        if not ids:
            return
        dlg = MoveToGroupDialog(self, selected_count=len(ids), service=self.service)
        if dlg.exec():
            group_id = dlg.selected_group_id()
            moved = self.service.move_athletes_to_group(ids, group_id)
            self._reload_table()
            QMessageBox.information(
                self, "สำเร็จ", f"ย้ายผู้ทดสอบ {moved} คนเรียบร้อยแล้ว"
            )
