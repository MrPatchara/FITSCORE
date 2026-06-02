"""
Athlete Dialogs — Form dialogs for athlete management.
Includes: AthleteFormDialog, GroupManagerDialog, MoveToGroupDialog.
All UI text is in Thai.
"""
from datetime import date
import json
import os
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QDateEdit, QTextEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QHeaderView,
    QAbstractItemView, QMessageBox, QFrame, QSpacerItem, QSizePolicy,
    QWidget, QCompleter, QScrollArea,
)
from PySide6.QtCore import Qt, QDate, Signal
from PySide6.QtGui import QFont

from app.services.athlete_service import AthleteService

# ─── Load Thailand Address Data ──────────────────────────────────────────────
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
THAI_ADDRESSES_PATH = os.path.normpath(os.path.join(CURRENT_DIR, "..", "resources", "thai_addresses.json"))

try:
    with open(THAI_ADDRESSES_PATH, "r", encoding="utf-8") as f:
        THAI_ADDRESSES = json.load(f)
except Exception as e:
    print(f"Error loading thai_addresses.json: {e}")
    THAI_ADDRESSES = {}

def _ensure_arrow_icon():
    resources_dir = os.path.normpath(os.path.join(CURRENT_DIR, "..", "resources"))
    os.makedirs(resources_dir, exist_ok=True)
    path = os.path.join(resources_dir, "arrow_down.png")
    if not os.path.exists(path):
        try:
            from PySide6.QtGui import QImage, QPainter, QColor, QPolygon
            from PySide6.QtCore import QPoint
            img = QImage(24, 24, QImage.Format_ARGB32)
            img.fill(QColor(0, 0, 0, 0))
            painter = QPainter(img)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor("#64748b"))
            painter.setPen(Qt.NoPen)
            poly = QPolygon([
                QPoint(6, 9),
                QPoint(18, 9),
                QPoint(12, 16)
            ])
            painter.drawPolygon(poly)
            painter.end()
            img.save(path)
        except Exception as e:
            print(f"Error generating arrow icon: {e}")

_ensure_arrow_icon()

# ─── Shared Palette (matches main_window design system) ───────────────────────
COL_BG_PRIMARY   = "#f1f5f9"
COL_BG_WHITE     = "#ffffff"
COL_TEXT_PRIMARY  = "#0f172a"
COL_TEXT_BODY     = "#334155"
COL_TEXT_MUTED    = "#64748b"
COL_ACCENT_BLUE  = "#2563eb"
COL_ACCENT_NAVY  = "#1e3a8a"
COL_BORDER       = "#e2e8f0"
COL_GREEN        = "#059669"
COL_GREEN_BG     = "#ecfdf5"
COL_RED          = "#dc2626"
COL_RED_BG       = "#fef2f2"
COL_BLUE_BG      = "#eff6ff"

# ─── Shared button stylesheet helper ──────────────────────────────────────────
def _btn_primary_style():
    return f"""
        QPushButton {{
            background-color: {COL_ACCENT_BLUE};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 9px 22px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #1d4ed8;
        }}
        QPushButton:pressed {{
            background-color: #1e40af;
        }}
    """

def _btn_secondary_style():
    return f"""
        QPushButton {{
            background-color: {COL_BG_WHITE};
            color: {COL_TEXT_BODY};
            border: 1px solid {COL_BORDER};
            border-radius: 6px;
            padding: 9px 22px;
            font-size: 13px;
            font-weight: 500;
        }}
        QPushButton:hover {{
            background-color: {COL_BG_PRIMARY};
            border-color: {COL_TEXT_MUTED};
        }}
    """

def _btn_danger_style():
    return f"""
        QPushButton {{
            background-color: {COL_RED};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 9px 22px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #b91c1c;
        }}
    """

def _btn_success_style():
    return f"""
        QPushButton {{
            background-color: {COL_GREEN};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 9px 22px;
            font-size: 13px;
            font-weight: 600;
        }}
        QPushButton:hover {{
            background-color: #047857;
        }}
    """

def _input_style():
    arrow_path = os.path.normpath(os.path.join(CURRENT_DIR, "..", "resources", "arrow_down.png")).replace("\\", "/")
    return f"""
        QLineEdit, QComboBox, QDateEdit, QTextEdit {{
            border: 1px solid {COL_BORDER};
            border-radius: 6px;
            padding: 8px 12px;
            font-size: 13px;
            background-color: {COL_BG_WHITE};
            color: {COL_TEXT_PRIMARY};
        }}
        QLineEdit:focus, QComboBox:focus, QDateEdit:focus, QTextEdit:focus {{
            border-color: {COL_ACCENT_BLUE};
            outline: none;
        }}
        QComboBox::drop-down, QDateEdit::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 28px;
            border-left: 1px solid {COL_BORDER};
            border-top-right-radius: 6px;
            border-bottom-right-radius: 6px;
            background-color: #f8fafc;
        }}
        QComboBox::drop-down:hover, QDateEdit::drop-down:hover {{
            background-color: #f1f5f9;
        }}
        QComboBox::down-arrow, QDateEdit::down-arrow {{
            image: url({arrow_path});
            width: 12px;
            height: 12px;
        }}
        QComboBox QAbstractItemView {{
            border: 1px solid {COL_BORDER};
            selection-background-color: {COL_ACCENT_BLUE};
            selection-color: white;
            background-color: {COL_BG_WHITE};
        }}
    """

def _dialog_base_style():
    return f"""
        QDialog {{
            background-color: {COL_BG_WHITE};
        }}
        QLabel {{
            color: {COL_TEXT_PRIMARY};
            font-size: 13px;
        }}
        QMenu {{
            background-color: {COL_BG_WHITE};
            color: {COL_TEXT_PRIMARY};
            border: 1px solid {COL_BORDER};
            border-radius: 6px;
            padding: 4px 0px;
        }}
        QMenu::item {{
            padding: 6px 20px 6px 16px;
            background-color: transparent;
            color: {COL_TEXT_PRIMARY};
        }}
        QMenu::item:selected {{
            background-color: {COL_BLUE_BG};
            color: {COL_ACCENT_BLUE};
        }}
    """

def _card_frame_style():
    return f"""
        QFrame {{
            background-color: {COL_BG_WHITE};
            border: 1px solid {COL_BORDER};
            border-radius: 8px;
        }}
    """


