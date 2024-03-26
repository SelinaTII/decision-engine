import asyncio
from .use_case_base import UseCaseBase

class BatteryStatusProvider(UseCaseBase):
    def __init__(self, start_percent=100.0, step=-5.0, interval=2):
        self.battery_percent = start_percent
        self.step = step
        self.interval = interval
        self.listeners = []

    def add_listener(self, listener):
        self.listeners.append(listener)

    async def start(self):
        while 0 <= self.battery_percent <= 100:
            await asyncio.sleep(self.interval)
            self.battery_percent += self.step
            # print(f"Simulated battery level: {self.battery_percent}%")
            for listener in self.listeners:
                await listener.notify({"use_case": "battery_status", "percent": self.battery_percent})
            if self.battery_percent <= 0 or self.battery_percent >= 100:
                self.step = -self.step  # Reverse the direction of battery change