import sys
import os
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import Qt
from app.core.db import init_db, db_session
from app.core.seed import seed_data
from app.models.test_type import TestType
from app.views.main_window import MainWindow

def main():
    # ── High DPI Scaling Configuration (Support 125%, 150% without distortion) ──
    os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "1"
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    # 1. Initialize database and schemas
    init_db()
    
    # 2. Auto-seed if database is empty
    try:
        if db_session.query(TestType).count() == 0:
            print("No test types found in database. Seeding default data...")
            seed_data(db_session)
            print("Database seeding completed.")
    except Exception as e:
        print(f"Error during database check/seeding: {e}")
    finally:
        db_session.remove()

    # 3. Launch PySide6 GUI Application
    app = QApplication(sys.argv)
    
    # Set global styling hints if needed
    app.setStyle("Fusion")
    
    window = MainWindow()
    window.showMaximized()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
