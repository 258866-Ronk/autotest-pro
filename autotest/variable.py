"""Variable context with ${name} substitution and parent inheritance."""
import re
from typing import Any, Dict, Optional

PATTERN = re.compile(r"\$\{([^}]+)\}")


class VariableContext:
    def __init__(self, initial: Optional[Dict[str, Any]] = None, parent: "VariableContext" = None):
        self.values: Dict[str, Any] = dict(initial or {})
        self.parent = parent

    def child(self) -> "VariableContext":
        return VariableContext(parent=self)

    def get(self, key: str) -> Optional[Any]:
        key = key.strip()
        if key in self.values:
            return self.values[key]
        if self.parent is not None:
            return self.parent.get(key)
        return None

    def set(self, key: str, value: Any) -> None:
        self.values[key] = value

    def render(self, text: Any) -> Any:
        """Replace ${name} placeholders. Unknown vars are kept untouched."""
        if not isinstance(text, str):
            return text

        def repl(match):
            key = match.group(1).strip()
            value = self.get(key)
            return match.group(0) if value is None else str(value)

        return PATTERN.sub(repl, text)

    def render_obj(self, obj):
        if isinstance(obj, str):
            return self.render(obj)
        if isinstance(obj, dict):
            return {k: self.render_obj(v) for k, v in obj.items()}
        if isinstance(obj, list):
            return [self.render_obj(v) for v in obj]
        return obj

    @staticmethod
    def has_var(*parts) -> bool:
        for part in parts:
            if isinstance(part, str) and PATTERN.search(part):
                return True
            if isinstance(part, dict) and any(PATTERN.search(str(v)) for v in part.values()):
                return True
        return False
