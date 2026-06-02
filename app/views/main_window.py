"""
FITSCORE Main Window
Professional fitness assessment management interface.
Designed for government agencies, universities, and sports organizations.
"""
import os
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QGridLayout,
    QPushButton, QLabel, QStackedWidget, QFrame, QSizePolicy,
    QMenuBar, QMenu, QStatusBar, QMessageBox, QToolBar,
    QSpacerItem, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QComboBox
)
from PySide6.QtCore import Qt, QSize, QTimer
from PySide6.QtGui import QAction, QKeySequence, QFont, QColor, QPalette, QPixmap

from app.config import APP_NAME, VERSION, DATABASE_URL
from app.views.athlete_page import AthletePage
from app.core.db import db_session
from app.models.athlete import Athlete, Group
from app.models.test_type import TestType
from app.models.record import TestRecord
from app.models.standard import Standard

# ─── Design System Constants ───────────────────────────────────────────────────
# Color Palette - Professional Light Theme
COL_BG_PRIMARY   = "#f1f5f9"   # Slate 100 - Main canvas
COL_BG_WHITE     = "#ffffff"   # Pure white - Cards & panels
COL_BG_SIDEBAR   = "#1e293b"   # Slate 800 - Dark sidebar for contrast
COL_BG_HOVER     = "#334155"   # Slate 700 - Sidebar hover
COL_BG_ACTIVE    = "#2563eb"   # Blue 600 - Active nav item

COL_TEXT_PRIMARY  = "#0f172a"   # Slate 900 - Headings
COL_TEXT_BODY     = "#334155"   # Slate 700 - Body text
COL_TEXT_MUTED    = "#64748b"   # Slate 500 - Descriptions
COL_TEXT_LIGHT    = "#94a3b8"   # Slate 400 - Hints on dark bg
COL_TEXT_WHITE    = "#f8fafc"   # Slate 50 - Text on dark bg

COL_ACCENT_BLUE  = "#2563eb"   # Blue 600
COL_ACCENT_NAVY  = "#1e3a8a"   # Blue 900
COL_BORDER       = "#e2e8f0"   # Slate 200
COL_BORDER_DARK  = "#475569"   # Slate 600

