from typing import Any, Optional, Self, Unpack

from ttkbootstrap.core.base_widget import BaseWidget
from ttkbootstrap.events import Event
from ttkbootstrap.interop.runtime.binding import Stream
from ttkbootstrap.types import EventHandler
from ttkbootstrap.validation.rules import ValidationRule
from ttkbootstrap.validation.types import RuleTriggerType, RuleType, ValidationOptions


class ValidationMixin(BaseWidget):
    """
    Mixin to add validation support to signal-bound widgets.

    Provides a declarative interface to register validation rules
    and trigger validation based on user interaction events such as
    key input, focus loss, or manual checks.
    """

    # NOTE: value() returns the raw/model value (str, float, date, None, etc.)
    # value: Callable
    # emit: Callable
    # on: Callable

    def __init__(self, *args, **kwargs):
        """Initialize the validation mixin."""
        self._rules: list[ValidationRule] = []
        super().__init__(*args, **kwargs)
        self._setup_validation_events()

    def on_invalid(
            self,
            handler: Optional[EventHandler],
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Invalid>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.INVALID, scope=scope)
        if handler:
            return stream
        stream.listen(handler)
        return self

    def on_valid(
            self,
            handler: Optional[EventHandler],
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Valid>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.VALID, scope=scope)
        if handler:
            return stream
        stream.listen(handler)
        return self

    def on_validated(
            self,
            handler: Optional[EventHandler],
            *, scope="widget") -> Stream[Any] | Self:
        """Stream or chainable binding for <<Validated>>

        - If `handler` is provided → bind immediately and return self (chainable).
        - If no handler → return the Stream for Rx-style composition.
        """
        stream = self.on(Event.VALIDATED, scope=scope)
        if handler:
            return stream
        stream.listen(handler)
        return self

    def _setup_validation_events(self):
        """Bind 'keyup' and 'blur' events to automatic validation checks."""
        self.on(Event.KEYUP).debounce(50).listen(lambda _: self.validate(self.value(), "key"))
        self.on(Event.BLUR).debounce(50).listen(lambda _: self.validate(self.value(), "blur"))

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
                self.emit(Event.INVALID, **data)
                self.emit(Event.VALIDATED, **data)
                return False

        if ran_rule:
            self.emit(Event.VALID, **data)
            self.emit(Event.VALIDATED, **data)

        return ran_rule
