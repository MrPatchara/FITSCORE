import pytest
from datetime import date, datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models.athlete import Group, Athlete
from app.models.test_type import TestType
from app.models.record import TestRecord
from app.models.standard import Standard, StandardRule
from app.services.interpreter import InterpreterService
from app.services.importer import StandardImportExportService

@pytest.fixture
def db_session():
    """
    Creates an in-memory SQLite database and yields a session.
    """
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(bind=engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    try:
        yield session
    finally:
        session.close()

def test_athlete_age_calculation(db_session):
    # Test age calculation properties
    ath = Athlete(
        first_name="Test",
        last_name="User",
        gender="Male",
        date_of_birth=date(date.today().year - 20, 1, 1) # 20 years old
    )
    db_session.add(ath)
    db_session.commit()
    
    assert ath.age == 20
    assert ath.full_name == "Test User"

def test_interpreter_bmi(db_session):
    # Set up BMI test type
    bmi_test = TestType(name="BMI", unit="kg/m²", category="Composition", is_lower_better=True)
    db_session.add(bmi_test)
    db_session.commit()
    
    # Set up standard and rules
    bmi_standard = Standard(test_type_id=bmi_test.id, name="WHO Classifications", is_active=True)
    db_session.add(bmi_standard)
    db_session.commit()
    
    rules = [
        StandardRule(standard_id=bmi_standard.id, gender="All", min_age=0, max_age=120, min_value=None, max_value=18.49, performance_level="Underweight", color_code="#3498DB", score_points=2),
        StandardRule(standard_id=bmi_standard.id, gender="All", min_age=0, max_age=120, min_value=18.5, max_value=24.99, performance_level="Normal", color_code="#2ECC71", score_points=5),
        StandardRule(standard_id=bmi_standard.id, gender="All", min_age=0, max_age=120, min_value=25.0, max_value=29.99, performance_level="Overweight", color_code="#F1C40F", score_points=3),
        StandardRule(standard_id=bmi_standard.id, gender="All", min_age=0, max_age=120, min_value=30.0, max_value=None, performance_level="Obese", color_code="#E74C3C", score_points=1)
    ]
    db_session.add_all(rules)
    db_session.commit()
    
    # Setup Athlete
    ath = Athlete(first_name="Alice", last_name="Smith", gender="Female", date_of_birth=date(1990, 5, 12))
    db_session.add(ath)
    db_session.commit()
    
    interpreter = InterpreterService(db_session)
    
    # Evaluate various BMIs
    res_under = interpreter.interpret(ath, bmi_test, 17.5)
    assert res_under["grade"] == "Underweight"
    assert res_under["score"] == 2
    
    res_normal = interpreter.interpret(ath, bmi_test, 22.0)
    assert res_normal["grade"] == "Normal"
    assert res_normal["score"] == 5
    
    res_over = interpreter.interpret(ath, bmi_test, 27.2)
    assert res_over["grade"] == "Overweight"
    assert res_over["score"] == 3
    
    res_obese = interpreter.interpret(ath, bmi_test, 32.5)
    assert res_obese["grade"] == "Obese"
    assert res_obese["score"] == 1

def test_interpreter_demographics(db_session):
    # Test VO2max gender/age division matching
    vo2_test = TestType(name="VO2max", unit="mL/kg/min", category="Cardiovascular")
    db_session.add(vo2_test)
    db_session.commit()
    
    vo2_standard = Standard(test_type_id=vo2_test.id, name="Cardio Standards", is_active=True)
    db_session.add(vo2_standard)
    db_session.commit()
    
    rules = [
        # Male 18-35
        StandardRule(standard_id=vo2_standard.id, gender="Male", min_age=18, max_age=35, min_value=50.0, max_value=None, performance_level="Excellent", color_code="#2ECC71", score_points=5),
        StandardRule(standard_id=vo2_standard.id, gender="Male", min_age=18, max_age=35, min_value=None, max_value=49.9, performance_level="Poor", color_code="#E74C3C", score_points=1),
        # Female 18-35
        StandardRule(standard_id=vo2_standard.id, gender="Female", min_age=18, max_age=35, min_value=45.0, max_value=None, performance_level="Excellent", color_code="#2ECC71", score_points=5),
        StandardRule(standard_id=vo2_standard.id, gender="Female", min_age=18, max_age=35, min_value=None, max_value=44.9, performance_level="Poor", color_code="#E74C3C", score_points=1)
    ]
    db_session.add_all(rules)
    db_session.commit()
    
    interpreter = InterpreterService(db_session)
    
    # 25 year old male
    male_athlete = Athlete(first_name="Male", last_name="User", gender="Male", date_of_birth=date(date.today().year - 25, 1, 1))
    db_session.add(male_athlete)
    
    # 25 year old female
    female_athlete = Athlete(first_name="Female", last_name="User", gender="Female", date_of_birth=date(date.today().year - 25, 1, 1))
    db_session.add(female_athlete)
    db_session.commit()
    
    # Score 47.0
    res_m = interpreter.interpret(male_athlete, vo2_test, 47.0)
    res_f = interpreter.interpret(female_athlete, vo2_test, 47.0)
    
    assert res_m["grade"] == "Poor"
    assert res_f["grade"] == "Excellent"

def test_importer_exporter(db_session):
    # Setup standard and rules to export
    tt = TestType(name="Grip", unit="kg", category="Strength")
    db_session.add(tt)
    db_session.commit()
    
    std = Standard(test_type_id=tt.id, name="Grip Norms", description="Adult grip norms")
    db_session.add(std)
    db_session.commit()
    
    rule = StandardRule(standard_id=std.id, gender="Male", min_age=20, max_age=30, min_value=45.0, max_value=60.0, performance_level="Normal", color_code="#CCCCCC", score_points=3)
    db_session.add(rule)
    db_session.commit()
    
    importer = StandardImportExportService(db_session)
    exported_json = importer.export_to_json(std.id)
    
    # Delete the standard
    db_session.delete(std)
    db_session.commit()
    
    # Re-import it
    imported_std = importer.import_from_json(exported_json, set_active=True)
    
    assert imported_std.name == "Grip Norms"
    assert len(imported_std.rules) == 1
    assert imported_std.rules[0].performance_level == "Normal"
    assert imported_std.is_active == True
