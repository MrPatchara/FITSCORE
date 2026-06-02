from datetime import date
from app.models.athlete import Group, Athlete
from app.models.test_type import TestType
from app.models.standard import Standard, StandardRule
from app.core.db import db_session, init_db

def seed_data(session):
    """
    Seeds the SQLite database with default test types, sample groups, 
    sample athletes, and standard interpretation scales.
    """
    # 1. Default Groups
    team_vanguard = session.query(Group).filter_by(name="Vanguard Team").first()
    if not team_vanguard:
        team_vanguard = Group(name="Vanguard Team", description="Elite performance tracking cohort.")
        session.add(team_vanguard)
        session.commit()

    team_scholars = session.query(Group).filter_by(name="Scholars Academy").first()
    if not team_scholars:
        team_scholars = Group(name="Scholars Academy", description="Youth physical education class.")
        session.add(team_scholars)
        session.commit()

    # 2. Default Test Types
    default_tests = [
        {"name": "Body Fat %", "unit": "%", "category": "Composition", "description": "Bioelectrical impedance or caliper body fat percentage.", "is_lower_better": True},
        {"name": "BMI", "unit": "kg/m²", "category": "Composition", "description": "Body Mass Index.", "is_lower_better": True},
        {"name": "Hand Grip Strength", "unit": "kg", "category": "Strength", "description": "Hand dynamometer grip strength.", "is_lower_better": False},
        {"name": "Leg Strength", "unit": "kg", "category": "Strength", "description": "Isometric leg dynamometer pull strength.", "is_lower_better": False},
        {"name": "Flexibility", "unit": "cm", "category": "Flexibility", "description": "Standard sit and reach flexibility test.", "is_lower_better": False},
        {"name": "Lung Capacity", "unit": "L", "category": "Respiratory", "description": "Forced vital lung capacity via spirometer.", "is_lower_better": False},
        {"name": "VO2max", "unit": "mL/kg/min", "category": "Cardiovascular", "description": "Estimated maximum rate of oxygen consumption.", "is_lower_better": False},
        {"name": "Push Up", "unit": "reps", "category": "Strength", "description": "Maximum consecutive push ups completed with proper form.", "is_lower_better": False},
        {"name": "Sit Up", "unit": "reps", "category": "Strength", "description": "Maximum sit ups completed in 60 seconds.", "is_lower_better": False},
        {"name": "12-Min Run Test", "unit": "m", "category": "Cardiovascular", "description": "Cooper 12-minute run fitness test.", "is_lower_better": False},
        {"name": "100m Sprint", "unit": "sec", "category": "Speed", "description": "Timed 100-meter track sprint.", "is_lower_better": True}
    ]

    test_type_objects = {}
    for test in default_tests:
        tt = session.query(TestType).filter_by(name=test["name"]).first()
        if not tt:
            tt = TestType(**test)
            session.add(tt)
            session.commit()
        test_type_objects[test["name"]] = tt

    # 3. Sample Athletes
    sample_athletes = [
        {"first_name": "Alice", "last_name": "Smith", "gender": "Female", "date_of_birth": date(1998, 5, 12), "group_id": team_vanguard.id, "notes": "Track athlete athlete."},
        {"first_name": "Bob", "last_name": "Jones", "gender": "Male", "date_of_birth": date(1995, 10, 22), "group_id": team_vanguard.id, "notes": "No health conditions noted."},
        {"first_name": "Charlie", "last_name": "Brown", "gender": "Male", "date_of_birth": date(2012, 3, 15), "group_id": team_scholars.id, "notes": "Junior program participant."}
    ]

    for athlete_data in sample_athletes:
        ath = session.query(Athlete).filter_by(first_name=athlete_data["first_name"], last_name=athlete_data["last_name"]).first()
        if not ath:
            ath = Athlete(**athlete_data)
            session.add(ath)
            session.commit()

    # 4. Standard Rules Seeding (World Health Organization BMI Standards)
    bmi_test = test_type_objects["BMI"]
    bmi_standard = session.query(Standard).filter_by(test_type_id=bmi_test.id, name="WHO Classifications").first()
    if not bmi_standard:
        bmi_standard = Standard(test_type_id=bmi_test.id, name="WHO Classifications", description="World Health Organization BMI range designations.", is_active=True)
        session.add(bmi_standard)
        session.commit()

        # BMI Ranges for ALL ages & genders
        bmi_rules = [
            {"gender": "All", "min_age": 0, "max_age": 120, "min_value": None, "max_value": 18.49, "performance_level": "Underweight", "color_code": "#3498DB", "score_points": 2},
            {"gender": "All", "min_age": 0, "max_age": 120, "min_value": 18.5, "max_value": 24.99, "performance_level": "Normal", "color_code": "#2ECC71", "score_points": 5},
            {"gender": "All", "min_age": 0, "max_age": 120, "min_value": 25.0, "max_value": 29.99, "performance_level": "Overweight", "color_code": "#F1C40F", "score_points": 3},
            {"gender": "All", "min_age": 0, "max_age": 120, "min_value": 30.0, "max_value": None, "performance_level": "Obese", "color_code": "#E74C3C", "score_points": 1}
        ]
        for rule in bmi_rules:
            r = StandardRule(standard_id=bmi_standard.id, **rule)
            session.add(r)
        session.commit()

    # 5. Standard Rules Seeding (Generic Adult VO2max Standard - ACSM-like snippet)
    vo2max_test = test_type_objects["VO2max"]
    vo2max_standard = session.query(Standard).filter_by(test_type_id=vo2max_test.id, name="General Adult Norms").first()
    if not vo2max_standard:
        vo2max_standard = Standard(test_type_id=vo2max_test.id, name="General Adult Norms", description="Standard cardiovascular fitness levels for adults aged 18-35.", is_active=True)
        session.add(vo2max_standard)
        session.commit()

        # VO2max Ranges: Males aged 18-35
        vo2_male_rules = [
            {"gender": "Male", "min_age": 18, "max_age": 35, "min_value": 52.0, "max_value": None, "performance_level": "Excellent", "color_code": "#2ECC71", "score_points": 5},
            {"gender": "Male", "min_age": 18, "max_age": 35, "min_value": 44.0, "max_value": 51.9, "performance_level": "Good", "color_code": "#27AE60", "score_points": 4},
            {"gender": "Male", "min_age": 18, "max_age": 35, "min_value": 36.0, "max_value": 43.9, "performance_level": "Average", "color_code": "#F1C40F", "score_points": 3},
            {"gender": "Male", "min_age": 18, "max_age": 35, "min_value": 30.0, "max_value": 35.9, "performance_level": "Below Average", "color_code": "#E67E22", "score_points": 2},
            {"gender": "Male", "min_age": 18, "max_age": 35, "min_value": None, "max_value": 29.9, "performance_level": "Poor", "color_code": "#E74C3C", "score_points": 1}
        ]

        # VO2max Ranges: Females aged 18-35
        vo2_female_rules = [
            {"gender": "Female", "min_age": 18, "max_age": 35, "min_value": 48.0, "max_value": None, "performance_level": "Excellent", "color_code": "#2ECC71", "score_points": 5},
            {"gender": "Female", "min_age": 18, "max_age": 35, "min_value": 39.0, "max_value": 47.9, "performance_level": "Good", "color_code": "#27AE60", "score_points": 4},
            {"gender": "Female", "min_age": 18, "max_age": 35, "min_value": 31.0, "max_value": 38.9, "performance_level": "Average", "color_code": "#F1C40F", "score_points": 3},
            {"gender": "Female", "min_age": 18, "max_age": 35, "min_value": 26.0, "max_value": 30.9, "performance_level": "Below Average", "color_code": "#E67E22", "score_points": 2},
            {"gender": "Female", "min_age": 18, "max_age": 35, "min_value": None, "max_value": 25.9, "performance_level": "Poor", "color_code": "#E74C3C", "score_points": 1}
        ]

        for rule in vo2_male_rules + vo2_female_rules:
            r = StandardRule(standard_id=vo2max_standard.id, **rule)
            session.add(r)
        session.commit()

if __name__ == "__main__":
    init_db()
    seed_data(db_session)
    print("Database successfully seeded with default test types and standards.")
