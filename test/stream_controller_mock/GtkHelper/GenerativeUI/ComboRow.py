class ComboRow:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self._widget = self

    def get_selected_item(self):
        pass

    def set_value(self):
        pass

    def _value_changed(self):
        pass

    def set_sensitive(self, _: bool) -> None:
        pass

    def get_item_amount(self) -> int:
        return len(self.args[3])

    def get_item_at(self, index: int):
        return self.args[3][index]

    @property
    def widget(self):
        return self._widget

    @widget.setter
    def widget(self, value):
        self._widget = value