COL_GREEN        = "#059669"   # Emerald 600
COL_GREEN_BG     = "#ecfdf5"   # Emerald 50
COL_ORANGE       = "#d97706"   # Amber 600
COL_ORANGE_BG    = "#fffbeb"   # Amber 50
COL_RED          = "#dc2626"   # Red 600
COL_PURPLE       = "#7c3aed"   # Violet 600
COL_PURPLE_BG    = "#f5f3ff"   # Violet 50
COL_BLUE_BG      = "#eff6ff"   # Blue 50


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(f"{APP_NAME}  —  Fitness Assessment Management System")
        self.resize(1280, 800)
        self.setMinimumSize(1024, 680)

        self._apply_global_style()
        self._init_menu_bar()

        # ── Central structure ──
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.root_layout = QHBoxLayout(self.central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)

        self._build_sidebar()

        # Right pane: top bar + stacked content
        right_pane = QWidget()
        right_layout = QVBoxLayout(right_pane)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setSpacing(0)

        self._build_top_bar(right_layout)
        self._build_content_stack(right_layout)

        self.root_layout.addWidget(right_pane, 1)

        # ── Status bar ──
        self._init_status_bar()

        # Default view
        self._switch_page(0)

    # ═══════════════════════════════════════════════════════════════════════════
    # GLOBAL STYLESHEET
    # ═══════════════════════════════════════════════════════════════════════════
    def _apply_global_style(self):
        self.setStyleSheet(f"""
            QMainWindow {{
                background-color: {COL_BG_PRIMARY};
            }}
            QWidget {{
                font-family: 'Segoe UI', 'Noto Sans Thai', 'Tahoma', sans-serif;
                font-size: 13px;
                color: {COL_TEXT_PRIMARY};
            }}

            /* ── Menu Bar ─────────────────── */
            QMenuBar {{
                background-color: {COL_BG_WHITE};
                color: {COL_TEXT_BODY};
                border-bottom: 1px solid {COL_BORDER};
                padding: 2px 0px;
                font-size: 13px;
            }}
            QMenuBar::item {{
                padding: 6px 14px;
                background: transparent;
                border-radius: 4px;
                margin: 2px;
            }}
            QMenuBar::item:selected {{
                background-color: {COL_BG_PRIMARY};
                color: {COL_TEXT_PRIMARY};
            }}
            QMenu {{
                background-color: {COL_BG_WHITE};
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 4px 0px;
                color: {COL_TEXT_PRIMARY};
            }}
            QMenu::item {{
                padding: 8px 28px 8px 16px;
                font-size: 13px;
            }}
            QMenu::item:selected {{
                background-color: {COL_BLUE_BG};
                color: {COL_ACCENT_BLUE};
            }}
            QMenu::separator {{
                height: 1px;
                background: {COL_BORDER};
                margin: 4px 10px;
            }}

            /* ── Toolbar ──────────────────── */
            QToolBar {{
                background-color: {COL_BG_WHITE};
                border-bottom: 1px solid {COL_BORDER};
                spacing: 6px;
                padding: 4px 10px;
            }}
            QToolBar QToolButton {{
                border: 1px solid {COL_BORDER};
                border-radius: 5px;
                padding: 5px 12px;
                font-size: 12px;
                color: {COL_TEXT_BODY};
                background-color: {COL_BG_WHITE};
            }}
            QToolBar QToolButton:hover {{
                background-color: {COL_BG_PRIMARY};
                border-color: {COL_TEXT_MUTED};
            }}

            /* ── Tables ───────────────────── */
            QTableWidget {{
                background-color: {COL_BG_WHITE};
                alternate-background-color: {COL_BG_PRIMARY};
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
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
                text-transform: uppercase;
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid {COL_BORDER};
            }}
            QTableWidget::item {{
                padding: 6px 12px;
                border-bottom: 1px solid {COL_BORDER};
            }}

            /* ── Status Bar ───────────────── */
            QStatusBar {{
                background-color: {COL_BG_WHITE};
                border-top: 1px solid {COL_BORDER};
                color: {COL_TEXT_MUTED};
                font-size: 12px;
                padding: 3px 10px;
            }}
        """)

    # ═══════════════════════════════════════════════════════════════════════════
    # MENU BAR
    # ═══════════════════════════════════════════════════════════════════════════
    def _init_menu_bar(self):
        mb = self.menuBar()

        # ── File ──
        m_file = mb.addMenu("ไฟล์")
        self._add_action(m_file, "เพิ่มผู้ทดสอบใหม่…", "Ctrl+N",
                         lambda: self._switch_page(1))
        self._add_action(m_file, "บันทึกผลการทดสอบใหม่…", "Ctrl+R",
                         lambda: self._switch_page(2))
        m_file.addSeparator()
        self._add_action(m_file, "นำเข้าเกณฑ์มาตรฐาน…", None,
                         lambda: self._msg("นำเข้า", "เปิดไฟล์เกณฑ์มาตรฐาน CSV/JSON…"))
        self._add_action(m_file, "ส่งออกรายงาน…", "Ctrl+E",
                         lambda: self._switch_page(5))
        m_file.addSeparator()
        self._add_action(m_file, "ออกจากโปรแกรม", "Ctrl+Q", self.close)

        # ── Edit ──
        m_edit = mb.addMenu("แก้ไข")
        self._add_action(m_edit, "ตั้งค่า…", "Ctrl+,",
                         lambda: self._msg("ตั้งค่า", "หน้าจอตั้งค่าระบบ…"))

        # ── View ──
        m_view = mb.addMenu("มุมมอง")
        pages = ["แดชบอร์ด", "ข้อมูลผู้ทดสอบ", "บันทึกการทดสอบ",
                 "เกณฑ์อ้างอิง", "วิเคราะห์กลุ่ม", "รายงาน"]
        for i, name in enumerate(pages):
            self._add_action(m_view, name, None,
                             lambda _=False, idx=i: self._switch_page(idx))

        # ── Tools ──
        m_tools = mb.addMenu("เครื่องมือ")
        self._add_action(m_tools, "จัดการประเภทการทดสอบ…", None,
                         lambda: self._msg("ประเภทการทดสอบ", "หน้าจอจัดการประเภทการทดสอบ…"))
        self._add_action(m_tools, "รีเซ็ตข้อมูลเริ่มต้น…", None,
                         lambda: self._msg("ข้อมูลเริ่มต้น", "กำลังตั้งค่าฐานข้อมูลใหม่ด้วยข้อมูลเริ่มต้น…"))

        # ── Help ──
        m_help = mb.addMenu("ความช่วยเหลือ")
        self._add_action(m_help, "คู่มือการใช้งาน", "F1",
                         lambda: self._msg("ความช่วยเหลือ", "กำลังเปิดเอกสารคู่มือการใช้งาน…"))
        m_help.addSeparator()
        act_about = QAction("เกี่ยวกับ FITSCORE", self)
        act_about.triggered.connect(self._show_about)
        m_help.addAction(act_about)

    def _add_action(self, menu, text, shortcut, callback):
        act = QAction(text, self)
        if shortcut:
            act.setShortcut(QKeySequence(shortcut))
        act.triggered.connect(callback)
        menu.addAction(act)



    # ═══════════════════════════════════════════════════════════════════════════
    # SIDEBAR
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setFixedWidth(230)
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {COL_BG_SIDEBAR};
                border: none;
            }}
        """)
        lay = QVBoxLayout(self.sidebar)
        lay.setContentsMargins(0, 0, 0, 0)
        lay.setSpacing(0)

        # ── Brand Header with Logo ──
        brand_frame = QFrame()
        brand_frame.setFixedHeight(135)
        brand_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #ffffff;
                border: none;
                border-bottom: 3px solid #10b981;
            }}
        """)
        brand_lay = QVBoxLayout(brand_frame)
        brand_lay.setContentsMargins(0, 0, 0, 0)
        brand_lay.setAlignment(Qt.AlignCenter)

        # Logo image
        logo_label = QLabel()
        logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "logo.png")
        if os.path.exists(logo_path):
            logo_pixmap = QPixmap(logo_path)
            logo_label.setPixmap(logo_pixmap.scaled(210, 125, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setStyleSheet("background: transparent; border: none;")
        brand_lay.addWidget(logo_label)

        lay.addWidget(brand_frame)

        # ── Section Label Helper ──
        def section_label(text):
            lbl = QLabel(f"  {text}")
            lbl.setFixedHeight(34)
            lbl.setStyleSheet(f"""
                font-size: 10px;
                font-weight: 700;
                color: {COL_TEXT_LIGHT};
                letter-spacing: 1.5px;
                text-transform: uppercase;
                padding-left: 18px;
                padding-top: 16px;
                background: transparent;
                border: none;
            """)
            return lbl

        # ── Nav Buttons ──
        self.nav_buttons = []
        nav_items = [
            ("ภาพรวม",    [("◉  แดชบอร์ด",        0)]),
            ("ป้อนข้อมูล",  [("👤  ข้อมูลผู้ทดสอบ",         1),
                             ("📝  บันทึกการทดสอบ",       2)]),
            ("เกณฑ์มาตรฐาน",   [("📊  เกณฑ์อ้างอิง",  3)]),
            ("การวิเคราะห์",    [("📈  วิเคราะห์กลุ่ม",   4),
                             ("📄  รายงาน",          5)]),
        ]

        for section_title, buttons in nav_items:
            lay.addWidget(section_label(section_title))
            for label, page_idx in buttons:
                btn = QPushButton(label)
                btn.setCheckable(True)
                btn.setCursor(Qt.PointingHandCursor)
                btn.setFixedHeight(40)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: transparent;
                        color: {COL_TEXT_LIGHT};
                        text-align: left;
                        padding-left: 20px;
                        font-size: 13px;
                        font-weight: 500;
                        border: none;
                        border-radius: 0;
                        margin: 1px 10px;
                        border-radius: 6px;
                    }}
                    QPushButton:hover {{
                        background-color: {COL_BG_HOVER};
                        color: {COL_TEXT_WHITE};
                    }}
                    QPushButton:checked {{
                        background-color: rgba(37, 99, 235, 0.85);
                        color: {COL_TEXT_WHITE};
                        font-weight: 600;
                    }}
                """)
                btn.clicked.connect(lambda _=False, idx=page_idx: self._switch_page(idx))
                lay.addWidget(btn)
                self.nav_buttons.append((btn, page_idx))

        lay.addStretch()

        # ── Footer ──
        footer_frame = QFrame()
        footer_frame.setFixedHeight(50)
        footer_frame.setStyleSheet(f"""
            background-color: rgba(0,0,0,0.2);
            border: none;
            border-top: 1px solid {COL_BORDER_DARK};
        """)
        footer_lay = QVBoxLayout(footer_frame)
        footer_lay.setContentsMargins(15, 8, 15, 8)

        ver_lbl = QLabel(f"FITSCORE v{VERSION}  ·  SQLite")
        ver_lbl.setAlignment(Qt.AlignCenter)
        ver_lbl.setStyleSheet(f"font-size: 10px; color: {COL_TEXT_LIGHT}; border: none; background: transparent;")
        footer_lay.addWidget(ver_lbl)
        lay.addWidget(footer_frame)

        self.root_layout.addWidget(self.sidebar)

    # ═══════════════════════════════════════════════════════════════════════════
    # TOP BAR  (breadcrumbs + DB indicator)
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_top_bar(self, parent_layout):
        bar = QFrame()
        bar.setFixedHeight(48)
        bar.setStyleSheet(f"""
            QFrame {{
                background-color: {COL_BG_WHITE};
                border-bottom: 1px solid {COL_BORDER};
            }}
        """)
        h = QHBoxLayout(bar)
        h.setContentsMargins(16, 0, 24, 0)
        h.setSpacing(0)

        # ── Toggle Sidebar Button ──
        self.btn_toggle_sidebar = QPushButton("☰")
        self.btn_toggle_sidebar.setCursor(Qt.PointingHandCursor)
        self.btn_toggle_sidebar.setToolTip("ซ่อนเมนู")
        self.btn_toggle_sidebar.setFixedSize(32, 32)
        self.btn_toggle_sidebar.setStyleSheet(f"""
            QPushButton {{
                background-color: transparent;
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                font-size: 14px;
                color: {COL_TEXT_BODY};
            }}
            QPushButton:hover {{
                background-color: {COL_BG_PRIMARY};
                border-color: {COL_TEXT_MUTED};
            }}
        """)
        self.btn_toggle_sidebar.clicked.connect(self._toggle_sidebar)
        h.addWidget(self.btn_toggle_sidebar)
        
        h.addSpacing(12)

        self.lbl_breadcrumb = QLabel("แดชบอร์ด")
        self.lbl_breadcrumb.setStyleSheet(f"""
            font-size: 14px;
            font-weight: 600;
            color: {COL_TEXT_PRIMARY};
        """)
        h.addWidget(self.lbl_breadcrumb)
        h.addStretch()

        # ── Active Standard Selector ──
        lbl_std = QLabel("🏅 เกณฑ์อ้างอิง:")
        lbl_std.setStyleSheet(f"""
            font-size: 13px;
            font-weight: 600;
            color: {COL_TEXT_MUTED};
        """)
        h.addWidget(lbl_std)

        self.cb_standard = QComboBox()
        self.cb_standard.setCursor(Qt.PointingHandCursor)
        self.cb_standard.setStyleSheet(f"""
            QComboBox {{
                border: 1px solid {COL_BORDER};
                border-radius: 5px;
                padding: 4px 10px 4px 10px;
                background-color: {COL_BLUE_BG};
                color: {COL_ACCENT_NAVY};
                font-weight: 700;
                font-size: 13px;
                min-width: 200px;
            }}
            QComboBox::drop-down {{
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 0px;
            }}
            QComboBox QAbstractItemView {{
                border: 1px solid {COL_BORDER};
                selection-background-color: {COL_BG_ACTIVE};
                selection-color: {COL_TEXT_WHITE};
                background-color: {COL_BG_WHITE};
            }}
        """)
        # Populate with some standard options
        self.cb_standard.addItem("การกีฬาแห่งประเทศไทย (กกท.)")
        self.cb_standard.addItem("เกณฑ์มาตรฐานกรมพลศึกษา")
        self.cb_standard.addItem("เกณฑ์กำหนดเอง (Custom)")
        h.addWidget(self.cb_standard)
        
        h.addSpacing(20)

        db_name = DATABASE_URL.rsplit("/", 1)[-1]
        db_lbl = QLabel(f"●  {db_name}")
        db_lbl.setStyleSheet(f"""
            font-size: 12px;
            color: {COL_GREEN};
            font-weight: 600;
            padding: 3px 10px;
            background-color: {COL_GREEN_BG};
            border: 1px solid #d1fae5;
            border-radius: 4px;
        """)
        h.addWidget(db_lbl)

        parent_layout.addWidget(bar)

    # ═══════════════════════════════════════════════════════════════════════════
    # CONTENT AREA (Stacked pages)
    # ═══════════════════════════════════════════════════════════════════════════
    def _build_content_stack(self, parent_layout):
        self.stack = QStackedWidget()
        self.stack.setStyleSheet(f"background-color: {COL_BG_PRIMARY}; border: none;")

        # Page 0 — Dashboard (rich)
        self.stack.addWidget(self._page_dashboard())

        # Page 1 — Athletes (real module)
        self.athlete_page = AthletePage()
        self.stack.addWidget(self.athlete_page)

        # Pages 2–5 — Placeholders (will be replaced later)
        placeholders = [
            ("บันทึกการทดสอบ", "📝", "บันทึกผลการทดสอบสมรรถภาพทางกายพร้อมแสดงการประเมินผลเรียลไทม์"),
            ("เกณฑ์อ้างอิง", "📊", "สร้าง แก้ไข นำเข้า และส่งออกตารางเกณฑ์มาตรฐานสมรรถภาพ"),
            ("วิเคราะห์กลุ่ม", "📈", "ดูข้อมูลสรุปของกลุ่ม/ทีม อันดับ ค่าเฉลี่ย และการกระจายตัวของผลการทดสอบ"),
            ("รายงาน", "📄", "สร้างรายงานแบบบุคคลและแบบกลุ่มในรูปแบบไฟล์ PDF และ Excel"),
        ]
        for title, icon, desc in placeholders:
            self.stack.addWidget(self._page_placeholder(title, icon, desc))

        parent_layout.addWidget(self.stack, 1)

    # ── Dashboard Page ────────────────────────────────────────────────────────
    def _page_dashboard(self):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(20)

        # Header
        hdr = QLabel("แดชบอร์ด")
        hdr.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        sub = QLabel("ภาพรวมของกิจกรรมการประเมินสมรรถภาพทางกายและตัวชี้วัดหลัก")
        sub.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED}; margin-top: -4px;")
        lay.addWidget(hdr)
        lay.addWidget(sub)

        # ── Metric Cards Row ──
        cards_row = QHBoxLayout()
        cards_row.setSpacing(16)

        # Query real data from seeded database
        try:
            athlete_count = db_session.query(Athlete).count()
            test_count = db_session.query(TestRecord).count()
            type_count = db_session.query(TestType).count()
            standard_count = db_session.query(Standard).filter_by(is_active=True).count()
        except Exception:
            athlete_count = test_count = type_count = standard_count = 0

        metrics = [
            ("ผู้ทดสอบทั้งหมด",     str(athlete_count),  COL_ACCENT_BLUE, COL_BLUE_BG,   "👤"),
            ("บันทึกผลการทดสอบ",       str(test_count),     COL_GREEN,       COL_GREEN_BG,   "📝"),
            ("ประเภทการทดสอบ",         str(type_count),     COL_PURPLE,      COL_PURPLE_BG,  "🧪"),
            ("เกณฑ์มาตรฐานที่ใช้งาน",   str(standard_count), COL_ORANGE,      COL_ORANGE_BG,  "📊"),
        ]

        for title, value, accent, bg, icon in metrics:
            cards_row.addWidget(self._metric_card(title, value, accent, bg, icon))

        lay.addLayout(cards_row)

        # ── Bottom Row: Recent Tests + Quick Info ──
        bottom_row = QHBoxLayout()
        bottom_row.setSpacing(16)

        # Recent tests table
        recent_card = self._card_frame()
        rc_lay = QVBoxLayout(recent_card)
        rc_lay.setContentsMargins(20, 18, 20, 18)
        rc_lay.setSpacing(12)

        rc_title = QLabel("ผลการประเมินล่าสุด")
        rc_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        rc_lay.addWidget(rc_title)

        table = QTableWidget()
        table.setColumnCount(5)
        table.setHorizontalHeaderLabels(["วันที่ทดสอบ", "ชื่อผู้ทดสอบ", "ประเภทการทดสอบ", "ค่าที่วัดได้", "ระดับผลการประเมิน"])
        table.horizontalHeader().setStretchLastSection(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        table.verticalHeader().setVisible(False)
        table.setAlternatingRowColors(True)
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setMinimumHeight(200)

        # Populate with recent records
        try:
            recent_records = (
                db_session.query(TestRecord)
                .order_by(TestRecord.test_date.desc())
                .limit(8)
                .all()
            )
            table.setRowCount(len(recent_records))
            for row, rec in enumerate(recent_records):
                table.setItem(row, 0, QTableWidgetItem(
                    rec.test_date.strftime("%Y-%m-%d") if rec.test_date else "—"))
                table.setItem(row, 1, QTableWidgetItem(
                    rec.athlete.full_name if rec.athlete else "—"))
                table.setItem(row, 2, QTableWidgetItem(
                    rec.test_type.name if rec.test_type else "—"))
                table.setItem(row, 3, QTableWidgetItem(str(rec.value)))
                grade_item = QTableWidgetItem(rec.interpreted_grade or "—")
                table.setItem(row, 4, grade_item)
        except Exception:
            table.setRowCount(1)
            table.setItem(0, 0, QTableWidgetItem("ยังไม่มีข้อมูลการบันทึก"))

        rc_lay.addWidget(table)
        bottom_row.addWidget(recent_card, 3)

        # Quick-start panel
        qs_card = self._card_frame()
        qs_lay = QVBoxLayout(qs_card)
        qs_lay.setContentsMargins(20, 18, 20, 18)
        qs_lay.setSpacing(10)

        qs_title = QLabel("เมนูลัด")
        qs_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        qs_lay.addWidget(qs_title)

        quick_actions = [
            ("➕  เพิ่มผู้ทดสอบใหม่",         1),
            ("📝  บันทึกผลการทดสอบ",      2),
            ("📊  จัดการเกณฑ์มาตรฐาน",        3),
            ("📈  ดูผลวิเคราะห์กลุ่ม",     4),
            ("📄  ส่งออกรายงาน",          5),
        ]

        for label, idx in quick_actions:
            btn = QPushButton(label)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(40)
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COL_BG_PRIMARY};
                    border: 1px solid {COL_BORDER};
                    border-radius: 6px;
                    text-align: left;
                    padding-left: 14px;
                    font-size: 13px;
                    font-weight: 500;
                    color: {COL_TEXT_BODY};
                }}
                QPushButton:hover {{
                    background-color: {COL_BLUE_BG};
                    border-color: {COL_ACCENT_BLUE};
                    color: {COL_ACCENT_BLUE};
                }}
            """)
            btn.clicked.connect(lambda _=False, i=idx: self._switch_page(i))
            qs_lay.addWidget(btn)

        qs_lay.addStretch()
        bottom_row.addWidget(qs_card, 1)

        lay.addLayout(bottom_row, 1)
        return page

    # ── Placeholder Page ──────────────────────────────────────────────────────
    def _page_placeholder(self, title, icon, description):
        page = QWidget()
        lay = QVBoxLayout(page)
        lay.setContentsMargins(28, 24, 28, 24)
        lay.setSpacing(12)

        hdr = QLabel(title)
        hdr.setStyleSheet(f"font-size: 26px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        sub = QLabel(description)
        sub.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        lay.addWidget(hdr)
        lay.addWidget(sub)

        # Placeholder card
        card = self._card_frame()
        card_lay = QVBoxLayout(card)
        card_lay.setAlignment(Qt.AlignCenter)
        card_lay.setSpacing(12)

        icon_lbl = QLabel(icon)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet("font-size: 48px;")
        card_lay.addWidget(icon_lbl)

        msg = QLabel(f"โมดูล {title}")
        msg.setAlignment(Qt.AlignCenter)
        msg.setStyleSheet(f"font-size: 18px; font-weight: 600; color: {COL_TEXT_BODY};")
        card_lay.addWidget(msg)

        hint = QLabel("โมดูลนี้จะได้รับการพัฒนาและติดตั้งใช้งานในเฟสถัดไป")
        hint.setAlignment(Qt.AlignCenter)
        hint.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        card_lay.addWidget(hint)

        lay.addWidget(card, 1)
        return page

    # ═══════════════════════════════════════════════════════════════════════════
    # REUSABLE COMPONENTS
    # ═══════════════════════════════════════════════════════════════════════════
    def _metric_card(self, title, value, accent_color, bg_color, icon):
        card = self._card_frame()
        card.setMinimumHeight(90)
        lay = QVBoxLayout(card)
        lay.setContentsMargins(16, 12, 16, 12)
        lay.setSpacing(4)

        # Top row: icon + title
        top = QHBoxLayout()
        icon_lbl = QLabel(icon)
        icon_lbl.setFixedSize(32, 32)
        icon_lbl.setAlignment(Qt.AlignCenter)
        icon_lbl.setStyleSheet(f"""
            font-size: 16px;
            background-color: {bg_color};
            border-radius: 7px;
            border: none;
        """)
        top.addWidget(icon_lbl)
        top.addStretch()
        lay.addLayout(top)

        # Value — reduced font size to prevent overflow at 150% scaling
        val_lbl = QLabel(value)
        val_lbl.setStyleSheet(f"""
            font-size: 22px;
            font-weight: 800;
            color: {COL_TEXT_PRIMARY};
        """)
        lay.addWidget(val_lbl)

        # Title
        title_lbl = QLabel(title)
        title_lbl.setStyleSheet(f"""
            font-size: 12px;
            font-weight: 500;
            color: {COL_TEXT_MUTED};
        """)
        lay.addWidget(title_lbl)

        return card

    def _card_frame(self):
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {COL_BG_WHITE};
                border: 1px solid {COL_BORDER};
                border-radius: 10px;
            }}
        """)
        return card

    # ═══════════════════════════════════════════════════════════════════════════
    # STATUS BAR
    # ═══════════════════════════════════════════════════════════════════════════
    def _init_status_bar(self):
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage(f"พร้อมใช้งาน  ·  เชื่อมต่อฐานข้อมูลเรียบร้อย  ·  {APP_NAME} v{VERSION}")

    # ═══════════════════════════════════════════════════════════════════════════
    # NAVIGATION
    # ═══════════════════════════════════════════════════════════════════════════
    def _switch_page(self, index):
        # Update sidebar checked states
        for btn, idx in self.nav_buttons:
            btn.setChecked(idx == index)

        self.stack.setCurrentIndex(index)

        breadcrumbs = [
            "แดชบอร์ด",
            "ป้อนข้อมูล  ›  ข้อมูลผู้ทดสอบ",
            "ป้อนข้อมูล  ›  บันทึกการทดสอบ",
            "เกณฑ์มาตรฐาน  ›  เกณฑ์อ้างอิง",
            "การวิเคราะห์  ›  วิเคราะห์กลุ่ม",
            "การวิเคราะห์  ›  รายงาน",
        ]
        self.lbl_breadcrumb.setText(breadcrumbs[index])
        self.status_bar.showMessage(f"มุมมองปัจจุบัน: {breadcrumbs[index]}")

    def _toggle_sidebar(self):
        is_visible = self.sidebar.isVisible()
        self.sidebar.setVisible(not is_visible)
        if self.sidebar.isVisible():
            self.btn_toggle_sidebar.setText("☰")
            self.btn_toggle_sidebar.setToolTip("ซ่อนเมนู")
        else:
            self.btn_toggle_sidebar.setText("▶")
            self.btn_toggle_sidebar.setToolTip("แสดงเมนู")

    # ═══════════════════════════════════════════════════════════════════════════
    # DIALOGS
    # ═══════════════════════════════════════════════════════════════════════════
    def _msg(self, title, text):
        QMessageBox.information(self, title, text)

    def _show_about(self):
        QMessageBox.about(
            self,
            "เกี่ยวกับ FITSCORE",
            f"<h2 style='color:{COL_ACCENT_NAVY};'>FITSCORE v{VERSION}</h2>"
            "<p><b>ระบบจัดการและประเมินผลสมรรถภาพทางกาย</b></p>"
            "<p style='color:#10b981; font-size:11px;'>ประเมิน · วิเคราะห์ · พัฒนา</p>"
            "<hr>"
            "<p>เครื่องมือระดับมืออาชีพสำหรับบันทึกผลการทดสอบสมรรถภาพทางกาย "
            "เปรียบเทียบกับเกณฑ์มาตรฐานระดับชาติหรือเกณฑ์ที่กำหนดเอง "
            "และจัดทำรายงานวิเคราะห์ทั้งรายบุคคลและรายกลุ่มอย่างละเอียด</p>"
            "<p>ออกแบบมาสำหรับนักวิทยาศาสตร์การกีฬา ผู้ฝึกสอน โรงเรียน มหาวิทยาลัย "
            "หน่วยงานรัฐบาล และสถานออกกำลังกาย</p>"
            "<br>"
            "<p style='color:#64748b;'>พัฒนาด้วย Python · PySide6 · SQLAlchemy · SQLite</p>"
        )
