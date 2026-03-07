from unittest.mock import Mock


class ActionCore:

    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.plugin_base = Mock()
        self.plugin_base.locale_manager = Mock()
        self.plugin_base.backend = Mock()
        self.plugin_base.backend.get_entities = Mock()
        self.plugin_base.add_action_ready_callback = Mock()
        self.plugin_base.remove_action_ready_callback = Mock()
        self.plugin_base.add_tracked_entity = Mock()
        self.plugin_base.remove_tracked_entity = Mock()
        pass

    def add_event_assigner(self, event_assigner):
        pass

    def get_input(self):
        raise AttributeError("get_input not available in mock")
