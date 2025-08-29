from typing import Any, Callable, Optional, Unpack
from ttkbootstrap.events import Event
from ttkbootstrap.validation.types import RuleTriggerType, RuleType, ValidationOptions
from ttkbootstrap.validation.rules import ValidationRule


class ValidatableMixin:
    """
    Mixin to add validation support to signal-bound widgets.

    Provides a declarative interface to register validation rules
    and trigger validation based on user interaction events such as
    key input, focus loss, or manual checks.

    Expected to be used with widgets that implement:
    - `value() -> str`
    - `bind(event, callback)`
    - `emit(event, data=...)`
    """

    value: Callable[[], str]
    emit: Callable[..., None]
    bind: Callable[[str, Callable], str]

    def __init__(self):
        """Initialize the validation mixin."""
        self._rules: list[ValidationRule] = []
        self._on_validated: Optional[Callable[[Any], Any]] = None
        self._on_invalid: Optional[Callable[[Any], Any]] = None
        self._on_valid: Optional[Callable[[Any], Any]] = None

    def _setup_validation_events(self):
        """Bind 'keyup' and 'blur' events to automatic validation checks."""
        self.bind(Event.KEYUP, lambda _: self.validate(self.value(), "key"))
        self.bind(Event.BLUR, lambda _: self.validate(self.value(), "blur"))

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Unpack[ValidationOptions]):
        """
        Add a single validation rule.

        Args:
            rule_type: Type of rule, e.g., "required", "regex".
            **kwargs: Rule options like trigger, message, pattern.

        Returns:
            self (chainable)
        """
        self._rules.append(ValidationRule(rule_type, **kwargs))
        return self

    def add_validation_rules(self, rules: list[ValidationRule]):
        """
        Set the full list of validation rules, replacing any existing ones.

        Args:
            rules: List of ValidationRule instances.

        Returns:
            self (chainable)
        """
        self._rules = rules
        return self

    def on_invalid(self, handler: Callable[[Any], Any] = None):
        """
        Bind a handler for the 'invalid' event.

        Args:
            handler: Callback to run when validation fails.

        Returns:
            Getter or self (chainable)
        """
        if handler is None:
            return self._on_invalid
        self._on_invalid = handler
        self.bind("invalid", self._on_invalid)
        return self

    def on_valid(self, handler: Callable[[Any], Any] = None):
        """
        Bind a handler for the 'valid' event.

        Args:
            handler: Callback to run when validation fails.

        Returns:
            Getter or self (chainable)
        """
        if handler is None:
            return self._on_valid
        self._on_valid = handler
        self.bind("valid", self._on_valid)
        return self

    def on_validated(self, handler: Callable[[Any], Any] = None):
        """
        Bind a handler for the 'validated' event.

        Args:
            handler: Callback to run after any validation attempt.

        Returns:
            Getter or self (chainable)
        """
        if handler is None:
            return self._on_validated
        self._on_validated = handler
        self.bind(Event.VALIDATED, self._on_validated)
        return self

    def validate(self, value: str, trigger: RuleTriggerType = "manual") -> bool:
        """
        Run validation rules against a value.

        Args:
            value: The string value to validate.
            trigger: One of "key", "blur", or "manual".

        Returns:
            True if rules were run and passed, False if any failed.
        """
        ran_rule = False
        data = {"value": value, "is_valid": True, "message": ""}

        for rule in self._rules:
            if trigger != "manual" and rule.trigger not in ("always", trigger):
                continue

            ran_rule = True
            result = rule.validate(value)
            data.update(message=result.message, is_valid=result.is_valid)

            if not result.is_valid:
                self.emit(Event.INVALID, data=data)
                self.emit(Event.VALIDATED, data=data)
                return False

        if ran_rule:
            self.emit(Event.VALID, data=data)
            self.emit(Event.VALIDATED, data=data)

        return ran_rule