# ═══════════════════════════════════════════════════════════════════════════════
# ATHLETE FORM DIALOG  (Add / Edit)
# ═══════════════════════════════════════════════════════════════════════════════

class AthleteFormDialog(QDialog):
    """Dialog for adding or editing an athlete, with contact details and photo upload."""

    def __init__(self, parent=None, athlete=None, service: AthleteService = None):
        super().__init__(parent)
        self.athlete = athlete
        self.service = service or AthleteService()
        self._is_edit = athlete is not None
        
        self.saved_photo_path = None
        self.temp_photo_path = None

        self.setWindowTitle("แก้ไขข้อมูลผู้ทดสอบ" if self._is_edit else "เพิ่มผู้ทดสอบใหม่")
        self.resize(840, 600)
        self.setMinimumSize(800, 500)
        self.setStyleSheet(_dialog_base_style() + _input_style())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()
        if self._is_edit:
            self._populate_from_athlete()

    def _get_photo_abs_path(self, relative_path):
        if not relative_path:
            return ""
        return os.path.normpath(os.path.join(CURRENT_DIR, "..", "..", relative_path))

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(28, 24, 28, 20)
        main_layout.setSpacing(16)

        # ── Header Text Group ──
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)
        header_text_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("แก้ไขข้อมูลผู้ทดสอบ" if self._is_edit else "เพิ่มผู้ทดสอบใหม่")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        header_text_layout.addWidget(title)

        subtitle = QLabel("กรุณากรอกข้อมูลส่วนตัว ข้อมูลติดต่อ และอัปโหลดรูปถ่ายผู้ทดสอบ (* จำเป็นต้องกรอก)")
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        subtitle.setStyleSheet(f"font-size: 12px; color: {COL_TEXT_MUTED};")
        header_text_layout.addWidget(subtitle)

        main_layout.addLayout(header_text_layout)

        # ── Separator ──
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COL_BORDER};")
        main_layout.addWidget(sep)

        # ── Scroll Area ──
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_content_layout = QHBoxLayout(scroll_content)
        scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        scroll_content_layout.setSpacing(24)

        # Left Column: Form Fields
        left_layout = QVBoxLayout()
        left_layout.setSpacing(12)
        
        form_card = QFrame()
        form_card.setStyleSheet(_card_frame_style())
        form_card_lay = QVBoxLayout(form_card)
        form_card_lay.setContentsMargins(18, 16, 18, 16)
        
        form = QGridLayout()
        form.setSpacing(12)
        form.setColumnStretch(0, 0)
        form.setColumnStretch(1, 1)
        form.setColumnStretch(2, 0)
        form.setColumnStretch(3, 1)

        # First name & Last name
        lbl_first_name = QLabel("ชื่อ *")
        lbl_first_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_first_name = QLineEdit()
        self.txt_first_name.setPlaceholderText("เช่น สมชาย")
        
        lbl_last_name = QLabel("นามสกุล *")
        lbl_last_name.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_last_name = QLineEdit()
        self.txt_last_name.setPlaceholderText("เช่น ใจดี")

        form.addWidget(lbl_first_name, 0, 0)
        form.addWidget(self.txt_first_name, 0, 1)
        form.addWidget(lbl_last_name, 0, 2)
        form.addWidget(self.txt_last_name, 0, 3)

        # Gender & Date of birth
        lbl_gender = QLabel("เพศ *")
        lbl_gender.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.cb_gender = QComboBox()
        self.cb_gender.addItems(["ชาย", "หญิง", "อื่นๆ"])
        
        lbl_dob = QLabel("วันเกิด *")
        lbl_dob.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.de_dob = QDateEdit()
        self.de_dob.setCalendarPopup(True)
        self.de_dob.setDisplayFormat("dd/MM/yyyy")
        self.de_dob.setDate(QDate(2000, 1, 1))
        self.de_dob.setMaximumDate(QDate.currentDate())
        self.de_dob.dateChanged.connect(self._update_age_label)

        # Customize calendar widget style and formats
        calendar = self.de_dob.calendarWidget()
        if calendar:
            from PySide6.QtGui import QTextCharFormat, QColor, QBrush
            
            # Format for weekends (Saturday and Sunday) - use slate color to match program theme
            weekend_format = QTextCharFormat()
            weekend_format.setBackground(QBrush(QColor(COL_BG_WHITE)))
            weekend_format.setForeground(QColor("#64748b")) # slate-500
            
            # Format for weekdays (Monday to Friday)
            weekday_format = QTextCharFormat()
            weekday_format.setBackground(QBrush(QColor(COL_BG_WHITE)))
            weekday_format.setForeground(QColor(COL_TEXT_BODY))
            
            # Set format for all days of the week to reset any OS default red background/text
            for day in [Qt.Monday, Qt.Tuesday, Qt.Wednesday, Qt.Thursday, Qt.Friday]:
                calendar.setWeekdayTextFormat(day, weekday_format)
            for day in [Qt.Saturday, Qt.Sunday]:
                calendar.setWeekdayTextFormat(day, weekend_format)
            
            # Set header text format (Sun, Mon... headers) to prevent red background there
            header_format = QTextCharFormat()
            header_format.setBackground(QBrush(QColor(COL_BG_PRIMARY)))
            header_format.setForeground(QColor(COL_TEXT_MUTED))
            calendar.setHeaderTextFormat(header_format)
            
            calendar.setStyleSheet(f"""
                QCalendarWidget {{
                    background-color: {COL_BG_WHITE};
                    border: 1px solid {COL_BORDER};
                    border-radius: 8px;
                }}
                QCalendarWidget QWidget#qt_calendar_navigationbar {{
                    background-color: {COL_BG_PRIMARY};
                    border-bottom: 1px solid {COL_BORDER};
                }}
                QCalendarWidget QToolButton {{
                    color: {COL_TEXT_PRIMARY};
                    font-size: 12px;
                    font-weight: 600;
                    background-color: transparent;
                    border: none;
                    border-radius: 4px;
                    margin: 3px;
                    padding: 3px 6px;
                }}
                QCalendarWidget QToolButton:hover {{
                    background-color: {COL_BORDER};
                }}
                QCalendarWidget QToolButton:pressed {{
                    background-color: {COL_TEXT_MUTED};
                    color: white;
                }}
                QCalendarWidget QAbstractItemView:enabled {{
                    background-color: {COL_BG_WHITE};
                    color: {COL_TEXT_BODY};
                    selection-background-color: {COL_ACCENT_BLUE};
                    selection-color: {COL_BG_WHITE};
                    border: none;
                    outline: none;
                }}
                QCalendarWidget QAbstractItemView:disabled {{
                    color: {COL_BORDER};
                }}
                QCalendarWidget QHeaderView::section {{
                    background-color: {COL_BG_PRIMARY};
                    color: {COL_TEXT_MUTED};
                    font-size: 11px;
                    font-weight: 600;
                    border: none;
                    border-bottom: 1px solid {COL_BORDER};
                    padding: 4px;
                }}
                QCalendarWidget QMenu {{
                    background-color: {COL_BG_WHITE};
                    color: {COL_TEXT_PRIMARY};
                    border: 1px solid {COL_BORDER};
                }}
                QCalendarWidget QMenu::item {{
                    padding: 6px 24px;
                    color: {COL_TEXT_PRIMARY};
                    background-color: transparent;
                }}
                QCalendarWidget QMenu::item:selected {{
                    background-color: {COL_BLUE_BG};
                    color: {COL_ACCENT_BLUE};
                }}
            """)

        form.addWidget(lbl_gender, 1, 0)
        form.addWidget(self.cb_gender, 1, 1)
        form.addWidget(lbl_dob, 1, 2)
        form.addWidget(self.de_dob, 1, 3)

        # Age display (auto-calculated BE year + age)
        lbl_age_title = QLabel("อายุ/ปี พ.ศ. เกิด")
        lbl_age_title.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.lbl_age = QLabel("—")
        self.lbl_age.setStyleSheet(f"""
            font-size: 13px; font-weight: 600; color: {COL_ACCENT_BLUE};
            background-color: {COL_BLUE_BG}; padding: 6px 14px;
            border-radius: 6px; border: 1px solid {COL_BORDER};
        """)
        form.addWidget(lbl_age_title, 2, 0)
        form.addWidget(self.lbl_age, 2, 1, 1, 3)
        self._update_age_label(self.de_dob.date())

        # Group
        lbl_group = QLabel("กลุ่มสังกัด")
        lbl_group.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.cb_group = QComboBox()
        self._load_groups()
        form.addWidget(lbl_group, 3, 0)
        form.addWidget(self.cb_group, 3, 1, 1, 3)

        # Address
        lbl_address = QLabel("ที่อยู่ติดต่อ")
        lbl_address.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText("ที่อยู่ติดต่อสะดวกรวดเร็ว")
        form.addWidget(lbl_address, 4, 0)
        form.addWidget(self.txt_address, 4, 1, 1, 3)

        # Phone & Email
        lbl_phone = QLabel("เบอร์โทรศัพท์")
        lbl_phone.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_phone = QLineEdit()
        self.txt_phone.setPlaceholderText("เช่น 0891234567")
        
        lbl_email = QLabel("อีเมล")
        lbl_email.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_email = QLineEdit()
        self.txt_email.setPlaceholderText("เช่น somchai@email.com")

        form.addWidget(lbl_phone, 5, 0)
        form.addWidget(self.txt_phone, 5, 1)
        form.addWidget(lbl_email, 5, 2)
        form.addWidget(self.txt_email, 5, 3)

        # Notes
        lbl_notes = QLabel("หมายเหตุ")
        lbl_notes.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.txt_notes = QTextEdit()
        self.txt_notes.setPlaceholderText("หมายเหตุเพิ่มเติม (ถ้ามี)")
        self.txt_notes.setMaximumHeight(65)
        form.addWidget(lbl_notes, 6, 0)
        form.addWidget(self.txt_notes, 6, 1, 1, 3)

        form_card_lay.addLayout(form)
        left_layout.addWidget(form_card)
        
        # Right Column: Photo Upload
        right_layout = QVBoxLayout()
        right_layout.setSpacing(14)
        right_layout.setAlignment(Qt.AlignTop | Qt.AlignHCenter)

        photo_card = QFrame()
        photo_card.setStyleSheet(_card_frame_style())
        photo_card.setFixedWidth(240)
        photo_card_lay = QVBoxLayout(photo_card)
        photo_card_lay.setContentsMargins(20, 20, 20, 20)
        photo_card_lay.setAlignment(Qt.AlignCenter)
        photo_card_lay.setSpacing(14)

        lbl_photo_title = QLabel("📷 รูปถ่ายผู้ทดสอบ")
        lbl_photo_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COL_ACCENT_NAVY};")
        photo_card_lay.addWidget(lbl_photo_title)

        # Preview area
        self.lbl_photo_preview = QLabel("📷\nคลิกปุ่มด้านล่างเพื่อเลือกรูป")
        self.lbl_photo_preview.setFixedSize(160, 160)
        self.lbl_photo_preview.setAlignment(Qt.AlignCenter)
        self.lbl_photo_preview.setStyleSheet("""
            border: 2px dashed #cbd5e1;
            border-radius: 12px;
            background-color: #f8fafc;
            color: #64748b;
            font-size: 12px;
            font-weight: 500;
        """)
        photo_card_lay.addWidget(self.lbl_photo_preview)

        # Upload button
        self.btn_upload = QPushButton("เลือกรูปถ่าย")
        self.btn_upload.setStyleSheet(_btn_secondary_style())
        self.btn_upload.setCursor(Qt.PointingHandCursor)
        self.btn_upload.clicked.connect(self._on_select_photo)
        photo_card_lay.addWidget(self.btn_upload)

        # Size restrictions note
        lbl_note = QLabel("ขนาดไฟล์ไม่เกิน 2MB\n(.gif, .jpg, .jpeg, .bmp, .wmf, .png)")
        lbl_note.setAlignment(Qt.AlignCenter)
        lbl_note.setStyleSheet("font-size: 11px; color: #94a3b8; line-height: 1.4;")
        photo_card_lay.addWidget(lbl_note)

        right_layout.addWidget(photo_card)

        # Assemble columns inside scroll area content layout
        scroll_content_layout.addLayout(left_layout, 5)
        scroll_content_layout.addLayout(right_layout, 3)
        scroll_content.setLayout(scroll_content_layout)
        scroll.setWidget(scroll_content)
        
        main_layout.addWidget(scroll, 1)

        # ── Action Buttons ──
        main_layout.addSpacing(8)
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setStyleSheet(_btn_secondary_style())
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("บันทึกการแก้ไข" if self._is_edit else "เพิ่มผู้ทดสอบ")
        btn_save.setStyleSheet(_btn_primary_style())
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)

        main_layout.addLayout(btn_row)

    def _load_groups(self):
        self.cb_group.clear()
        self.cb_group.addItem("— ไม่ระบุกลุ่ม —", None)
        groups = self.service.get_all_groups()
        for g in groups:
            self.cb_group.addItem(g.name, g.id)

    def _populate_from_athlete(self):
        a = self.athlete
        self.txt_first_name.setText(a.first_name)
        self.txt_last_name.setText(a.last_name)

        gender_map = {"Male": "ชาย", "Female": "หญิง", "Other": "อื่นๆ"}
        idx = self.cb_gender.findText(gender_map.get(a.gender, "อื่นๆ"))
        if idx >= 0:
            self.cb_gender.setCurrentIndex(idx)

        self.de_dob.setDate(QDate(a.date_of_birth.year, a.date_of_birth.month, a.date_of_birth.day))
        self._update_age_label(self.de_dob.date())

        if a.group_id:
            idx = self.cb_group.findData(a.group_id)
            if idx >= 0:
                self.cb_group.setCurrentIndex(idx)

        self.txt_address.setText(a.address or "")
        self.txt_phone.setText(a.phone or "")
        self.txt_email.setText(a.email or "")
        self.txt_notes.setPlainText(a.notes or "")

        if hasattr(a, "photo_bytes") and a.photo_bytes:
            self._show_photo_preview(a.photo_bytes)
        elif a.photo_path:
            abs_path = self._get_photo_abs_path(a.photo_path)
            if os.path.exists(abs_path):
                self._show_photo_preview(abs_path)
                self.saved_photo_path = a.photo_path

    def _update_age_label(self, qdate: QDate):
        today = date.today()
        dob = date(qdate.year(), qdate.month(), qdate.day())
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))
        thai_year = qdate.year() + 543
        self.lbl_age.setText(f"เกิดปี พ.ศ. {thai_year}  (อายุ {age} ปี)")

    def _on_select_photo(self):
        from PySide6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "เลือกรูปถ่ายผู้ทดสอบ",
            "",
            "Image Files (*.gif *.jpg *.jpeg *.png *.bmp *.wmf)"
        )
        if file_path:
            # Validate size (max 2MB)
            file_size = os.path.getsize(file_path)
            if file_size > 2 * 1024 * 1024:
                QMessageBox.warning(self, "ไฟล์มีขนาดใหญ่เกินไป", "กรุณาเลือกไฟล์รูปภาพที่มีขนาดไม่เกิน 2MB")
                return
            
            # Validate extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in ['.gif', '.jpg', '.jpeg', '.bmp', '.wmf', '.png']:
                QMessageBox.warning(
                    self,
                    "รูปแบบไฟล์ไม่ถูกต้อง",
                    "รองรับเฉพาะไฟล์รูปภาพสกุล .gif, .jpg, .jpeg, .bmp, .wmf, .png เท่านั้น"
                )
                return

            self.temp_photo_path = file_path
            self._show_photo_preview(file_path)

    def _show_photo_preview(self, path_or_bytes):
        from PySide6.QtGui import QPixmap
        pixmap = QPixmap()
        if isinstance(path_or_bytes, bytes):
            pixmap.loadFromData(path_or_bytes)
        else:
            pixmap.load(path_or_bytes)
            
        if not pixmap.isNull():
            scaled = pixmap.scaled(
                150, 150,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation
            )
            self.lbl_photo_preview.setPixmap(scaled)
            self.lbl_photo_preview.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 12px; background-color: #ffffff;")
        else:
            self.lbl_photo_preview.clear()
            self.lbl_photo_preview.setText("❌ โหลดรูปภาพล้มเหลว")

    def _on_save(self):
        first = self.txt_first_name.text().strip()
        last = self.txt_last_name.text().strip()

        if not first or not last:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกชื่อและนามสกุล")
            return

        gender_map = {"ชาย": "Male", "หญิง": "Female", "อื่นๆ": "Other"}
        gender = gender_map.get(self.cb_gender.currentText(), "Other")

        qd = self.de_dob.date()
        dob = date(qd.year(), qd.month(), qd.day())

        group_id = self.cb_group.currentData()
        
        address = self.txt_address.text().strip()
        phone = self.txt_phone.text().strip()
        email = self.txt_email.text().strip()
        notes = self.txt_notes.toPlainText().strip()

        photo_path = self.athlete.photo_path if self._is_edit else None
        photo_bytes = self.athlete.photo_bytes if (self._is_edit and hasattr(self.athlete, "photo_bytes")) else None

        # If a new photo was chosen, read its bytes
        if self.temp_photo_path:
            try:
                with open(self.temp_photo_path, "rb") as f:
                    photo_bytes = f.read()
                photo_path = None  # Clear path since we store directly in DB
            except Exception as e:
                QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถอ่านไฟล์รูปภาพได้:\n{e}")
                return

        try:
            if self._is_edit:
                self.service.update_athlete(
                    self.athlete.id,
                    first_name=first,
                    last_name=last,
                    gender=gender,
                    date_of_birth=dob,
                    group_id=group_id,
                    notes=notes,
                    address=address,
                    phone=phone,
                    email=email,
                    photo_path=photo_path,
                    photo_bytes=photo_bytes
                )
            else:
                self.service.create_athlete(
                    first_name=first,
                    last_name=last,
                    gender=gender,
                    date_of_birth=dob,
                    group_id=group_id,
                    notes=notes,
                    address=address,
                    phone=phone,
                    email=email,
                    photo_path=photo_path,
                    photo_bytes=photo_bytes
                )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลผู้ทดสอบได้:\n{e}")


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP FORM DIALOG (Add / Edit Detail)
# ═══════════════════════════════════════════════════════════════════════════════

