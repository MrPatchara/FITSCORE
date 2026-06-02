"""
TestEntryPage — Page for recording fitness assessment results and calculations.
All UI text is in Thai.
"""
import math
from datetime import date
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QComboBox, QPushButton,
    QFrame, QMessageBox, QScrollArea, QSizePolicy,
    QButtonGroup, QRadioButton, QFormLayout
)
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QFont, QPixmap, QIcon

from app.core.db import db_session
from app.models.athlete import Athlete, Group
from app.models.test_type import TestType
from app.models.record import TestRecord
from app.services.athlete_service import AthleteService
from app.services.interpreter import InterpreterService

# ─── Design System ────────────────────────────────────────────────────────────
COL_BG_PRIMARY   = "#f1f5f9"   # Slate 100
COL_BG_WHITE     = "#ffffff"   # Pure white
COL_TEXT_PRIMARY  = "#0f172a"   # Slate 900
COL_TEXT_BODY     = "#334155"   # Slate 700
COL_TEXT_MUTED    = "#64748b"   # Slate 500
COL_TEXT_LIGHT    = "#94a3b8"   # Slate 400
COL_ACCENT_BLUE  = "#2563eb"   # Blue 600
COL_ACCENT_NAVY  = "#1e3a8a"   # Blue 900
COL_BORDER       = "#e2e8f0"   # Slate 200
COL_GREEN        = "#059669"   # Emerald 600
COL_GREEN_BG     = "#ecfdf5"   # Emerald 50
COL_ORANGE       = "#d97706"   # Amber 600
COL_ORANGE_BG    = "#fffbeb"   # Amber 50
COL_RED          = "#dc2626"   # Red 600
COL_RED_BG       = "#fef2f2"   # Red 50
COL_BLUE_BG      = "#eff6ff"   # Blue 50
COL_PURPLE       = "#7c3aed"   # Violet 600
COL_PURPLE_BG    = "#f5f3ff"   # Violet 50


def get_or_create_test_type(session, name, unit, category):
    tt = session.query(TestType).filter_by(name=name).first()
    if not tt:
        tt = TestType(name=name, unit=unit, category=category, description=name)
        session.add(tt)
        session.commit()
    return tt


class TestEntryPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.athlete_service = AthleteService()
        self.interpreter = InterpreterService(db_session)
        
        # Temp variables for calculators
        self.current_fat_pct = None
        self.current_fat_res = None
        self.current_vo2max = None
        self.current_vo2_res = None
        
        self._build_ui()
        self._load_athletes()

    def _build_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(24, 16, 24, 16)
        main_layout.setSpacing(14)

        # ── Header ──
        hdr_layout = QVBoxLayout()
        hdr_layout.setSpacing(4)
        
        hdr = QLabel("บันทึกผลการทดสอบสมรรถภาพทางกาย")
        hdr.setStyleSheet(f"font-size: 24px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        hdr_layout.addWidget(hdr)

        sub = QLabel("บันทึกผลการประเมินรายบุคคลพร้อมระบบคำนวณและประเมินผลตามเกณฑ์มาตรฐานอัตโนมัติ")
        sub.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        hdr_layout.addWidget(sub)
        main_layout.addLayout(hdr_layout)

        # ── Scroll Area for Forms ──
        scroll = QScrollArea(self)
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet("QScrollArea { background-color: transparent; border: none; }")

        scroll_content = QWidget()
        scroll_content.setStyleSheet("background-color: transparent;")
        scroll_content_layout = QHBoxLayout(scroll_content)
        scroll_content_layout.setContentsMargins(0, 0, 0, 0)
        scroll_content_layout.setSpacing(20)

        # ════════ LEFT COLUMN: Athlete Selection & Pre-test ════════
        left_layout = QVBoxLayout()
        left_layout.setSpacing(16)
        left_layout.setAlignment(Qt.AlignTop)

        # 1. Card: Athlete Selection & Profile Info
        ath_card = QFrame()
        ath_card.setStyleSheet(self._card_style())
        ath_lay = QVBoxLayout(ath_card)
        ath_lay.setContentsMargins(18, 16, 18, 16)
        ath_lay.setSpacing(12)

        lbl_ath_title = QLabel("👤 เลือกผู้เข้ารับการทดสอบ")
        lbl_ath_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_ACCENT_NAVY};")
        ath_lay.addWidget(lbl_ath_title)

        self.cb_athlete = QComboBox()
        self.cb_athlete.setStyleSheet(self._input_style())
        self.cb_athlete.currentIndexChanged.connect(self._on_athlete_changed)
        ath_lay.addWidget(self.cb_athlete)

        # Profile display box
        profile_box = QFrame()
        profile_box.setStyleSheet(f"background-color: {COL_BG_PRIMARY}; border-radius: 6px; border: none;")
        profile_lay = QHBoxLayout(profile_box)
        profile_lay.setContentsMargins(12, 10, 12, 10)
        profile_lay.setSpacing(16)

        self.lbl_avatar = QLabel("👤")
        self.lbl_avatar.setFixedSize(70, 70)
        self.lbl_avatar.setAlignment(Qt.AlignCenter)
        self.lbl_avatar.setStyleSheet("font-size: 32px; border: 1px dashed #cbd5e1; border-radius: 6px; background-color: #ffffff;")
        profile_lay.addWidget(self.lbl_avatar)

        details_lay = QVBoxLayout()
        details_lay.setSpacing(4)
        self.lbl_gender = QLabel("เพศ: —")
        self.lbl_gender.setStyleSheet("font-weight: 600;")
        self.lbl_age = QLabel("อายุ: —")
        self.lbl_age.setStyleSheet("font-weight: 600;")
        self.lbl_group = QLabel("กลุ่ม: —")
        self.lbl_group.setStyleSheet("font-weight: 600;")
        details_lay.addWidget(self.lbl_gender)
        details_lay.addWidget(self.lbl_age)
        details_lay.addWidget(self.lbl_group)
        profile_lay.addLayout(details_lay)
        profile_lay.addStretch()

        ath_lay.addWidget(profile_box)
        left_layout.addWidget(ath_card)

        # 2. Card: General Info & BMI
        gen_card = QFrame()
        gen_card.setStyleSheet(self._card_style())
        gen_lay = QVBoxLayout(gen_card)
        gen_lay.setContentsMargins(18, 16, 18, 16)
        gen_lay.setSpacing(12)

        lbl_gen_title = QLabel("🩺 ข้อมูลทั่วไปก่อนทดสอบ")
        lbl_gen_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_ACCENT_NAVY};")
        gen_lay.addWidget(lbl_gen_title)

        form_grid = QGridLayout()
        form_grid.setSpacing(10)

        # Weight & Height
        form_grid.addWidget(QLabel("น้ำหนัก (กิโลกรัม)"), 0, 0)
        self.txt_weight = QLineEdit()
        self.txt_weight.setPlaceholderText("เช่น 65.5")
        self.txt_weight.setStyleSheet(self._input_style())
        self.txt_weight.textChanged.connect(self._on_bmi_inputs_changed)
        form_grid.addWidget(self.txt_weight, 0, 1)

        form_grid.addWidget(QLabel("ส่วนสูง (เซนติเมตร)"), 0, 2)
        self.txt_height = QLineEdit()
        self.txt_height.setPlaceholderText("เช่น 175")
        self.txt_height.setStyleSheet(self._input_style())
        self.txt_height.textChanged.connect(self._on_bmi_inputs_changed)
        form_grid.addWidget(self.txt_height, 0, 3)

        # Pulse & Blood Pressure
        form_grid.addWidget(QLabel("ชีพจร (ครั้ง/นาที)"), 1, 0)
        self.txt_pulse = QLineEdit()
        self.txt_pulse.setPlaceholderText("เช่น 72")
        self.txt_pulse.setStyleSheet(self._input_style())
        form_grid.addWidget(self.txt_pulse, 1, 1)

        form_grid.addWidget(QLabel("ความดันโลหิต บน/ล่าง"), 1, 2)
        bp_layout = QHBoxLayout()
        bp_layout.setSpacing(4)
        self.txt_bp_sys = QLineEdit()
        self.txt_bp_sys.setPlaceholderText("บน (Sys)")
        self.txt_bp_sys.setStyleSheet(self._input_style())
        self.txt_bp_dia = QLineEdit()
        self.txt_bp_dia.setPlaceholderText("ล่าง (Dia)")
        self.txt_bp_dia.setStyleSheet(self._input_style())
        bp_layout.addWidget(self.txt_bp_sys)
        bp_layout.addWidget(self.txt_bp_dia)
        form_grid.addLayout(bp_layout, 1, 3)

        # Status: Athlete vs General
        form_grid.addWidget(QLabel("ประเภทบุคลากร"), 2, 0)
        status_lay = QHBoxLayout()
        status_lay.setSpacing(10)
        self.rad_general = QRadioButton("บุคคลทั่วไป")
        self.rad_general.setChecked(True)
        self.rad_general.toggled.connect(self._on_bmi_inputs_changed)
        self.rad_athlete = QRadioButton("นักกีฬา")
        self.rad_athlete.toggled.connect(self._on_bmi_inputs_changed)
        status_lay.addWidget(self.rad_general)
        status_lay.addWidget(self.rad_athlete)
        form_grid.addLayout(status_lay, 2, 1, 1, 3)

        # Exercise Frequency
        form_grid.addWidget(QLabel("ความถี่ออกกำลังกาย"), 3, 0)
        self.cb_exercise_freq = QComboBox()
        self.cb_exercise_freq.addItems([
            "ไม่ค่อยออกกำลังกาย",
            "1-2 ครั้ง / สัปดาห์",
            "3-4 ครั้ง / สัปดาห์",
            "5 ครั้งขึ้นไป / สัปดาห์"
        ])
        self.cb_exercise_freq.setStyleSheet(self._input_style())
        form_grid.addWidget(self.cb_exercise_freq, 3, 1, 1, 3)

        gen_lay.addLayout(form_grid)

        # Separator line
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet(f"color: {COL_BORDER};")
        gen_lay.addWidget(line)

        # BMI Output Indicators
        bmi_out_lay = QHBoxLayout()
        bmi_out_lay.setSpacing(16)
        
        # BMI Display
        bmi_v_box = QVBoxLayout()
        bmi_v_box.setSpacing(4)
        bmi_v_box.addWidget(QLabel("ดัชนีมวลกาย (BMI)"))
        self.lbl_bmi_val = QLabel("—")
        self.lbl_bmi_val.setStyleSheet(f"font-size: 20px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        bmi_v_box.addWidget(self.lbl_bmi_val)
        bmi_out_lay.addLayout(bmi_v_box)

        # Body Shape Display
        shape_v_box = QVBoxLayout()
        shape_v_box.setSpacing(4)
        shape_v_box.addWidget(QLabel("การประเมินรูปร่าง"))
        self.lbl_bmi_shape = QLabel("—")
        self.lbl_bmi_shape.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_TEXT_MUTED};")
        shape_v_box.addWidget(self.lbl_bmi_shape)
        bmi_out_lay.addLayout(shape_v_box)
        
        bmi_out_lay.addStretch()
        gen_lay.addLayout(bmi_out_lay)

        left_layout.addWidget(gen_card)
        scroll_content_layout.addLayout(left_layout, 4)

        # ════════ RIGHT COLUMN: Test Performance Details ════════
        right_layout = QVBoxLayout()
        right_layout.setSpacing(16)
        right_layout.setAlignment(Qt.AlignTop)

        # 3. Card: Skinfold Fat percentage
        fat_card = QFrame()
        fat_card.setStyleSheet(self._card_style())
        fat_lay = QVBoxLayout(fat_card)
        fat_lay.setContentsMargins(18, 16, 18, 16)
        fat_lay.setSpacing(12)

        lbl_fat_title = QLabel("1. เปอร์เซ็นต์ไขมัน (Skinfold Thickness)")
        lbl_fat_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_ACCENT_NAVY};")
        fat_lay.addWidget(lbl_fat_title)

        fat_grid = QGridLayout()
        fat_grid.setSpacing(10)
        
        fat_grid.addWidget(QLabel("Biceps (มม.)"), 0, 0)
        self.txt_fat_biceps = QLineEdit()
        self.txt_fat_biceps.setStyleSheet(self._input_style())
        fat_grid.addWidget(self.txt_fat_biceps, 0, 1)

        fat_grid.addWidget(QLabel("Triceps (มม.)"), 0, 2)
        self.txt_fat_triceps = QLineEdit()
        self.txt_fat_triceps.setStyleSheet(self._input_style())
        fat_grid.addWidget(self.txt_fat_triceps, 0, 3)

        fat_grid.addWidget(QLabel("Subscapular (มม.)"), 1, 0)
        self.txt_fat_sub = QLineEdit()
        self.txt_fat_sub.setStyleSheet(self._input_style())
        fat_grid.addWidget(self.txt_fat_sub, 1, 1)

        fat_grid.addWidget(QLabel("Supraliac (มม.)"), 1, 2)
        self.txt_fat_sup = QLineEdit()
        self.txt_fat_sup.setStyleSheet(self._input_style())
        fat_grid.addWidget(self.txt_fat_sup, 1, 3)

        fat_lay.addLayout(fat_grid)

        # Calc row for Fat %
        fat_calc_row = QHBoxLayout()
        self.btn_calc_fat = QPushButton("คำนวณเปอร์เซ็นต์ไขมัน")
        self.btn_calc_fat.setCursor(Qt.PointingHandCursor)
        self.btn_calc_fat.setStyleSheet(self._btn_secondary_style())
        self.btn_calc_fat.clicked.connect(self._calculate_body_fat)
        fat_calc_row.addWidget(self.btn_calc_fat)
        fat_calc_row.addSpacing(16)

        fat_results_box = QHBoxLayout()
        fat_results_box.setSpacing(12)
        self.lbl_fat_val = QLabel("—")
        self.lbl_fat_val.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        self.lbl_fat_grade = QLabel("ระดับ: —")
        self.lbl_fat_grade.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        self.lbl_fat_score = QLabel("คะแนน: —")
        self.lbl_fat_score.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        
        fat_results_box.addWidget(self.lbl_fat_val)
        fat_results_box.addWidget(self.lbl_fat_grade)
        fat_results_box.addWidget(self.lbl_fat_score)
        fat_calc_row.addLayout(fat_results_box)
        fat_calc_row.addStretch()
        fat_lay.addLayout(fat_calc_row)

        right_layout.addWidget(fat_card)

        # 4. Card: Muscular System & Other Tests
        phys_card = QFrame()
        phys_card.setStyleSheet(self._card_style())
        phys_lay = QVBoxLayout(phys_card)
        phys_lay.setContentsMargins(18, 16, 18, 16)
        phys_lay.setSpacing(12)

        lbl_phys_title = QLabel("2. ระบบกล้ามเนื้อ / ความอ่อนตัว / ความจุปอด")
        lbl_phys_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_ACCENT_NAVY};")
        phys_lay.addWidget(lbl_phys_title)

        phys_grid = QGridLayout()
        phys_grid.setSpacing(10)

        # Arm & Leg Strength
        phys_grid.addWidget(QLabel("ความแข็งแรงแขน (กก.)"), 0, 0)
        self.txt_strength_arm = QLineEdit()
        self.txt_strength_arm.setStyleSheet(self._input_style())
        self.txt_strength_arm.textChanged.connect(self._update_overall_summary)
        phys_grid.addWidget(self.txt_strength_arm, 0, 1)

        phys_grid.addWidget(QLabel("ความแข็งแรงขา (กก.)"), 0, 2)
        self.txt_strength_leg = QLineEdit()
        self.txt_strength_leg.setStyleSheet(self._input_style())
        self.txt_strength_leg.textChanged.connect(self._update_overall_summary)
        phys_grid.addWidget(self.txt_strength_leg, 0, 3)

        # Flexibility & Lung capacity
        phys_grid.addWidget(QLabel("ความอ่อนตัว (ซม.)"), 1, 0)
        self.txt_flexibility = QLineEdit()
        self.txt_flexibility.setStyleSheet(self._input_style())
        self.txt_flexibility.textChanged.connect(self._update_overall_summary)
        phys_grid.addWidget(self.txt_flexibility, 1, 1)

        phys_grid.addWidget(QLabel("ความจุปอด (มล.)"), 1, 2)
        self.txt_lung = QLineEdit()
        self.txt_lung.setStyleSheet(self._input_style())
        self.txt_lung.textChanged.connect(self._update_overall_summary)
        phys_grid.addWidget(self.txt_lung, 1, 3)

        phys_lay.addLayout(phys_grid)
        right_layout.addWidget(phys_card)

        # 5. Card: Cardiorespiratory cycle test
        cardio_card = QFrame()
        cardio_card.setStyleSheet(self._card_style())
        cardio_lay = QVBoxLayout(cardio_card)
        cardio_lay.setContentsMargins(18, 16, 18, 16)
        cardio_lay.setSpacing(12)

        lbl_cardio_title = QLabel("3. ระบบหายใจและไหลเวียนเลือด (Astrand Cycle Ergometer)")
        lbl_cardio_title.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {COL_ACCENT_NAVY};")
        cardio_lay.addWidget(lbl_cardio_title)

        cardio_grid = QGridLayout()
        cardio_grid.setSpacing(10)

        cardio_grid.addWidget(QLabel("ชีพจรขณะทดสอบ (ครั้ง/นาที)"), 0, 0)
        self.txt_pulse_test = QLineEdit()
        self.txt_pulse_test.setStyleSheet(self._input_style())
        cardio_grid.addWidget(self.txt_pulse_test, 0, 1)

        cardio_grid.addWidget(QLabel("น้ำหนักถ่วง (กิโลปอนด์ - kp)"), 0, 2)
        self.txt_load_weight = QLineEdit()
        self.txt_load_weight.setStyleSheet(self._input_style())
        cardio_grid.addWidget(self.txt_load_weight, 0, 3)

        cardio_lay.addLayout(cardio_grid)

        # Calc row for Cardio VO2max
        cardio_calc_row = QHBoxLayout()
        self.btn_calc_cardio = QPushButton("คำนวณ VO2max")
        self.btn_calc_cardio.setCursor(Qt.PointingHandCursor)
        self.btn_calc_cardio.setStyleSheet(self._btn_secondary_style())
        self.btn_calc_cardio.clicked.connect(self._calculate_cardio)
        cardio_calc_row.addWidget(self.btn_calc_cardio)
        cardio_calc_row.addSpacing(16)

        cardio_results_box = QHBoxLayout()
        cardio_results_box.setSpacing(12)
        self.lbl_cardio_val = QLabel("—")
        self.lbl_cardio_val.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COL_TEXT_PRIMARY};")
        self.lbl_cardio_grade = QLabel("ระดับ: —")
        self.lbl_cardio_grade.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        self.lbl_cardio_score = QLabel("คะแนน: —")
        self.lbl_cardio_score.setStyleSheet(f"font-size: 13px; color: {COL_TEXT_MUTED};")
        
        cardio_results_box.addWidget(self.lbl_cardio_val)
        cardio_results_box.addWidget(self.lbl_cardio_grade)
        cardio_results_box.addWidget(self.lbl_cardio_score)
        cardio_calc_row.addLayout(cardio_results_box)
        cardio_calc_row.addStretch()
        cardio_lay.addLayout(cardio_calc_row)

        right_layout.addWidget(cardio_card)

        scroll_content_layout.addLayout(right_layout, 5)
        scroll_content.setLayout(scroll_content_layout)
        scroll.setWidget(scroll_content)
        main_layout.addWidget(scroll, 1)

        # ── Bottom Summary Row & Action Buttons ──
        bottom_box = QFrame()
        bottom_box.setStyleSheet(f"background-color: {COL_BG_WHITE}; border: 1px solid {COL_BORDER}; border-radius: 10px;")
        bottom_lay = QHBoxLayout(bottom_box)
        bottom_lay.setContentsMargins(20, 14, 20, 14)
        bottom_lay.setSpacing(20)

        # Total Scores Display
        score_v_lay = QVBoxLayout()
        score_v_lay.setSpacing(2)
        score_v_lay.addWidget(QLabel("คะแนนรวมสมรรถภาพ (เต็ม 30 คะแนน)"))
        self.lbl_summary_score = QLabel("—")
        self.lbl_summary_score.setStyleSheet(f"font-size: 24px; font-weight: 800; color: {COL_ACCENT_BLUE};")
        score_v_lay.addWidget(self.lbl_summary_score)
        bottom_lay.addLayout(score_v_lay)

        # Overall Grade Display
        grade_v_lay = QVBoxLayout()
        grade_v_lay.setSpacing(2)
        grade_v_lay.addWidget(QLabel("การประเมินผลสมรรถภาพรวม"))
        self.lbl_summary_grade = QLabel("—")
        self.lbl_summary_grade.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {COL_TEXT_MUTED};")
        grade_v_lay.addWidget(self.lbl_summary_grade)
        bottom_lay.addLayout(grade_v_lay)

        bottom_lay.addStretch()

        # Action Buttons
        self.btn_save_records = QPushButton("💾 บันทึกข้อมูลการทดสอบ")
        self.btn_save_records.setCursor(Qt.PointingHandCursor)
        self.btn_save_records.setStyleSheet(self._btn_primary_style())
        self.btn_save_records.clicked.connect(self._on_save)
        bottom_lay.addWidget(self.btn_save_records)

        main_layout.addWidget(bottom_box)

    def _load_athletes(self):
        self.cb_athlete.blockSignals(True)
        self.cb_athlete.clear()
        self.cb_athlete.addItem("— กรุณาเลือกผู้ทดสอบ —", None)
        
        athletes = self.athlete_service.get_all_athletes()
        for a in athletes:
            self.cb_athlete.addItem(f"{a.full_name} (อายุ {a.age} ปี, {a.group.name if a.group else 'ไม่มีกลุ่ม'})", a.id)
            
        self.cb_athlete.blockSignals(False)
        self._on_athlete_changed()

    def _on_athlete_changed(self):
        athlete_id = self.cb_athlete.currentData()
        if not athlete_id:
            self._clear_form()
            return
            
        athlete = self.athlete_service.get_athlete_by_id(athlete_id)
        if not athlete:
            self._clear_form()
            return
            
        # Display details
        self.lbl_gender.setText(f"เพศ: {'ชาย' if athlete.gender == 'Male' else 'หญิง' if athlete.gender == 'Female' else 'อื่นๆ'}")
        self.lbl_age.setText(f"อายุ: {athlete.age} ปี")
        self.lbl_group.setText(f"กลุ่ม: {athlete.group.name if athlete.group else '—'}")
        
        # Load avatar
        if athlete.photo_bytes:
            pixmap = QPixmap()
            if pixmap.loadFromData(athlete.photo_bytes):
                self.lbl_avatar.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.lbl_avatar.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 6px; background-color: white;")
            else:
                self.lbl_avatar.setText("👤")
        elif athlete.photo_path:
            import os
            from app.config import PROJECT_ROOT
            abs_path = PROJECT_ROOT / athlete.photo_path
            if abs_path.is_file():
                pixmap = QPixmap(str(abs_path))
                self.lbl_avatar.setPixmap(pixmap.scaled(70, 70, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                self.lbl_avatar.setStyleSheet("border: 1px solid #cbd5e1; border-radius: 6px; background-color: white;")
            else:
                self.lbl_avatar.setText("👤")
        else:
            self.lbl_avatar.setText("👤")
            self.lbl_avatar.setStyleSheet("font-size: 32px; border: 1px dashed #cbd5e1; border-radius: 6px; background-color: #f8fafc;")
            
        self._on_bmi_inputs_changed()
        self._update_overall_summary()

    def _clear_form(self):
        self.lbl_gender.setText("เพศ: —")
        self.lbl_age.setText("อายุ: —")
        self.lbl_group.setText("กลุ่ม: —")
        self.lbl_avatar.setText("👤")
        self.lbl_avatar.setStyleSheet("font-size: 32px; border: 1px dashed #cbd5e1; border-radius: 6px; background-color: #f8fafc;")
        
        self.txt_weight.clear()
        self.txt_height.clear()
        self.txt_pulse.clear()
        self.txt_bp_sys.clear()
        self.txt_bp_dia.clear()
        self.txt_fat_biceps.clear()
        self.txt_fat_triceps.clear()
        self.txt_fat_sub.clear()
        self.txt_fat_sup.clear()
        self.txt_strength_arm.clear()
        self.txt_strength_leg.clear()
        self.txt_flexibility.clear()
        self.txt_lung.clear()
        self.txt_pulse_test.clear()
        self.txt_load_weight.clear()
        
        self.lbl_bmi_val.setText("—")
        self.lbl_bmi_shape.setText("—")
        self.lbl_fat_val.setText("—")
        self.lbl_fat_grade.setText("ระดับ: —")
        self.lbl_fat_grade.setStyleSheet("color: #64748b;")
        self.lbl_fat_score.setText("คะแนน: —")
        
        self.lbl_cardio_val.setText("—")
        self.lbl_cardio_grade.setText("ระดับ: —")
        self.lbl_cardio_grade.setStyleSheet("color: #64748b;")
        self.lbl_cardio_score.setText("คะแนน: —")
        
        self.lbl_summary_score.setText("—")
        self.lbl_summary_grade.setText("—")
        
        self.current_fat_pct = None
        self.current_fat_res = None
        self.current_vo2max = None
        self.current_vo2_res = None

    def _on_bmi_inputs_changed(self):
        try:
            weight_str = self.txt_weight.text().strip()
            height_str = self.txt_height.text().strip()
            if not weight_str or not height_str:
                self.lbl_bmi_val.setText("—")
                self.lbl_bmi_shape.setText("—")
                return
            
            weight = float(weight_str)
            height = float(height_str)
            if weight <= 0 or height <= 0:
                self.lbl_bmi_val.setText("—")
                self.lbl_bmi_shape.setText("—")
                return
                
            bmi = weight / ((height / 100.0) ** 2)
            self.lbl_bmi_val.setText(f"{bmi:.2f}")
            
            # Asian BMI Standard range
            if bmi < 18.5:
                status = "น้ำหนักน้อย / ผอม"
                color = "#3498DB"
            elif bmi < 23.0:
                status = "ปกติ / สุขภาพดี"
                color = "#2ECC71"
            elif bmi < 25.0:
                status = "น้ำหนักเกิน"
                color = "#F1C40F"
            elif bmi < 30.0:
                status = "อ้วนระดับ 1"
                color = "#E67E22"
            else:
                status = "อ้วนระดับ 2 / อ้วนมาก"
                color = "#E74C3C"
                
            if self.rad_athlete.isChecked():
                status += " (นักกีฬา)"
                
            self.lbl_bmi_shape.setText(status)
            self.lbl_bmi_shape.setStyleSheet(f"font-size: 15px; font-weight: 700; color: {color};")
        except ValueError:
            self.lbl_bmi_val.setText("—")
            self.lbl_bmi_shape.setText("—")

    def _calculate_body_fat(self):
        athlete_id = self.cb_athlete.currentData()
        if not athlete_id:
            QMessageBox.warning(self, "เตือน", "กรุณาเลือกผู้ทดสอบก่อนคำนวณ")
            return
            
        athlete = self.athlete_service.get_athlete_by_id(athlete_id)
        if not athlete:
            return
            
        try:
            biceps = float(self.txt_fat_biceps.text() or 0)
            triceps = float(self.txt_fat_triceps.text() or 0)
            sub = float(self.txt_fat_sub.text() or 0)
            sup = float(self.txt_fat_sup.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "ข้อมูลไม่ถูกต้อง", "กรุณากรอกตัวเลขสำหรับความหนาผิวหนัง")
            return
            
        sum_skinfold = biceps + triceps + sub + sup
        if sum_skinfold <= 0:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกความหนาผิวหนังอย่างน้อยหนึ่งตำแหน่ง")
            return
            
        age = athlete.age
        gender = athlete.gender
        
        # Durnin & Womersley (1974) body density constants
        log_sum = math.log10(sum_skinfold)
        if gender == "Male":
            if age < 20:
                c, m = 1.1620, 0.0630
            elif age <= 29:
                c, m = 1.1631, 0.0632
            elif age <= 39:
                c, m = 1.1422, 0.0544
            elif age <= 49:
                c, m = 1.1620, 0.0700
            else:
                c, m = 1.1715, 0.0779
        else:
            if age < 20:
                c, m = 1.1549, 0.0678
            elif age <= 29:
                c, m = 1.1599, 0.0717
            elif age <= 39:
                c, m = 1.1423, 0.0632
            elif age <= 49:
                c, m = 1.1333, 0.0612
            else:
                c, m = 1.1339, 0.0645
                
        density = c - m * log_sum
        fat_pct = (4.95 / density - 4.50) * 100
        fat_pct = max(2.0, min(60.0, fat_pct))
        
        # Interpret
        fat_type = db_session.query(TestType).filter_by(name="Body Fat %").first()
        if fat_type:
            res = self.interpreter.interpret(athlete, fat_type, fat_pct)
            self.lbl_fat_val.setText(f"{fat_pct:.1f} %")
            self.lbl_fat_grade.setText(f"ระดับ: {res['grade']}")
            self.lbl_fat_grade.setStyleSheet(f"color: {res['color']}; font-weight: bold;")
            self.lbl_fat_score.setText(f"คะแนน: {res['score']} / 5")
            
            self.current_fat_pct = fat_pct
            self.current_fat_res = res
            self._update_overall_summary()
        else:
            self.lbl_fat_val.setText(f"{fat_pct:.1f} %")
            self.lbl_fat_grade.setText("ระดับ: ไม่พบเกณฑ์ประเมิน")
            self.lbl_fat_score.setText("คะแนน: —")
            self.current_fat_pct = fat_pct
            self.current_fat_res = {"grade": "—", "score": 0, "color": "#7F8C8D"}

    def _calculate_cardio(self):
        athlete_id = self.cb_athlete.currentData()
        if not athlete_id:
            QMessageBox.warning(self, "เตือน", "กรุณาเลือกผู้ทดสอบก่อนคำนวณ")
            return
            
        athlete = self.athlete_service.get_athlete_by_id(athlete_id)
        if not athlete:
            return
            
        try:
            pulse_test = float(self.txt_pulse_test.text() or 0)
            load_kp = float(self.txt_load_weight.text() or 0)
            weight = float(self.txt_weight.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "ข้อมูลไม่ถูกต้อง", "กรุณากรอกตัวเลขสำหรับ ชีพจรขณะทดสอบ, น้ำหนักถ่วง, และน้ำหนักตัว")
            return
            
        if weight <= 0:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกน้ำหนักตัวในส่วนข้อมูลทั่วไปก่อนคำนวณ")
            return
            
        if pulse_test <= 0 or load_kp <= 0:
            QMessageBox.warning(self, "ข้อมูลไม่ครบ", "กรุณากรอกชีพจรขณะทดสอบและน้ำหนักถ่วงก่อนคำนวณ")
            return
            
        # Work rate (kgm/min) = Load (kp) * 300
        work_rate = load_kp * 300
        
        # O2 Uptake
        if athlete.gender == "Male":
            vo2 = (0.00212 * work_rate) + 0.229
        else:
            vo2 = (0.00193 * work_rate) + 0.326
            
        age = athlete.age
        # Age factors (Astrand 1960)
        if age < 15:
            age_factor = 1.12
        elif age <= 24:
            age_factor = 1.00
        elif age <= 34:
            age_factor = 0.84
        elif age <= 44:
            age_factor = 0.77
        elif age <= 54:
            age_factor = 0.69
        elif age <= 64:
            age_factor = 0.64
        else:
            age_factor = 0.52
            
        # Nomogram calculations
        if athlete.gender == "Male":
            if pulse_test <= 61:
                QMessageBox.warning(self, "ข้อมูลไม่ถูกต้อง", "ชีพจรขณะทดสอบต่ำเกินไปสำหรับประเมินการทดสอบจักรยาน")
                return
            raw_vo2max = vo2 * ((220 - age - 61) / (pulse_test - 61))
        else:
            if pulse_test <= 72:
                QMessageBox.warning(self, "ข้อมูลไม่ถูกต้อง", "ชีพจรขณะทดสอบต่ำเกินไปสำหรับประเมินการทดสอบจักรยาน")
                return
            raw_vo2max = vo2 * ((220 - age - 72) / (pulse_test - 72))
            
        vo2max_corrected = raw_vo2max * age_factor
        relative_vo2max = (vo2max_corrected * 1000.0) / weight
        relative_vo2max = max(5.0, min(95.0, relative_vo2max))
        
        # Interpret
        vo2_type = db_session.query(TestType).filter_by(name="VO2max").first()
        if vo2_type:
            res = self.interpreter.interpret(athlete, vo2_type, relative_vo2max)
            self.lbl_cardio_val.setText(f"{relative_vo2max:.1f} mL/kg/min")
            self.lbl_cardio_grade.setText(f"ระดับ: {res['grade']}")
            self.lbl_cardio_grade.setStyleSheet(f"color: {res['color']}; font-weight: bold;")
            self.lbl_cardio_score.setText(f"คะแนน: {res['score']} / 5")
            
            self.current_vo2max = relative_vo2max
            self.current_vo2_res = res
            self._update_overall_summary()
        else:
            self.lbl_cardio_val.setText(f"{relative_vo2max:.1f} mL/kg/min")
            self.lbl_cardio_grade.setText("ระดับ: ไม่พบเกณฑ์ประเมิน")
            self.lbl_cardio_score.setText("คะแนน: —")
            self.current_vo2max = relative_vo2max
            self.current_vo2_res = {"grade": "—", "score": 0, "color": "#7F8C8D"}

    def _update_overall_summary(self):
        athlete_id = self.cb_athlete.currentData()
        if not athlete_id:
            return
        athlete = self.athlete_service.get_athlete_by_id(athlete_id)
        if not athlete:
            return
            
        scores = []
        
        # 1. Body Fat %
        if self.current_fat_res:
            scores.append(self.current_fat_res["score"])
            
        # 2. Hand Grip
        arm_val_str = self.txt_strength_arm.text().strip()
        if arm_val_str:
            try:
                val = float(arm_val_str)
                tt = db_session.query(TestType).filter_by(name="Hand Grip Strength").first()
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    scores.append(res["score"])
            except ValueError:
                pass
                
        # 3. Leg Strength
        leg_val_str = self.txt_strength_leg.text().strip()
        if leg_val_str:
            try:
                val = float(leg_val_str)
                tt = db_session.query(TestType).filter_by(name="Leg Strength").first()
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    scores.append(res["score"])
            except ValueError:
                pass
                
        # 4. Flexibility
        flex_val_str = self.txt_flexibility.text().strip()
        if flex_val_str:
            try:
                val = float(flex_val_str)
                tt = db_session.query(TestType).filter_by(name="Flexibility").first()
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    scores.append(res["score"])
            except ValueError:
                pass
                
        # 5. Lung Capacity
        lung_val_str = self.txt_lung.text().strip()
        if lung_val_str:
            try:
                val = float(lung_val_str) / 1000.0 # Convert mL to L
                tt = db_session.query(TestType).filter_by(name="Lung Capacity").first()
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    scores.append(res["score"])
            except ValueError:
                pass
                
        # 6. Cardio VO2max
        if self.current_vo2_res:
            scores.append(self.current_vo2_res["score"])
            
        if not scores:
            self.lbl_summary_score.setText("—")
            self.lbl_summary_grade.setText("—")
            return
            
        total_score = sum(scores)
        avg_score = total_score / len(scores)
        
        self.lbl_summary_score.setText(f"{total_score} คะแนน")
        
        if avg_score >= 4.5:
            grade_str = "ดีเลิศ (Excellent)"
            color = COL_GREEN
        elif avg_score >= 3.5:
            grade_str = "ดี (Good)"
            color = "#10B981"
        elif avg_score >= 2.5:
            grade_str = "ปานกลาง / พอใช้ (Average)"
            color = COL_ORANGE
        elif avg_score >= 1.5:
            grade_str = "ต่ำกว่าเกณฑ์ (Below Average)"
            color = "#E67E22"
        else:
            grade_str = "ควรปรับปรุงอย่างยิ่ง (Poor)"
            color = COL_RED
            
        self.lbl_summary_grade.setText(grade_str)
        self.lbl_summary_grade.setStyleSheet(f"font-size: 16px; font-weight: 700; color: {color};")

    def _on_save(self):
        athlete_id = self.cb_athlete.currentData()
        if not athlete_id:
            QMessageBox.warning(self, "เตือน", "กรุณาเลือกผู้เข้ารับการทดสอบก่อนทำการบันทึก")
            return
            
        athlete = self.athlete_service.get_athlete_by_id(athlete_id)
        if not athlete:
            return
            
        try:
            weight = float(self.txt_weight.text() or 0) if self.txt_weight.text() else None
            height = float(self.txt_height.text() or 0) if self.txt_height.text() else None
            resting_pulse = float(self.txt_pulse.text() or 0) if self.txt_pulse.text() else None
            bp_sys = float(self.txt_bp_sys.text() or 0) if self.txt_bp_sys.text() else None
            bp_dia = float(self.txt_bp_dia.text() or 0) if self.txt_bp_dia.text() else None
        except ValueError:
            QMessageBox.critical(self, "ข้อผิดพลาด", "ข้อมูลสัดส่วนร่างกาย/ชีพจร/ความดัน ต้องเป็นตัวเลขเท่านั้น")
            return
            
        test_date = date.today()
        
        def save_record(test_name, value, category, unit, grade=None):
            if value is None:
                return
            tt = get_or_create_test_type(db_session, test_name, unit, category)
            
            # Check if record already exists on the same day
            rec = db_session.query(TestRecord).filter_by(
                athlete_id=athlete_id,
                test_date=test_date,
                test_type_id=tt.id
            ).first()
            
            if rec:
                rec.value = value
                rec.interpreted_grade = grade
            else:
                rec = TestRecord(
                    athlete_id=athlete_id,
                    test_date=test_date,
                    test_type_id=tt.id,
                    value=value,
                    interpreted_grade=grade
                )
                db_session.add(rec)
                
        try:
            # 1. Save Pre-test indicators
            save_record("Weight", weight, "Composition", "kg")
            save_record("Height", height, "Composition", "cm")
            save_record("Resting Pulse", resting_pulse, "Cardiovascular", "bpm")
            if bp_sys is not None and bp_dia is not None:
                save_record("Blood Pressure Systolic", bp_sys, "Cardiovascular", "mmHg")
                save_record("Blood Pressure Diastolic", bp_dia, "Cardiovascular", "mmHg")
                
            # 2. Save BMI
            if weight and height:
                bmi = weight / ((height / 100.0) ** 2)
                grade = self.lbl_bmi_shape.text()
                save_record("BMI", bmi, "Composition", "kg/m²", grade)
                
            # 3. Save Body Fat %
            if self.current_fat_pct is not None:
                grade = self.current_fat_res["grade"] if self.current_fat_res else None
                save_record("Body Fat %", self.current_fat_pct, "Composition", "%", grade)
                
            # 4. Save Grip strength
            grip_str = self.txt_strength_arm.text().strip()
            if grip_str:
                val = float(grip_str)
                tt = db_session.query(TestType).filter_by(name="Hand Grip Strength").first()
                grade = None
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    grade = res["grade"]
                save_record("Hand Grip Strength", val, "Strength", "kg", grade)
                
            # 5. Save Leg strength
            leg_str = self.txt_strength_leg.text().strip()
            if leg_str:
                val = float(leg_str)
                tt = db_session.query(TestType).filter_by(name="Leg Strength").first()
                grade = None
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    grade = res["grade"]
                save_record("Leg Strength", val, "Strength", "kg", grade)
                
            # 6. Save Flexibility
            flex_str = self.txt_flexibility.text().strip()
            if flex_str:
                val = float(flex_str)
                tt = db_session.query(TestType).filter_by(name="Flexibility").first()
                grade = None
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    grade = res["grade"]
                save_record("Flexibility", val, "Flexibility", "cm", grade)
                
            # 7. Save Lung capacity
            lung_str = self.txt_lung.text().strip()
            if lung_str:
                val = float(lung_str) / 1000.0  # Convert to L
                tt = db_session.query(TestType).filter_by(name="Lung Capacity").first()
                grade = None
                if tt:
                    res = self.interpreter.interpret(athlete, tt, val)
                    grade = res["grade"]
                save_record("Lung Capacity", val, "Respiratory", "L", grade)
                
            # 8. Save VO2max
            if self.current_vo2max is not None:
                grade = self.current_vo2_res["grade"] if self.current_vo2_res else None
                save_record("VO2max", self.current_vo2max, "Cardiovascular", "mL/kg/min", grade)
                
            db_session.commit()
            QMessageBox.information(self, "สำเร็จ", f"บันทึกผลการทดสอบของ \"{athlete.full_name}\" เรียบร้อยแล้ว")
            self._clear_form()
            self._load_athletes()
            
        except Exception as e:
            db_session.rollback()
            QMessageBox.critical(self, "เกิดข้อผิดพลาด", f"ไม่สามารถบันทึกข้อมูลการทดสอบได้:\n{e}")

    # ── Reusable Component Styles ──
    def _card_style(self):
        return f"""
            QFrame {{
                background-color: {COL_BG_WHITE};
                border: 1px solid {COL_BORDER};
                border-radius: 8px;
            }}
            QLabel {{
                border: none;
                background: transparent;
                color: {COL_TEXT_BODY};
            }}
        """

    def _input_style(self):
        return f"""
            QLineEdit, QComboBox {{
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 6px 10px;
                font-size: 13px;
                background-color: {COL_BG_PRIMARY};
                color: {COL_TEXT_PRIMARY};
            }}
            QLineEdit:focus, QComboBox:focus {{
                border-color: {COL_ACCENT_BLUE};
                background-color: {COL_BG_WHITE};
            }}
        """

    def _btn_primary_style(self):
        return f"""
            QPushButton {{
                background-color: {COL_ACCENT_BLUE};
                color: white;
                border: none;
                border-radius: 6px;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: #1d4ed8;
            }}
        """

    def _btn_secondary_style(self):
        return f"""
            QPushButton {{
                background-color: {COL_BLUE_BG};
                color: {COL_ACCENT_BLUE};
                border: 1px solid {COL_BORDER};
                border-radius: 6px;
                padding: 6px 14px;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background-color: {COL_ACCENT_BLUE};
                color: white;
                border-color: {COL_ACCENT_BLUE};
            }}
        """
