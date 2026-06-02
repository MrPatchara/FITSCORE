import json
from sqlalchemy.orm import Session
from app.models.test_type import TestType
from app.models.standard import Standard, StandardRule

class StandardImportExportService:
    def __init__(self, db_session: Session):
        self.session = db_session

    def export_to_json(self, standard_id: int) -> str:
        """
        Exports a Standard and all its associated StandardRules to a JSON string.
        """
        standard = self.session.query(Standard).filter_by(id=standard_id).first()
        if not standard:
            raise ValueError(f"Standard with ID {standard_id} not found.")

        data = {
            "test_type_name": standard.test_type.name,
            "name": standard.name,
            "description": standard.description,
            "rules": [
                {
                    "gender": rule.gender,
                    "min_age": rule.min_age,
                    "max_age": rule.max_age,
                    "min_value": rule.min_value,
                    "max_value": rule.max_value,
                    "performance_level": rule.performance_level,
                    "color_code": rule.color_code,
                    "score_points": rule.score_points
                }
                for rule in standard.rules
            ]
        }
        return json.dumps(data, indent=4)

    def import_from_json(self, json_content: str, set_active: bool = False) -> Standard:
        """
        Imports a Standard and its rules from a JSON string.
        Resolves the TestType by name, creating a new Standard record.
        """
        data = json.loads(json_content)
        
        test_type_name = data.get("test_type_name")
        test_type = self.session.query(TestType).filter_by(name=test_type_name).first()
        if not test_type:
            raise ValueError(f"Test type '{test_type_name}' does not exist in the database. "
                             f"Please create the test type first.")

        # Create Standard
        new_standard = Standard(
            test_type_id=test_type.id,
            name=data.get("name"),
            description=data.get("description"),
            is_active=set_active
        )
        self.session.add(new_standard)
        self.session.commit()  # commit to get standard.id

        # If set active, deactivate other standards for this test type
        if set_active:
            self.session.query(Standard).filter(
                Standard.test_type_id == test_type.id,
                Standard.id != new_standard.id
            ).update({"is_active": False})

        # Add rules
        for rule_data in data.get("rules", []):
            rule = StandardRule(
                standard_id=new_standard.id,
                gender=rule_data.get("gender"),
                min_age=int(rule_data.get("min_age")),
                max_age=int(rule_data.get("max_age")),
                min_value=rule_data.get("min_value"),
                max_value=rule_data.get("max_value"),
                performance_level=rule_data.get("performance_level"),
                color_code=rule_data.get("color_code", "#7F8C8D"),
                score_points=int(rule_data.get("score_points", 0))
            )
            self.session.add(rule)
        
        self.session.commit()
        return new_standard
