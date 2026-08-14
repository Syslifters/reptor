import copy
from typing import Any, Dict, List, Set, Tuple, Union

DEFAULT_OBJECT_TYPE = "finding"
OBJECT_TYPES = ("finding", "note", "section")


def parse_remove_fields(fields_string: str) -> Tuple[Dict[str, List[str]], List[str]]:
    """Parse comma-separated field specs into a dict keyed by object type.

    Each entry is ``[type:]field``. Unprefixed names and ``:field`` both default
    to ``finding``. Split on the first colon so dotted paths work
    (e.g. ``finding:data.cvss``).

    Returns:
        A tuple of ``(exclude_by_type, warnings)``.
    """
    if not fields_string:
        return {}, []

    exclude_by_type: Dict[str, List[str]] = {}
    warnings: List[str] = []

    for raw in fields_string.split(","):
        spec = raw.strip()
        if not spec:
            warnings.append("Ignoring empty field name")
            continue

        if ":" in spec:
            object_type, _, field = spec.partition(":")
            object_type = object_type.strip() or DEFAULT_OBJECT_TYPE
            field = field.strip()
        else:
            object_type = DEFAULT_OBJECT_TYPE
            field = spec

        if not field:
            warnings.append(f"Ignoring empty field name for type '{object_type}'")
            continue

        if object_type not in OBJECT_TYPES:
            warnings.append(
                f"Ignoring unknown object type '{object_type}' in '{spec}'"
            )
            continue

        exclude_by_type.setdefault(object_type, []).append(field)

    return exclude_by_type, warnings


def format_remove_fields(exclude_by_type: Dict[str, List[str]]) -> str:
    """Format scoped exclude fields for logging."""
    parts: List[str] = []
    for object_type in OBJECT_TYPES:
        for field in exclude_by_type.get(object_type, []):
            parts.append(f"{object_type}:{field}")
    return ", ".join(parts)


class FieldExcluder:
    """Remove specified fields from finding/section/note data structures.

    Field lists are scoped per object type (``finding``, ``note``, ``section``).
    Call ``remove_fields(data, object_type=...)`` to apply only that type's list.

    Within a type, fields can be specified in two ways:

    - **Bare field name** (e.g. ``"cvss"``): removed *recursively* at every nesting
      level and inside every list item.
    - **Dotted path** (e.g. ``"data.cvss"``): removes the field only where that exact
      parent/child path exists. Dotted paths are also applied to objects nested inside
      list items.

    The original input is never mutated; a deep copy is returned.

    Note:
        ``remove_fields(None)`` returns an empty dict (``{}``), not ``None``. Callers
        that may pass ``None`` (e.g. a missing ``data`` field) should guard accordingly.
    """

    def __init__(
        self, exclude_fields: Union[List[str], Dict[str, List[str]]]
    ) -> None:
        if isinstance(exclude_fields, dict):
            self._exclude_by_type: Dict[str, Set[str]] = {
                object_type: set(fields)
                for object_type, fields in exclude_fields.items()
                if fields
            }
        else:
            self._exclude_by_type = (
                {DEFAULT_OBJECT_TYPE: set(exclude_fields)}
                if exclude_fields
                else {}
            )

    def remove_fields(
        self,
        data: Dict[str, Any],
        object_type: str = DEFAULT_OBJECT_TYPE,
    ) -> Dict[str, Any]:
        """Remove the configured fields for ``object_type`` from a data structure.

        Bare field names are removed recursively at every nesting level; dotted
        paths (e.g. ``"data.cvss"``) are removed only at their exact location. See
        the class docstring for the full semantics. Returns a deep copy; the input
        is not modified. ``None`` input yields ``{}``. If the type has no configured
        fields, returns a deep copy unchanged.
        """
        if data is None:
            return {}

        exclude_fields = self._exclude_by_type.get(object_type, set())
        result = copy.deepcopy(data)
        if not exclude_fields:
            return result

        self._remove_fields_from_dict(result, exclude_fields)
        return result

    def _remove_fields_from_dict(
        self, data: Dict[str, Any], exclude_fields: Set[str]
    ) -> None:
        if not isinstance(data, dict):
            return

        keys_to_remove = self._get_nested_keys_to_remove(data, exclude_fields)

        for key in keys_to_remove:
            if key in data:
                del data[key]

        for dot_key in keys_to_remove:
            if "." in dot_key:
                parts = dot_key.split(".")
                self._remove_from_nested_path(data, parts)

        for key, value in list(data.items()):
            if isinstance(value, dict):
                self._remove_fields_from_dict(value, exclude_fields)
            elif isinstance(value, list):
                self._process_array(value, exclude_fields)

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
            if key in data:
                del data[key]
        else:
            self._remove_from_nested_path(data[key], remaining_parts)

    def _get_nested_keys_to_remove(
        self, data: Dict[str, Any], exclude_fields: Set[str]
    ) -> List[str]:
        """Get all keys (including nested paths) that should be removed."""
        keys_to_remove: List[str] = []

        for key in exclude_fields:
            if key in data:
                keys_to_remove.append(key)

        for dot_key in exclude_fields:
            if "." in dot_key:
                parts = dot_key.split(".")
                current = data
                found = True

                for part in parts[:-1]:
                    if isinstance(current, dict) and part in current:
                        current = current[part]
                    else:
                        found = False
                        break

                if found:
                    last_part = parts[-1]
                    if isinstance(current, dict) and last_part in current:
                        if dot_key not in keys_to_remove:
                            keys_to_remove.append(dot_key)

        return keys_to_remove

    def _process_array(self, array: List[Any], exclude_fields: Set[str]) -> None:
        """Process an array by removing fields from each element if it's an object."""
        if not isinstance(array, list):
            return

        for item in array:
            if isinstance(item, dict):
                self._remove_fields_from_dict(item, exclude_fields)
            elif isinstance(item, list):
                self._process_array(item, exclude_fields)
