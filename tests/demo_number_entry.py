from ttkbootstrap import App, NumericEntry, Pack

with App("Number Entry Demo") as app:
    with Pack(padding=16, gap=8, fill_items="x"):
        # Basic float with inferred precision from increment
        NumericEntry(
            0.25,
            "Basic (inferred from increment)",
            increment=1.01,
            min_value=0.0,
            max_value=100.0,
            show_spin_buttons=False,
        )

        # Fixed decimals (2) – formats on commit, steps at 0.01
        NumericEntry(
            12.3,
            "FixedPoint (2 decimals)",
            value_format={"type": "fixedPoint", "precision": 2},
            increment=0.01,
            min_value=0,
            max_value=1000,
        )

        # Decimal with thousands separator, 3 decimals (custom pattern)
        NumericEntry(
            1234.567,
            "Decimal with grouping (3)",
            value_format={"type": "custom", "pattern": "#,##0.000"},
            increment=0.001,
            min_value=0,
            max_value=1000000,
        )

        # Percent – show 25% for 0.25; keep 1 decimal
        NumericEntry(
            0.25,
            "Percent (1 decimal)",
            value_format={"type": "percent", "precision": 1},
            increment=0.01,
            min_value=0,
            max_value=1,
        )

        # Currency – USD with 2 decimals
        NumericEntry(
            1234.56,
            "Currency (USD)",
            value_format={"type": "currency", "currency": "USD", "precision": 2},
            increment=0.01,
            min_value=0,
            max_value=1000000,
        )

        # Currency (more locales)
        NumericEntry(
            1234.56,
            "Currency (EUR, de_DE)",
            value_format={"type": "currency", "currency": "EUR", "precision": 2},
            increment=0.01,
            min_value=0,
            max_value=1000000,
            locale="de_DE",
        )

        NumericEntry(
            1234.56,
            "Currency (EUR, fr_FR)",
            value_format={"type": "currency", "currency": "EUR", "precision": 2},
            increment=0.01,
            min_value=0,
            max_value=1000000,
            locale="fr_FR",
        )

        NumericEntry(
            1234.56,
            "Currency (JPY, ja_JP)",
            value_format={"type": "currency", "currency": "JPY", "precision": 0},
            increment=1,
            min_value=0,
            max_value=1000000,
            locale="ja_JP",
        )

        # Scientific / exponential
        NumericEntry(
            0.0001234,
            "Exponential",
            value_format={"type": "exponential"},
            increment=0.0000001,
            min_value=0,
            max_value=1,
        )

        # Large number suffixing (auto K/M/B/T)
        NumericEntry(
            1_542_000,
            "Large Number (suffix)",
            value_format={"type": "largeNumber", "precision": 2},
            increment=100000,
            min_value=0,
            max_value=10_000_000_000,
        )

        # Thousands short form
        NumericEntry(
            15_500,
            "Thousands (K)",
            value_format={"type": "thousands", "precision": 1},
            increment=100,
            min_value=0,
            max_value=1_000_000,
        )

app.run()
