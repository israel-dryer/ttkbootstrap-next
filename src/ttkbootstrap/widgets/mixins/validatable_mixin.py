from typing import Any, Callable, Unpack
from ttkbootstrap.events import Event, event_handler
from ttkbootstrap.validation.types import RuleTriggerType, RuleType, ValidationOptions
from ttkbootstrap.validation.rules import ValidationRule


class ValidationMixin:
    """
    Mixin to add validation support to signal-bound widgets.

    Provides a declarative interface to register validation rules
    and trigger validation based on user interaction events such as
    key input, focus loss, or manual checks.

    Expected to be used with widgets that implement:
    - `value() -> Any`     # RAW/MODEL VALUE (not necessarily a string)
    - `bind(event, callback)`
    - `emit(event, data=...)`
    """

    # NOTE: value() returns the raw/model value (str, float, date, None, etc.)
    value: Callable[[], Any]
    emit: Callable[..., None]
    bind: Callable[[str, Callable], str]

    def __init__(self, *args, **kwargs):
        """Initialize the validation mixin."""
        self._rules: list[ValidationRule] = []
        super().__init__(*args, **kwargs)
        self._setup_validation_events()

    @event_handler(Event.INVALID)
    def on_invalid(self, handler: Callable = None):
        """Bind or get the <<Invalid>> event handler"""
        ...

    @event_handler(Event.VALID)
    def on_valid(self, handler: Callable = None):
        """Bind or get the <<Valid>> event handler"""
        ...

    @event_handler(Event.VALIDATED)
    def on_validated(self, handler: Callable = None):
        """Bind or get the <<Validated>> event handler"""
        ...

    def _setup_validation_events(self):
        """Bind 'keyup' and 'blur' events to automatic validation checks."""
        self.bind(Event.KEYUP, lambda _: self.validate(self.value(), "key"))
        self.bind(Event.BLUR, lambda _: self.validate(self.value(), "blur"))

    def add_validation_rule(self, rule_type: RuleType, **kwargs: Unpack[ValidationOptions]):
        """Add a single validation rule."""
        self._rules.append(ValidationRule(rule_type, **kwargs))
        return self

    def add_validation_rules(self, rules: list[ValidationRule]):
        """Set the full list of validation rules, replacing any existing ones."""
        self._rules = rules
        return self

    def validate(self, value: Any, trigger: RuleTriggerType = "manual") -> bool:
        """
        Run validation rules against a *raw/model* value.

        The rule itself is responsible for interpreting the value's type.
        For example, a 'required' rule may treat `None` as invalid and any
        non-empty string/number/date as valid.
        """
        ran_rule = False
        data = {"value": value, "is_valid": True, "message": ""}

        for rule in self._rules:
            if trigger != "manual" and rule.trigger not in ("always", trigger):
                continue

            ran_rule = True
            result = rule.validate(value)  # value is raw/model (Any)
            data.update(message=result.message, is_valid=result.is_valid)

            if not result.is_valid:
                self.emit(Event.INVALID, data=data)
                self.emit(Event.VALIDATED, data=data)
                return False

        if ran_rule:
            self.emit(Event.VALID, data=data)
            self.emit(Event.VALIDATED, data=data)

        return ran_rule
