import copy
from typing import Any, Dict, List, Set


class FieldExcluder:
    """Remove specified fields from finding/section/note data structures.

    This class provides functionality to exclude specific fields from data before
    sending it to an LLM. Fields can be specified in two ways, with different scopes:

    - **Bare field name** (e.g. ``"cvss"``): removed *recursively* at every nesting
      level and inside every list item. This is a blunt instrument: excluding
      ``"title"`` strips ``title`` from the top-level object *and* from any nested
      object field that happens to have a ``title`` sub-key. Prefer a dotted path
      when you only mean a specific location.
    - **Dotted path** (e.g. ``"data.cvss"``): removes the field only where that exact
      parent/child path exists, leaving identically-named keys elsewhere untouched.
      Dotted paths are also applied to objects nested inside list items.

    The original input is never mutated; a deep copy is returned.

    Note:
        ``remove_fields(None)`` returns an empty dict (``{}``), not ``None``. Callers
        that may pass ``None`` (e.g. a missing ``data`` field) should guard accordingly.
    """

    def __init__(self, exclude_fields: List[str]):
        self._exclude_fields: Set[str] = exclude_fields

    def remove_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Remove the configured fields from a data structure.

        Bare field names are removed recursively at every nesting level; dotted
        paths (e.g. ``"data.cvss"``) are removed only at their exact location. See
        the class docstring for the full semantics. Returns a deep copy; the input
        is not modified. ``None`` input yields ``{}``.
        """
        if data is None:
            return {}

        result = copy.deepcopy(data)
        self._remove_fields_from_dict(result)

        return result

    def _remove_fields_from_dict(self, data: Dict[str, Any]) -> None:
        if not isinstance(data, dict):
            return

        keys_to_remove = self._get_nested_keys_to_remove(data)

        # Remove top-level fields first
        for key in keys_to_remove:
            if key in data:
                del data[key]

        # Remove nested paths
        for dot_key in keys_to_remove:
            if "." in dot_key:
                parts = dot_key.split(".")
                self._remove_from_nested_path(data, parts)

        for key, value in list(data.items()):
            if isinstance(value, dict):
                self._remove_fields_from_dict(value)
            elif isinstance(value, list):
                self._process_array(value)

    def _remove_from_nested_path(self, data: Dict[str, Any], parts: List[str]) -> None:
        """Remove a field from a nested path.

        This method traverses the nested structure and removes the target field.
        If a parent path doesn't exist, it's left unchanged.
        """
        if not data or not parts:
            return

        key = parts[0]
        remaining_parts = parts[1:]

        if not isinstance(data, dict):
            return

        if key not in data:
            return

        if len(remaining_parts) == 0:
            # This is the final part - the field to remove
            if key in data:
                del data[key]
        else:
            # Continue traversing to the parent
            self._remove_from_nested_path(data[key], remaining_parts)

    def _get_nested_keys_to_remove(self, data: Dict[str, Any]) -> List[str]:
        """Get all keys (including nested paths) that should be removed.

        This method collects:
        - Top-level keys to remove
        - Nested paths to remove (e.g., "data.cvss")
        """

        keys_to_remove = []

        # Check for direct matches at this level
        for key in self._exclude_fields:
            if key in data:
                keys_to_remove.append(key)

        # Also check for nested paths by splitting on dots
        for dot_key in self._exclude_fields:
            if "." in dot_key:
                parts = dot_key.split(".")
                current = data
                found = True

                # Navigate to the parent of the nested field
                for part in parts[:-1]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        found = False
                        break

                if found:
                    # We're at the parent, check if the last part exists as a key
                    last_part = parts[-1]
                    if isinstance(current, dict) and last_part in current:
                        # Need to add the full path, not just the last part
                        if dot_key not in keys_to_remove:
                            keys_to_remove.append(dot_key)

        return keys_to_remove

    def _process_array(self, array: List[Any]) -> None:
        """Process an array by removing fields from each element if it's an object.
        """
        if not isinstance(array, list):
            return

        for item in array:
            if isinstance(item, dict):
                self._remove_fields_from_dict(item)
            elif isinstance(item, list):
                self._process_array(item)
