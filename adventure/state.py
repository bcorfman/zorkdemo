class StateMachine:
    def __init__(self, **kwargs):
        self.states = kwargs['states'].copy()
        self.current_state = ''
        if kwargs['initial'] in self.states.keys():
            self.switch_state(kwargs['initial'])

    def switch_state(self, state):
        self.current_state = state
        self.states[state]()
