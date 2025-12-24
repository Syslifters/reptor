import copy
import hashlib
from typing import Dict, Any


class Anonymizer:
    def __init__(self):
        self.mappings: Dict[str, Dict[str, Any]] = {}

    def _get_project_map(self, project_id: str) -> Dict[str, Any]:
        if project_id not in self.mappings:
            self.mappings[project_id] = {
                "real_to_mock": {},
                "mock_to_real": {},
            }
        return self.mappings[project_id]

    def _generate_mock(self, project_id: str, original: str) -> str:
        """Generate a deterministic mock value using hash."""
        hash_input = f"{project_id}:{original}"
        hash_digest = hashlib.sha256(hash_input.encode()).hexdigest()[:8]
        return f"REDACTED_{hash_digest}"

    def anonymize(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Replaces sensitive fields in data with masked values.
        Returns a new dictionary with modifications.
        """
        if "affected_components" not in data or not data["affected_components"]:
            return data

        new_data = copy.deepcopy(data)
        project_map = self._get_project_map(project_id)
        
        new_components = []
        for component in new_data["affected_components"]:
            # Check if we already have a mock for this component
            if component in project_map["real_to_mock"]:
                mock = project_map["real_to_mock"][component]
            else:
                mock = self._generate_mock(project_id, component)
                project_map["real_to_mock"][component] = mock
                project_map["mock_to_real"][mock] = component

            new_components.append(mock)
        
        new_data["affected_components"] = new_components
        return new_data

    def deanonymize(self, project_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Restores sensitive fields in data from masked values.
        Returns a new dictionary with modifications.
        """
        if "affected_components" not in data or not data["affected_components"]:
            return data

        if project_id not in self.mappings:
            return data

        new_data = copy.deepcopy(data)
        project_map = self.mappings[project_id]
        
        restored_components = []
        for component in new_data["affected_components"]:
            if component in project_map["mock_to_real"]:
                restored_components.append(project_map["mock_to_real"][component])
            else:
                restored_components.append(component)
        
        new_data["affected_components"] = restored_components
        return new_data
