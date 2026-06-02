from app.models.athlete import Athlete
from app.models.test_type import TestType
from app.models.record import TestRecord
from app.models.standard import Standard, StandardRule

class InterpreterService:
    def __init__(self, db_session):
        self.session = db_session

    def interpret(self, athlete: Athlete, test_type: TestType, value: float) -> dict:
        """
        Evaluate a single score against the active standard for a given test type, 
        considering athlete age and gender.

        Returns:
            dict: {
                "grade": str (e.g., "Excellent"),
                "color": str (e.g., "#2ECC71"),
                "score": int (e.g., 5),
                "standard_name": str (e.g., "WHO Classifications")
            }
        """
        # Find active standard for this test type
        active_standard = (
            self.session.query(Standard)
            .filter(Standard.test_type_id == test_type.id, Standard.is_active == True)
            .first()
        )

        if not active_standard:
            return {
                "grade": "No Active Standard",
                "color": "#7F8C8D",
                "score": 0,
                "standard_name": "None"
            }

        age = athlete.age
        gender = athlete.gender

        # Get rules matching the athlete's gender (or 'All') and age range
        rules = (
            self.session.query(StandardRule)
            .filter(
                StandardRule.standard_id == active_standard.id,
                StandardRule.gender.in_([gender, "All"]),
                StandardRule.min_age <= age,
                StandardRule.max_age >= age
            )
            .all()
        )

        for rule in rules:
            # Check lower bound: if min_value is None, there is no lower limit
            min_ok = (rule.min_value is None) or (value >= rule.min_value)
            # Check upper bound: if max_value is None, there is no upper limit
            max_ok = (rule.max_value is None) or (value <= rule.max_value)

            if min_ok and max_ok:
                return {
                    "grade": rule.performance_level,
                    "color": rule.color_code,
                    "score": rule.score_points,
                    "standard_name": active_standard.name
                }

        # Fallback if demographic rules exist but the value is out of all defined bounds
        return {
            "grade": "Unclassified",
            "color": "#95A5A6",
            "score": 0,
            "standard_name": active_standard.name
        }

    def interpret_record(self, record: TestRecord) -> dict:
        """
        Evaluates a TestRecord, updates its cached interpreted_grade field, 
        and returns the evaluation metrics.
        """
        result = self.interpret(record.athlete, record.test_type, record.value)
        record.interpreted_grade = result["grade"]
        return result
