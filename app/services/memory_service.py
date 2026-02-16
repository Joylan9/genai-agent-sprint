class MemoryService:
    def __init__(self, max_messages=6):
        self.max_messages = max_messages
        self.history = []

    def add_message(self, role, content):
        self.history.append({"role": role, "content": content})

        # Keep only last N messages
        if len(self.history) > self.max_messages:
            self.history = self.history[-self.max_messages:]

    def get_history(self):
        return self.history
