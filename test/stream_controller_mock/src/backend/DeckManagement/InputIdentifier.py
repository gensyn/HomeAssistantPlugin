class Input:
    class Key:
        class Events:
            DOWN = "Key Down"
            UP = "Key Up"
            SHORT_UP = "Key Short Up"
            HOLD_START = "Key Hold Start"
            HOLD_STOP = "Key Hold Stop"

    class Dial:
        class Events:
            DOWN = "Dial Down"
            UP = "Dial Up"
            SHORT_UP = "Dial Short Up"
            HOLD_START = "Dial Hold Start"
            HOLD_STOP = "Dial Hold Stop"
            TURN_CW = "Dial Turn CW"
            TURN_CCW = "Dial Turn CCW"
            SHORT_TOUCH_PRESS = "Dial Touchscreen Short Press"
            LONG_TOUCH_PRESS = "Dial Touchscreen Long Press"

    class Touchscreen:
        class Events:
            DRAG_LEFT = "Touchscreen Drag Left"
            DRAG_RIGHT = "Touchscreen Drag Right"