class GroupFormDialog(QDialog):
    """Detailed form dialog for adding or editing a group."""

    def __init__(self, parent=None, group=None, service: AthleteService = None):
        super().__init__(parent)
        self.group = group
        self.service = service or AthleteService()
        self._is_edit = group is not None

        self.setWindowTitle("แก้ไขข้อมูลกลุ่ม" if self._is_edit else "เพิ่มกลุ่มใหม่")
        self.resize(840, 580)
        self.setMinimumSize(800, 480)
        self.setStyleSheet(_dialog_base_style() + _input_style())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()
        self._init_address_fields()
        
        if self._is_edit:
            self._populate_from_group()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # ── Header Text Group ──
        header_text_layout = QVBoxLayout()
        header_text_layout.setSpacing(4)
        header_text_layout.setContentsMargins(0, 0, 0, 0)

        title = QLabel("แก้ไขข้อมูลกลุ่ม" if self._is_edit else "เพิ่มกลุ่มใหม่")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        header_text_layout.addWidget(title)

        subtitle = QLabel("กรุณากรอกข้อมูลกลุ่ม ข้อมูลที่อยู่ และข้อมูลติดต่อผู้ดูแล/ผู้ประสานงาน")
        subtitle.setWordWrap(True)
        subtitle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        subtitle.setStyleSheet(f"font-size: 12px; color: {COL_TEXT_MUTED};")
        header_text_layout.addWidget(subtitle)

        main_layout.addLayout(header_text_layout)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COL_BORDER};")
        main_layout.addWidget(sep)

        # ── Scroll Area ──
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_content_layout = QHBoxLayout(scroll_content)
        scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        scroll_content_layout.setSpacing(16)

        left_column = QVBoxLayout()
        left_column.setSpacing(16)
        right_column = QVBoxLayout()
        right_column.setSpacing(16)

        # ════════ LEFT COLUMN ════════
        # Card 1: ข้อมูลกลุ่ม
        card_info = QFrame()
        card_info.setStyleSheet(_card_frame_style())
        card_info_lay = QVBoxLayout(card_info)
        card_info_lay.setContentsMargins(16, 14, 16, 14)
        card_info_lay.setSpacing(10)

        lbl_info_title = QLabel("📁 ข้อมูลกลุ่ม")
        lbl_info_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COL_ACCENT_NAVY}; border: none;")
        card_info_lay.addWidget(lbl_info_title)

        form_info = QFormLayout()
        form_info.setSpacing(8)
        form_info.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.txt_group_name = QLineEdit()
        self.txt_group_name.setPlaceholderText("เช่น ทีมโรงเรียนกีฬา")
        form_info.addRow("ชื่อกลุ่ม *", self.txt_group_name)

        self.txt_notes = QLineEdit()
        self.txt_notes.setPlaceholderText("หมายเหตุเพิ่มเติม")
        form_info.addRow("หมายเหตุ", self.txt_notes)

        card_info_lay.addLayout(form_info)
        left_column.addWidget(card_info)

        # Card 2: ที่อยู่กลุ่ม
        card_addr = QFrame()
        card_addr.setStyleSheet(_card_frame_style())
        card_addr_lay = QVBoxLayout(card_addr)
        card_addr_lay.setContentsMargins(16, 14, 16, 14)
        card_addr_lay.setSpacing(10)

        lbl_addr_title = QLabel("📍 ที่อยู่กลุ่ม")
        lbl_addr_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COL_ACCENT_NAVY}; border: none;")
        card_addr_lay.addWidget(lbl_addr_title)

        form_addr = QFormLayout()
        form_addr.setSpacing(8)
        form_addr.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.txt_address = QLineEdit()
        self.txt_address.setPlaceholderText("เลขที่, ซอย, ถนน...")
        form_addr.addRow("ที่อยู่รายละเอียด", self.txt_address)

        self.cb_province = QComboBox()
        self.cb_province.setEditable(True)
        self.cb_province.setInsertPolicy(QComboBox.NoInsert)
        self.cb_province.completer().setFilterMode(Qt.MatchContains)
        self.cb_province.completer().setCompletionMode(QCompleter.PopupCompletion)
        form_addr.addRow("จังหวัด", self.cb_province)

        self.cb_district = QComboBox()
        self.cb_district.setEnabled(False)
        self.cb_district.setEditable(True)
        self.cb_district.setInsertPolicy(QComboBox.NoInsert)
        if self.cb_district.completer():
            self.cb_district.completer().setFilterMode(Qt.MatchContains)
            self.cb_district.completer().setCompletionMode(QCompleter.PopupCompletion)
        form_addr.addRow("อำเภอ/เขต", self.cb_district)

        self.cb_sub_district = QComboBox()
        self.cb_sub_district.setEnabled(False)
        self.cb_sub_district.setEditable(True)
        self.cb_sub_district.setInsertPolicy(QComboBox.NoInsert)
        if self.cb_sub_district.completer():
            self.cb_sub_district.completer().setFilterMode(Qt.MatchContains)
            self.cb_sub_district.completer().setCompletionMode(QCompleter.PopupCompletion)
        form_addr.addRow("ตำบล/แขวง", self.cb_sub_district)

        self.txt_postal_code = QLineEdit()
        self.txt_postal_code.setPlaceholderText("รหัสไปรษณีย์")
        form_addr.addRow("รหัสไปรษณีย์", self.txt_postal_code)

        card_addr_lay.addLayout(form_addr)
        left_column.addWidget(card_addr)

        # ════════ RIGHT COLUMN ════════
        # Card 3: ผู้ประสานงานกลุ่ม
        card_coord = QFrame()
        card_coord.setStyleSheet(_card_frame_style())
        card_coord_lay = QVBoxLayout(card_coord)
        card_coord_lay.setContentsMargins(16, 14, 16, 14)
        card_coord_lay.setSpacing(10)

        lbl_coord_title = QLabel("🤝 ผู้ประสานงานกลุ่ม")
        lbl_coord_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COL_ACCENT_NAVY}; border: none;")
        card_coord_lay.addWidget(lbl_coord_title)

        form_coord = QFormLayout()
        form_coord.setSpacing(8)
        form_coord.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.txt_coord_name = QLineEdit()
        self.txt_coord_name.setPlaceholderText("ชื่อผู้ประสานงาน")
        form_coord.addRow("ชื่อ-สกุล", self.txt_coord_name)

        self.txt_coord_phone = QLineEdit()
        self.txt_coord_phone.setPlaceholderText("เบอร์โทรศัพท์")
        form_coord.addRow("เบอร์โทร", self.txt_coord_phone)

        self.txt_coord_email = QLineEdit()
        self.txt_coord_email.setPlaceholderText("อีเมล")
        form_coord.addRow("อีเมล", self.txt_coord_email)

        card_coord_lay.addLayout(form_coord)
        right_column.addWidget(card_coord)

        # Card 4: ผู้ควบคุมการทดสอบ
        card_super = QFrame()
        card_super.setStyleSheet(_card_frame_style())
        card_super_lay = QVBoxLayout(card_super)
        card_super_lay.setContentsMargins(16, 14, 16, 14)
        card_super_lay.setSpacing(10)

        lbl_super_title = QLabel("👮 ผู้ควบคุมการทดสอบ")
        lbl_super_title.setStyleSheet(f"font-size: 14px; font-weight: 700; color: {COL_ACCENT_NAVY}; border: none;")
        card_super_lay.addWidget(lbl_super_title)

        form_super = QFormLayout()
        form_super.setSpacing(8)
        form_super.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)

        self.txt_super_name = QLineEdit()
        self.txt_super_name.setPlaceholderText("ชื่อผู้ควบคุม")
        form_super.addRow("ชื่อ-สกุล", self.txt_super_name)

        self.txt_super_phone = QLineEdit()
        self.txt_super_phone.setPlaceholderText("เบอร์โทรศัพท์")
        form_super.addRow("เบอร์โทร", self.txt_super_phone)

        self.txt_super_email = QLineEdit()
        self.txt_super_email.setPlaceholderText("อีเมล")
        form_super.addRow("อีเมล", self.txt_super_email)

        card_super_lay.addLayout(form_super)
        right_column.addWidget(card_super)

        # Assemble columns inside scroll area content layout
        scroll_content_layout.addLayout(left_column, 1)
        scroll_content_layout.addLayout(right_column, 1)
        scroll_content.setLayout(scroll_content_layout)
        scroll.setWidget(scroll_content)
        
        main_layout.addWidget(scroll, 1)

        # ── Action Buttons ──
        main_layout.addSpacing(10)
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setStyleSheet(_btn_secondary_style())
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_save = QPushButton("บันทึกข้อมูล")
        btn_save.setStyleSheet(_btn_primary_style())
        btn_save.setCursor(Qt.PointingHandCursor)
        btn_save.clicked.connect(self._on_save)
        btn_row.addWidget(btn_save)

        main_layout.addLayout(btn_row)

    def _init_address_fields(self):
        # Populate provinces
        self.cb_province.clear()
        self.cb_province.addItem("— เลือกจังหวัด —", "")
        provinces = sorted(THAI_ADDRESSES.keys())
        for p in provinces:
            self.cb_province.addItem(p)
            
        self.cb_province.currentIndexChanged.connect(self._on_province_changed)
        self.cb_district.currentIndexChanged.connect(self._on_district_changed)
        self.cb_sub_district.currentIndexChanged.connect(self._on_sub_district_changed)

    def _on_province_changed(self, index):
        self.cb_district.blockSignals(True)
        self.cb_sub_district.blockSignals(True)
        
        self.cb_district.clear()
        self.cb_sub_district.clear()
        self.txt_postal_code.clear()
        
        province = self.cb_province.currentText()
        if province and province in THAI_ADDRESSES:
            self.cb_district.addItem("— เลือกอำเภอ/เขต —", "")
            districts = sorted(THAI_ADDRESSES[province].keys())
            for d in districts:
                self.cb_district.addItem(d)
            self.cb_district.setEnabled(True)
        else:
            self.cb_district.setEnabled(False)
            self.cb_sub_district.setEnabled(False)
            
        self.cb_district.blockSignals(False)
        self.cb_sub_district.blockSignals(False)

    def _on_district_changed(self, index):
        self.cb_sub_district.blockSignals(True)
        
        self.cb_sub_district.clear()
        self.txt_postal_code.clear()
        
        province = self.cb_province.currentText()
        district = self.cb_district.currentText()
        
        if province and district and province in THAI_ADDRESSES and district in THAI_ADDRESSES[province]:
            self.cb_sub_district.addItem("— เลือกตำบล/แขวง —", "")
            sub_districts = sorted(THAI_ADDRESSES[province][district].keys())
            for sd in sub_districts:
                self.cb_sub_district.addItem(sd)
            self.cb_sub_district.setEnabled(True)
        else:
            self.cb_sub_district.setEnabled(False)
            
        self.cb_sub_district.blockSignals(False)

    def _on_sub_district_changed(self, index):
        province = self.cb_province.currentText()
        district = self.cb_district.currentText()
        sub_district = self.cb_sub_district.currentText()
        
        if (province and district and sub_district and 
            province in THAI_ADDRESSES and 
            district in THAI_ADDRESSES[province] and 
            sub_district in THAI_ADDRESSES[province][district]):
            zip_code = THAI_ADDRESSES[province][district][sub_district]
            self.txt_postal_code.setText(zip_code)
        else:
            self.txt_postal_code.clear()

    def _populate_from_group(self):
        g = self.group
        self.txt_group_name.setText(g.name or "")
        self.txt_notes.setText(g.description or "")
        self.txt_address.setText(g.address or "")
        
        # Populate contact details
        self.txt_coord_name.setText(g.coordinator_name or "")
        self.txt_coord_phone.setText(g.coordinator_phone or "")
        self.txt_coord_email.setText(g.coordinator_email or "")
        self.txt_super_name.setText(g.supervisor_name or "")
        self.txt_super_phone.setText(g.supervisor_phone or "")
        self.txt_super_email.setText(g.supervisor_email or "")
        
        self.cb_province.blockSignals(True)
        self.cb_district.blockSignals(True)
        self.cb_sub_district.blockSignals(True)
        
        # 1. Province
        p_name = g.province or ""
        p_idx = self.cb_province.findText(p_name)
        if p_idx >= 0:
            self.cb_province.setCurrentIndex(p_idx)
            
            # Load districts
            self.cb_district.clear()
            self.cb_district.addItem("— เลือกอำเภอ/เขต —", "")
            districts = sorted(THAI_ADDRESSES.get(p_name, {}).keys())
            for d in districts:
                self.cb_district.addItem(d)
            self.cb_district.setEnabled(True)
            
            # 2. District
            d_name = g.district or ""
            d_idx = self.cb_district.findText(d_name)
            if d_idx >= 0:
                self.cb_district.setCurrentIndex(d_idx)
                
                # Load sub-districts
                self.cb_sub_district.clear()
                self.cb_sub_district.addItem("— เลือกตำบล/แขวง —", "")
                sub_districts = sorted(THAI_ADDRESSES.get(p_name, {}).get(d_name, {}).keys())
                for sd in sub_districts:
                    self.cb_sub_district.addItem(sd)
                self.cb_sub_district.setEnabled(True)
                
                # 3. Sub-district
                sd_name = g.sub_district or ""
                sd_idx = self.cb_sub_district.findText(sd_name)
                if sd_idx >= 0:
                    self.cb_sub_district.setCurrentIndex(sd_idx)
        
        # 4. Postal Code
        self.txt_postal_code.setText(g.postal_code or "")
        
        self.cb_province.blockSignals(False)
        self.cb_district.blockSignals(False)
        self.cb_sub_district.blockSignals(False)

    def _on_save(self):
        name = self.txt_group_name.text().strip()
        if not name:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกชื่อกลุ่ม")
            return
            
        exclude_id = self.group.id if self._is_edit else None
        if self.service.group_name_exists(name, exclude_id=exclude_id):
            QMessageBox.warning(self, "ชื่อซ้ำ", f"กลุ่มชื่อ \"{name}\" มีอยู่แล้ว")
            return

        # Prepare kwargs
        data = {
            "name": name,
            "description": self.txt_notes.text().strip(),
            "address": self.txt_address.text().strip(),
            "province": self.cb_province.currentText().strip() if self.cb_province.currentText() != "— เลือกจังหวัด —" else "",
            "district": self.cb_district.currentText().strip() if self.cb_district.currentText() != "— เลือกอำเภอ/เขต —" else "",
            "sub_district": self.cb_sub_district.currentText().strip() if self.cb_sub_district.currentText() != "— เลือกตำบล/แขวง —" else "",
            "postal_code": self.txt_postal_code.text().strip(),
            "coordinator_name": self.txt_coord_name.text().strip(),
            "coordinator_phone": self.txt_coord_phone.text().strip(),
            "coordinator_email": self.txt_coord_email.text().strip(),
            "supervisor_name": self.txt_super_name.text().strip(),
            "supervisor_phone": self.txt_super_phone.text().strip(),
            "supervisor_email": self.txt_super_email.text().strip(),
        }

        try:
            if self._is_edit:
                self.service.update_group(self.group.id, **data)
            else:
                self.service.create_group(**data)
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลกลุ่มได้:\n{e}")


