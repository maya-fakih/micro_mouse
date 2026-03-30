class ButtonEventHandler:
    def __init__(self):
        self.callbacks = {
            1: self._default,
            2: self._default,
            3: self._default,
            4: self._default,
            5: self._default,
            6: self._default,
        }
    
    def register_callback(self, button_num, callback):
        if 1 <= button_num <= 6:
            self.callbacks[button_num] = callback
    
    def handle_click(self, button_num, *args, **kwargs):
        if button_num in self.callbacks:
            self.callbacks[button_num](*args, **kwargs)
    
    def _default(self, *args, **kwargs):
        pass