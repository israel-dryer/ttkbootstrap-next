import re
from typing import Callable, Literal, Optional, TypedDict

RuleType = Literal["required", "email", "pattern", "stringLength", "custom", "compare"]
RuleTriggerType = Literal['key', 'blur', 'always', 'manual']


class ValidationOptions(TypedDict, total=False):
    pattern: str
    message: str
    min: int
    max: int
    trigger: Optional[Literal["key", "blur", "always", "manual"]]
    func: Callable[[str], bool]


class ValidationResult:
    def __init__(self, is_valid: bool, message: str = ""):
        self.is_valid = is_valid
        self.message = message


class ValidationRule:
    def __init__(
            self,
            rule_type: RuleType,
            message: str = "",
            **kwargs
    ):
        self.type = rule_type
        self.message = message
        self.trigger = kwargs.pop('trigger', self._default_trigger())
        self.params = kwargs

    def validate(self, value: str) -> ValidationResult:
        msg = self.message or self._default_message()

        if self.type == "required":
            if not value.strip():
                return ValidationResult(False, msg)
        elif self.type == "email":
            if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
                return ValidationResult(False, msg)
        elif self.type == "stringLength":
            min_len = self.params.get("min", 0)
            max_len = self.params.get("max", float("inf"))
            if not (min_len <= len(value) <= max_len):
                return ValidationResult(False, msg)
        elif self.type == "pattern":
            pattern = self.params.get("pattern", "")
            if not re.match(pattern, value):
                return ValidationResult(False, msg)
        elif self.type == "custom":
            func: Callable[[str], bool] = self.params.get("func")
            if func and not func(value):
                return ValidationResult(False, msg)

        return ValidationResult(True)

    def _default_message(self) -> str:
        if self.type == "required":
            return "This field is required."
        elif self.type == "email":
            return "Enter a valid email address."
        elif self.type == "stringLength":
            min_len = self.params.get("min", 0)
            max_len = self.params.get("max", None)
            if max_len is None or max_len == float("inf"):
                return f"Enter at least {min_len} characters."
            return f"Enter between {min_len} and {max_len} characters."
        elif self.type == "pattern":
            return "Value does not match the required pattern."
        elif self.type == "custom":
            return "Invalid value."
        return "Invalid input."

    def _default_trigger(self) -> RuleTriggerType:
        if self.type in {"required", "stringLength"}:
            return "blur"
        elif self.type in {"email", "pattern"}:
            return "always"
        elif self.type in {"custom"}:
            return "manual"
        return "blur"