# ═══════════════════════════════════════════════════════════════════════════════
# GROUP MANAGER DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class GroupManagerDialog(QDialog):
    """Dialog for managing groups — add, edit, delete."""

    groups_changed = Signal()

    def __init__(self, parent=None, service: AthleteService = None):
        super().__init__(parent)
        self.service = service or AthleteService()

        self.setWindowTitle("จัดการกลุ่ม")
        self.setMinimumSize(780, 500)
        self.setStyleSheet(_dialog_base_style() + _input_style())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()
        self._load_groups()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        # Header Row
        hdr_layout = QHBoxLayout()
        title_vbox = QVBoxLayout()
        
        title = QLabel("จัดการกลุ่ม")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        title_vbox.addWidget(title)

        subtitle = QLabel("สร้าง แก้ไข หรือลบกลุ่ม และดูสมาชิกกลุ่ม")
        subtitle.setStyleSheet(f"font-size: 12px; color: {COL_TEXT_MUTED}; margin-top: -4px;")
        title_vbox.addWidget(subtitle)
        
        hdr_layout.addLayout(title_vbox)
        hdr_layout.addStretch()
        
        btn_add = QPushButton("➕ เพิ่มกลุ่มใหม่")
        btn_add.setStyleSheet(_btn_success_style())
        btn_add.setCursor(Qt.PointingHandCursor)
        btn_add.clicked.connect(self._on_add_group)
        hdr_layout.addWidget(btn_add)
        
        layout.addLayout(hdr_layout)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COL_BORDER};")
        layout.addWidget(sep)

        # ── Groups table ──
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ชื่อกลุ่ม", "หมายเหตุ", "จำนวนสมาชิก", "ดำเนินการ"])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.Fixed)
        self.table.setColumnWidth(3, 180)
        self.table.verticalHeader().setVisible(False)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setStyleSheet(f"""
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
                padding: 8px 12px;
                border: none;
                border-bottom: 2px solid {COL_BORDER};
            }}
            QTableWidget::item {{
                padding: 6px 12px;
                border-bottom: 1px solid {COL_BORDER};
            }}
        """)
        layout.addWidget(self.table, 1)

        # ── Close button ──
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_close = QPushButton("ปิด")
        btn_close.setStyleSheet(_btn_secondary_style())
        btn_close.setCursor(Qt.PointingHandCursor)
        btn_close.clicked.connect(self.accept)
        btn_row.addWidget(btn_close)
        layout.addLayout(btn_row)

    def _load_groups(self):
        groups = self.service.get_all_groups()
        self.table.setRowCount(len(groups))

        for row, group in enumerate(groups):
            # Tooltip for full group information
            tooltip_text = (
                f"ชื่อกลุ่ม: {group.name}\n"
                f"ที่อยู่: {group.full_address or '—'}\n"
                f"ผู้ประสานงาน: {group.coordinator_name or '—'} (โทร: {group.coordinator_phone or '—'})\n"
                f"ผู้ควบคุม: {group.supervisor_name or '—'} (โทร: {group.supervisor_phone or '—'})\n"
                f"หมายเหตุ: {group.description or '—'}"
            )
            
            name_item = QTableWidgetItem(group.name)
            name_item.setToolTip(tooltip_text)
            self.table.setItem(row, 0, name_item)
            
            desc_item = QTableWidgetItem(group.description or "—")
            desc_item.setToolTip(tooltip_text)
            self.table.setItem(row, 1, desc_item)
            
            count_item = QTableWidgetItem(str(len(group.athletes)))
            count_item.setTextAlignment(Qt.AlignCenter)
            count_item.setToolTip(tooltip_text)
            self.table.setItem(row, 2, count_item)

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
                    border: 1px solid {COL_BORDER};
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COL_ACCENT_BLUE};
                    color: white;
                }}
            """)
            btn_edit.clicked.connect(lambda _=False, gid=group.id: self._on_edit_group(gid))
            action_layout.addWidget(btn_edit)

            btn_del = QPushButton("🗑️ ลบ")
            btn_del.setCursor(Qt.PointingHandCursor)
            btn_del.setStyleSheet(f"""
                QPushButton {{
                    background-color: {COL_RED_BG};
                    color: {COL_RED};
                    border: 1px solid {COL_BORDER};
                    border-radius: 4px;
                    padding: 4px 10px;
                    font-size: 12px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {COL_RED};
                    color: white;
                }}
            """)
            btn_del.clicked.connect(lambda _=False, gid=group.id: self._on_delete_group(gid))
            action_layout.addWidget(btn_del)

            self.table.setCellWidget(row, 3, action_widget)
            self.table.setRowHeight(row, 44)

    def _on_add_group(self):
        dlg = GroupFormDialog(self, service=self.service)
        if dlg.exec() == QDialog.Accepted:
            self._load_groups()
            self.groups_changed.emit()

    def _on_edit_group(self, group_id):
        group = self.service.get_group_by_id(group_id)
        if not group:
            return
        dlg = GroupFormDialog(self, group=group, service=self.service)
        if dlg.exec() == QDialog.Accepted:
            self._load_groups()
            self.groups_changed.emit()

    def _on_delete_group(self, group_id):
        group = self.service.get_group_by_id(group_id)
        if not group:
            return

        member_count = len(group.athletes)
        msg = f"ต้องการลบกลุ่ม \"{group.name}\" หรือไม่?"
        if member_count > 0:
            msg += f"\n\nสมาชิก {member_count} คนในกลุ่มนี้จะถูกย้ายออกเป็น \"ไม่ระบุกลุ่ม\" โดยอัตโนมัติ"

        dlg = CustomConfirmDialog(self, title="ยืนยันการลบกลุ่ม", message=msg, yes_text="ลบกลุ่ม", no_text="ยกเลิก", is_danger=True)
        if dlg.exec() == QDialog.Accepted:
            self.service.delete_group(group_id)
            self._load_groups()
            self.groups_changed.emit()


# ═══════════════════════════════════════════════════════════════════════════════
# MOVE TO GROUP DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class MoveToGroupDialog(QDialog):
    """Dialog for assigning selected athletes to a group (or removing from group)."""

    def __init__(self, parent=None, selected_count: int = 0, service: AthleteService = None):
        super().__init__(parent)
        self.service = service or AthleteService()
        self._selected_count = selected_count

        self.setWindowTitle("ย้ายผู้ทดสอบเข้ากลุ่ม")
        self.setMinimumWidth(420)
        self.setStyleSheet(_dialog_base_style() + _input_style())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 24, 28, 20)
        layout.setSpacing(16)

        title = QLabel("ย้ายผู้ทดสอบเข้ากลุ่ม")
        title.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        layout.addWidget(title)

        info = QLabel(f"เลือกกลุ่มปลายทางสำหรับผู้ทดสอบ {self._selected_count} คนที่เลือก")
        info.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        layout.addWidget(info)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COL_BORDER};")
        layout.addWidget(sep)

        form = QFormLayout()
        form.setSpacing(12)

        self.cb_target_group = QComboBox()
        self.cb_target_group.addItem("— ย้ายออกจากกลุ่ม (ไม่ระบุ) —", None)
        groups = self.service.get_all_groups()
        for g in groups:
            self.cb_target_group.addItem(f"{g.name}  ({len(g.athletes)} คน)", g.id)
        form.addRow("กลุ่มปลายทาง", self.cb_target_group)
        layout.addLayout(form)

        layout.addSpacing(8)
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        btn_cancel = QPushButton("ยกเลิก")
        btn_cancel.setStyleSheet(_btn_secondary_style())
        btn_cancel.setCursor(Qt.PointingHandCursor)
        btn_cancel.clicked.connect(self.reject)
        btn_row.addWidget(btn_cancel)

        btn_move = QPushButton("ย้ายเข้ากลุ่ม")
        btn_move.setStyleSheet(_btn_primary_style())
        btn_move.setCursor(Qt.PointingHandCursor)
        btn_move.clicked.connect(self.accept)
        btn_row.addWidget(btn_move)

        layout.addLayout(btn_row)

    def selected_group_id(self):
        """Returns the group_id selected, or None if 'no group'."""
        return self.cb_target_group.currentData()


# ═══════════════════════════════════════════════════════════════════════════════
# CUSTOM CONFIRM DIALOG
# ═══════════════════════════════════════════════════════════════════════════════

class CustomConfirmDialog(QDialog):
    """A premium custom confirmation dialog that matches application theme."""

    def __init__(self, parent=None, title="", message="", yes_text="ใช่", no_text="ไม่ใช่", is_danger=True):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setMinimumWidth(400)
        self.setStyleSheet(_dialog_base_style() + _input_style())
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 20)
        layout.setSpacing(16)

        # Header Row (Icon + Title)
        header = QHBoxLayout()
        header.setSpacing(12)

        icon_label = QLabel("⚠️" if is_danger else "❓")
        icon_label.setStyleSheet("font-size: 26px;")
        header.addWidget(icon_label)

        title_label = QLabel(title)
        title_label.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        header.addWidget(title_label, 1)

        layout.addLayout(header)

        # Message
        msg_label = QLabel(message)
        msg_label.setWordWrap(True)
        msg_label.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_BODY}; line-height: 1.5;")
        layout.addWidget(msg_label)

        # Separator
        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet(f"color: {COL_BORDER};")
        layout.addWidget(sep)

        # Action Buttons
        btn_row = QHBoxLayout()
        btn_row.addStretch()

        btn_no = QPushButton(no_text)
        btn_no.setStyleSheet(_btn_secondary_style())
        btn_no.setCursor(Qt.PointingHandCursor)
        btn_no.clicked.connect(self.reject)
        btn_row.addWidget(btn_no)

        btn_yes = QPushButton(yes_text)
        btn_yes.setStyleSheet(_btn_danger_style() if is_danger else _btn_primary_style())
        btn_yes.setCursor(Qt.PointingHandCursor)
        btn_yes.clicked.connect(self.accept)
        btn_row.addWidget(btn_yes)

        layout.addLayout(btn_row)

