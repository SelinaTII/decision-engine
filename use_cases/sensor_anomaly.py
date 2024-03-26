import asyncio
import random
from .use_case_base import UseCaseBase

class SensorAnomalyProvider(UseCaseBase):
    def __init__(self, interval=2):
        super().__init__()
        self.interval = interval  # Interval between checks in seconds

    async def start(self):
        while True:
            await asyncio.sleep(self.interval)
            confidence = random.random()  # Generate a random confidence level between 0 and 1
            
            # Prepare the data with the confidence factor
            data = {
                "use_case": "sensor_anomaly",
                "confidence": confidence,  # Directly provide the confidence level
                "detail": "Confidence level of anomaly detection."
            }

            await self.notify_listeners(data)