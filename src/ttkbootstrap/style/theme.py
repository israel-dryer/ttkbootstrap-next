import json
import importlib.resources as resources


def load_json(filename: str, package: str = "ttkbootstrap.assets.themes") -> dict:
    """
    Load a JSON file from the given package using importlib.resources.

    Args:
        filename (str): Name of the JSON file, e.g. 'Fluent2AzureLightTokens.json'
        package (str): Dot-path to the package containing the file, default is 'assets'

    Returns:
        dict: Parsed JSON data.
    """
    with resources.files(package).joinpath(filename).open("r", encoding="utf-8") as f:
        return json.load(f)


class ColorTheme:
    def __init__(self, tokens: dict):
        self.tokens = tokens

    def get(self, name: str) -> str:
        return self.tokens.get(name, "#000000")

    @property
    def background(self) -> str:
        return self.tokens.get('background', '#000000')

    @property
    def calendar_background(self) -> str:
        return self.tokens.get('calendarBackground', '#000000')

    @property
    def calendar_button_border(self) -> str:
        return self.tokens.get('calendarButtonBorder', '#000000')

    @property
    def calendar_button_hover(self) -> str:
        return self.tokens.get('calendarButtonHover', '#000000')

    @property
    def calendar_button_selected(self) -> str:
        return self.tokens.get('calendarButtonSelected', '#000000')

    @property
    def calendar_text_disabled(self) -> str:
        return self.tokens.get('calendarTextDisabled', '#000000')

    @property
    def calendar_text_hover(self) -> str:
        return self.tokens.get('calendarTextHover', '#000000')

    @property
    def calendar_text_outside(self) -> str:
        return self.tokens.get('calendarTextOutside', '#000000')

    @property
    def calendar_text_rest(self) -> str:
        return self.tokens.get('calendarTextRest', '#000000')

    @property
    def check_box_checked_background(self) -> str:
        return self.tokens.get('checkBoxCheckedBackground', '#000000')

    @property
    def check_box_checked_border(self) -> str:
        return self.tokens.get('checkBoxCheckedBorder', '#000000')

    @property
    def check_box_checked_default(self) -> str:
        return self.tokens.get('checkBoxCheckedDefault', '#000000')

    @property
    def check_box_checked_hover_background(self) -> str:
        return self.tokens.get('checkBoxCheckedHoverBackground', '#000000')

    @property
    def check_box_checked_hover_border(self) -> str:
        return self.tokens.get('checkBoxCheckedHoverBorder', '#000000')

    @property
    def check_box_disabled_background(self) -> str:
        return self.tokens.get('checkBoxDisabledBackground', '#000000')

    @property
    def check_box_disabled_border(self) -> str:
        return self.tokens.get('checkBoxDisabledBorder', '#000000')

    @property
    def check_box_indeterminate_circle_background(self) -> str:
        return self.tokens.get('checkBoxIndeterminateCircleBackground', '#000000')

    @property
    def check_box_indeterminate_circle_hover_background(self) -> str:
        return self.tokens.get('checkBoxIndeterminateCircleHoverBackground', '#000000')

    @property
    def check_box_rest_background(self) -> str:
        return self.tokens.get('checkBoxRestBackground', '#000000')

    @property
    def check_box_rest_border(self) -> str:
        return self.tokens.get('checkBoxRestBorder', '#000000')

    @property
    def check_box_rest_check(self) -> str:
        return self.tokens.get('checkBoxRestCheck', '#000000')

    @property
    def check_box_rest_focus(self) -> str:
        return self.tokens.get('checkBoxRestFocus', '#000000')

    @property
    def check_box_rest_hover(self) -> str:
        return self.tokens.get('checkBoxRestHover', '#000000')

    @property
    def check_box_rest_hover_text(self) -> str:
        return self.tokens.get('checkBoxRestHoverText', '#000000')

    @property
    def choice_group_circle_hover(self) -> str:
        return self.tokens.get('choiceGroupCircleHover', '#000000')

    @property
    def choice_group_focus(self) -> str:
        return self.tokens.get('choiceGroupFocus', '#000000')

    @property
    def command_bar_border(self) -> str:
        return self.tokens.get('commandBarBorder', '#000000')

    @property
    def command_bar_button_disabled_color(self) -> str:
        return self.tokens.get('commandBarButtonDisabledColor', '#000000')

    @property
    def command_bar_button_focus_border_color(self) -> str:
        return self.tokens.get('commandBarButtonFocusBorderColor', '#000000')

    @property
    def command_bar_button_hover_background(self) -> str:
        return self.tokens.get('commandBarButtonHoverBackground', '#000000')

    @property
    def command_bar_button_hover_color(self) -> str:
        return self.tokens.get('commandBarButtonHoverColor', '#000000')

    @property
    def command_bar_button_hover_icon(self) -> str:
        return self.tokens.get('commandBarButtonHoverIcon', '#000000')

    @property
    def command_bar_button_root_color(self) -> str:
        return self.tokens.get('commandBarButtonRootColor', '#000000')

    @property
    def command_bar_button_selected_background(self) -> str:
        return self.tokens.get('commandBarButtonSelectedBackground', '#000000')

    @property
    def command_bar_button_selected_icon(self) -> str:
        return self.tokens.get('commandBarButtonSelectedIcon', '#000000')

    @property
    def command_bar_button_selected_hover_background(self) -> str:
        return self.tokens.get('commandBarButtonSelectedHoverBackground', '#000000')

    @property
    def control_outlines_accent(self) -> str:
        return self.tokens.get('controlOutlinesAccent', '#000000')

    @property
    def control_outlines_background(self) -> str:
        return self.tokens.get('controlOutlinesBackground', '#000000')

    @property
    def control_outlines_dirty(self) -> str:
        return self.tokens.get('controlOutlinesDirty', '#000000')

    @property
    def control_outlines_disabled(self) -> str:
        return self.tokens.get('controlOutlinesDisabled', '#000000')

    @property
    def control_outlines_error(self) -> str:
        return self.tokens.get('controlOutlinesError', '#000000')

    @property
    def control_outlines_focus(self) -> str:
        return self.tokens.get('controlOutlinesFocus', '#000000')

    @property
    def control_outlines_hover(self) -> str:
        return self.tokens.get('controlOutlinesHover', '#000000')

    @property
    def control_outlines_rest(self) -> str:
        return self.tokens.get('controlOutlinesRest', '#000000')

    @property
    def danger_button_hover_background(self) -> str:
        return self.tokens.get('dangerButtonHoverBackground', '#000000')

    @property
    def danger_button_hover_border(self) -> str:
        return self.tokens.get('dangerButtonHoverBorder', '#000000')

    @property
    def danger_button_hover_text(self) -> str:
        return self.tokens.get('dangerButtonHoverText', '#000000')

    @property
    def danger_button_pressed_background(self) -> str:
        return self.tokens.get('dangerButtonPressedBackground', '#000000')

    @property
    def danger_button_pressed_border(self) -> str:
        return self.tokens.get('dangerButtonPressedBorder', '#000000')

    @property
    def danger_button_pressed_text(self) -> str:
        return self.tokens.get('dangerButtonPressedText', '#000000')

    @property
    def danger_button_rest_background(self) -> str:
        return self.tokens.get('dangerButtonRestBackground', '#000000')

    @property
    def danger_button_rest_border(self) -> str:
        return self.tokens.get('dangerButtonRestBorder', '#000000')

    @property
    def danger_button_rest_text(self) -> str:
        return self.tokens.get('dangerButtonRestText', '#000000')

    @property
    def data_color_data_color1(self) -> str:
        return self.tokens.get('dataColorDataColor1', '#000000')

    @property
    def data_color_data_color10(self) -> str:
        return self.tokens.get('dataColorDataColor10', '#000000')

    @property
    def data_color_data_color2(self) -> str:
        return self.tokens.get('dataColorDataColor2', '#000000')

    @property
    def data_color_data_color3(self) -> str:
        return self.tokens.get('dataColorDataColor3', '#000000')

    @property
    def data_color_data_color4(self) -> str:
        return self.tokens.get('dataColorDataColor4', '#000000')

    @property
    def data_color_data_color5(self) -> str:
        return self.tokens.get('dataColorDataColor5', '#000000')

    @property
    def data_color_data_color6(self) -> str:
        return self.tokens.get('dataColorDataColor6', '#000000')

    @property
    def data_color_data_color7(self) -> str:
        return self.tokens.get('dataColorDataColor7', '#000000')

    @property
    def data_color_data_color8(self) -> str:
        return self.tokens.get('dataColorDataColor8', '#000000')

    @property
    def data_color_data_color9(self) -> str:
        return self.tokens.get('dataColorDataColor9', '#000000')

    @property
    def data_color_nodata1(self) -> str:
        return self.tokens.get('dataColorNodata1', '#000000')

    @property
    def data_color_nodata2(self) -> str:
        return self.tokens.get('dataColorNodata2', '#000000')

    @property
    def date_picker_disabled_border(self) -> str:
        return self.tokens.get('datePickerDisabledBorder', '#000000')

    @property
    def date_picker_rest_selected(self) -> str:
        return self.tokens.get('datePickerRestSelected', '#000000')

    @property
    def date_picker_rest_text(self) -> str:
        return self.tokens.get('datePickerRestText', '#000000')

    @property
    def details_row_border(self) -> str:
        return self.tokens.get('detailsRowBorder', '#000000')

    @property
    def details_row_focus(self) -> str:
        return self.tokens.get('detailsRowFocus', '#000000')

    @property
    def details_row_hovered_background(self) -> str:
        return self.tokens.get('detailsRowHoveredBackground', '#000000')

    @property
    def details_row_hovered_link(self) -> str:
        return self.tokens.get('detailsRowHoveredLink', '#000000')

    @property
    def details_row_hovered_row_link(self) -> str:
        return self.tokens.get('detailsRowHoveredRowLink', '#000000')

    @property
    def details_row_selected_hovered_link(self) -> str:
        return self.tokens.get('detailsRowSelectedHoveredLink', '#000000')

    @property
    def details_row_selected_link(self) -> str:
        return self.tokens.get('detailsRowSelectedLink', '#000000')

    @property
    def disabled_button_background(self) -> str:
        return self.tokens.get('disabledButtonBackground', '#000000')

    @property
    def disabled_button_text(self) -> str:
        return self.tokens.get('disabledButtonText', '#000000')

    @property
    def drop_down_background_hover(self) -> str:
        return self.tokens.get('dropDownBackgroundHover', '#000000')

    @property
    def drop_down_background_rest(self) -> str:
        return self.tokens.get('dropDownBackgroundRest', '#000000')

    @property
    def drop_down_text_hovered(self) -> str:
        return self.tokens.get('dropDownTextHovered', '#000000')

    @property
    def item_hover(self) -> str:
        return self.tokens.get('itemHover', '#000000')

    @property
    def item_select(self) -> str:
        return self.tokens.get('itemSelect', '#000000')

    @property
    def item_select_hovered(self) -> str:
        return self.tokens.get('itemSelectHovered', '#000000')

    @property
    def primary_button_disabled_background(self) -> str:
        return self.tokens.get('primaryButtonDisabledBackground', '#000000')

    @property
    def primary_button_disabled_border(self) -> str:
        return self.tokens.get('primaryButtonDisabledBorder', '#000000')

    @property
    def primary_button_disabled_text(self) -> str:
        return self.tokens.get('primaryButtonDisabledText', '#000000')

    @property
    def primary_button_focus_text(self) -> str:
        return self.tokens.get('primaryButtonFocusText', '#000000')

    @property
    def primary_button_hover_background(self) -> str:
        return self.tokens.get('primaryButtonHoverBackground', '#000000')

    @property
    def primary_button_hover_text(self) -> str:
        return self.tokens.get('primaryButtonHoverText', '#000000')

    @property
    def primary_button_pressed_background(self) -> str:
        return self.tokens.get('primaryButtonPressedBackground', '#000000')

    @property
    def primary_button_pressed_text(self) -> str:
        return self.tokens.get('primaryButtonPressedText', '#000000')

    @property
    def primary_button_rest_background(self) -> str:
        return self.tokens.get('primaryButtonRestBackground', '#000000')

    @property
    def primary_button_rest_border(self) -> str:
        return self.tokens.get('primaryButtonRestBorder', '#000000')

    @property
    def primary_button_rest_text(self) -> str:
        return self.tokens.get('primaryButtonRestText', '#000000')

    @property
    def radio_button_circle_border_disabled(self) -> str:
        return self.tokens.get('radioButtonCircleBorderDisabled', '#000000')

    @property
    def radio_button_circle_checked_disabled(self) -> str:
        return self.tokens.get('radioButtonCircleCheckedDisabled', '#000000')

    @property
    def radio_button_circle_unchecked_rest(self) -> str:
        return self.tokens.get('radioButtonCircleUncheckedRest', '#000000')

    @property
    def radio_button_pill_checked_hover(self) -> str:
        return self.tokens.get('radioButtonPillCheckedHover', '#000000')

    @property
    def radio_button_pill_disabled(self) -> str:
        return self.tokens.get('radioButtonPillDisabled', '#000000')

    @property
    def radio_button_pill_unchecked_disabled(self) -> str:
        return self.tokens.get('radioButtonPillUncheckedDisabled', '#000000')

    @property
    def radio_button_pill_unchecked_hover(self) -> str:
        return self.tokens.get('radioButtonPillUncheckedHover', '#000000')

    @property
    def secondary_button_focus_border(self) -> str:
        return self.tokens.get('secondaryButtonFocusBorder', '#000000')

    @property
    def secondary_button_hover_background(self) -> str:
        return self.tokens.get('secondaryButtonHoverBackground', '#000000')

    @property
    def secondary_button_hover_border(self) -> str:
        return self.tokens.get('secondaryButtonHoverBorder', '#000000')

    @property
    def secondary_button_hover_color(self) -> str:
        return self.tokens.get('secondaryButtonHoverColor', '#000000')

    @property
    def secondary_button_pressed_background(self) -> str:
        return self.tokens.get('secondaryButtonPressedBackground', '#000000')

    @property
    def secondary_button_pressed_border(self) -> str:
        return self.tokens.get('secondaryButtonPressedBorder', '#000000')

    @property
    def secondary_button_pressed_text(self) -> str:
        return self.tokens.get('secondaryButtonPressedText', '#000000')

    @property
    def secondary_button_rest_background(self) -> str:
        return self.tokens.get('secondaryButtonRestBackground', '#000000')

    @property
    def secondary_button_rest_border(self) -> str:
        return self.tokens.get('secondaryButtonRestBorder', '#000000')

    @property
    def secondary_button_rest_text(self) -> str:
        return self.tokens.get('secondaryButtonRestText', '#000000')

    @property
    def shimmer_primary(self) -> str:
        return self.tokens.get('shimmerPrimary', '#000000')

    @property
    def shimmer_secondary(self) -> str:
        return self.tokens.get('shimmerSecondary', '#000000')

    @property
    def slider_active_background(self) -> str:
        return self.tokens.get('sliderActiveBackground', '#000000')

    @property
    def slider_active_background_hovered(self) -> str:
        return self.tokens.get('sliderActiveBackgroundHovered', '#000000')

    @property
    def slider_active_background_pressed(self) -> str:
        return self.tokens.get('sliderActiveBackgroundPressed', '#000000')

    @property
    def slider_active_disabled_background(self) -> str:
        return self.tokens.get('sliderActiveDisabledBackground', '#000000')

    @property
    def slider_inactive_background_hovered(self) -> str:
        return self.tokens.get('sliderInactiveBackgroundHovered', '#000000')

    @property
    def slider_inactive_disabled_background(self) -> str:
        return self.tokens.get('sliderInactiveDisabledBackground', '#000000')

    @property
    def status_bar_background_error(self) -> str:
        return self.tokens.get('statusBarBackgroundError', '#000000')

    @property
    def status_bar_background_information(self) -> str:
        return self.tokens.get('statusBarBackgroundInformation', '#000000')

    @property
    def status_bar_background_success(self) -> str:
        return self.tokens.get('statusBarBackgroundSuccess', '#000000')

    @property
    def status_bar_background_upsell(self) -> str:
        return self.tokens.get('statusBarBackgroundUpsell', '#000000')

    @property
    def status_bar_background_warning(self) -> str:
        return self.tokens.get('statusBarBackgroundWarning', '#000000')

    @property
    def status_bar_border_default(self) -> str:
        return self.tokens.get('statusBarBorderDefault', '#000000')

    @property
    def status_bar_border_error(self) -> str:
        return self.tokens.get('statusBarBorderError', '#000000')

    @property
    def status_bar_border_information(self) -> str:
        return self.tokens.get('statusBarBorderInformation', '#000000')

    @property
    def status_bar_border_okay(self) -> str:
        return self.tokens.get('statusBarBorderOkay', '#000000')

    @property
    def status_bar_border_upsell(self) -> str:
        return self.tokens.get('statusBarBorderUpsell', '#000000')

    @property
    def status_bar_border_warning(self) -> str:
        return self.tokens.get('statusBarBorderWarning', '#000000')

    @property
    def status_bar_icon_disabled(self) -> str:
        return self.tokens.get('statusBarIconDisabled', '#000000')

    @property
    def status_bar_icon_error(self) -> str:
        return self.tokens.get('statusBarIconError', '#000000')

    @property
    def status_bar_icon_information(self) -> str:
        return self.tokens.get('statusBarIconInformation', '#000000')

    @property
    def status_bar_icon_success(self) -> str:
        return self.tokens.get('statusBarIconSuccess', '#000000')

    @property
    def status_bar_icon_upsell(self) -> str:
        return self.tokens.get('statusBarIconUpsell', '#000000')

    @property
    def status_bar_icon_warning(self) -> str:
        return self.tokens.get('statusBarIconWarning', '#000000')

    @property
    def status_bar_link_hover(self) -> str:
        return self.tokens.get('statusBarLinkHover', '#000000')

    @property
    def status_bar_link_rest(self) -> str:
        return self.tokens.get('statusBarLinkRest', '#000000')

    @property
    def tabs_hover(self) -> str:
        return self.tokens.get('tabsHover', '#000000')

    @property
    def tag_button_hover_background(self) -> str:
        return self.tokens.get('tagButtonHoverBackground', '#000000')

    @property
    def tag_button_hover_border(self) -> str:
        return self.tokens.get('tagButtonHoverBorder', '#000000')

    @property
    def tag_button_hover_text(self) -> str:
        return self.tokens.get('tagButtonHoverText', '#000000')

    @property
    def tag_button_pressed_background(self) -> str:
        return self.tokens.get('tagButtonPressedBackground', '#000000')

    @property
    def tag_button_pressed_border(self) -> str:
        return self.tokens.get('tagButtonPressedBorder', '#000000')

    @property
    def tag_button_pressed_text(self) -> str:
        return self.tokens.get('tagButtonPressedText', '#000000')

    @property
    def tag_button_rest_background(self) -> str:
        return self.tokens.get('tagButtonRestBackground', '#000000')

    @property
    def tag_button_rest_border(self) -> str:
        return self.tokens.get('tagButtonRestBorder', '#000000')

    @property
    def tag_button_rest_text(self) -> str:
        return self.tokens.get('tagButtonRestText', '#000000')

    @property
    def teaching_bubble_hover_primary_button_background(self) -> str:
        return self.tokens.get('teachingBubbleHoverPrimaryButtonBackground', '#000000')

    @property
    def teaching_bubble_rest_background(self) -> str:
        return self.tokens.get('teachingBubbleRestBackground', '#000000')

    @property
    def teaching_bubble_rest_border(self) -> str:
        return self.tokens.get('teachingBubbleRestBorder', '#000000')

    @property
    def teaching_bubble_rest_secondary_background(self) -> str:
        return self.tokens.get('teachingBubbleRestSecondaryBackground', '#000000')

    @property
    def teaching_bubble_rest_text(self) -> str:
        return self.tokens.get('teachingBubbleRestText', '#000000')

    @property
    def text_body(self) -> str:
        return self.tokens.get('textBody', '#000000')

    @property
    def text_body_hovered(self) -> str:
        return self.tokens.get('textBodyHovered', '#000000')

    @property
    def text_disabled(self) -> str:
        return self.tokens.get('textDisabled', '#000000')

    @property
    def text_error(self) -> str:
        return self.tokens.get('textError', '#000000')

    @property
    def text_heading(self) -> str:
        return self.tokens.get('textHeading', '#000000')

    @property
    def text_hyperlink(self) -> str:
        return self.tokens.get('textHyperlink', '#000000')

    @property
    def text_hyperlink_hovered(self) -> str:
        return self.tokens.get('textHyperlink_hovered', '#000000')

    @property
    def text_icon(self) -> str:
        return self.tokens.get('textIcon', '#000000')

    @property
    def text_label(self) -> str:
        return self.tokens.get('textLabel', '#000000')

    @property
    def text_list(self) -> str:
        return self.tokens.get('textList', '#000000')

    @property
    def text_placeholder(self) -> str:
        return self.tokens.get('textPlaceholder', '#000000')

    @property
    def text_success(self) -> str:
        return self.tokens.get('textSuccess', '#000000')

    @property
    def text_value(self) -> str:
        return self.tokens.get('textValue', '#000000')

    @property
    def toggle_disabled_background(self) -> str:
        return self.tokens.get('toggleDisabledBackground', '#000000')



# Example
theme = ColorTheme(load_json("Fluent2AzureLightTokens.json"))
bg = theme.primary_button_hover_background

print(bg)
print(theme)
