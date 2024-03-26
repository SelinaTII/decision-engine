import asyncio

class UseCaseBase:
    def __init__(self):
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    async def notify_listeners(self, data):
        for listener in self.listeners:
            await listener.notify(data)