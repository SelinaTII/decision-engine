import asyncio
from experta import *

from custom_logger import CustomLogger
logger_instance = CustomLogger("drone_actions")

# Define facts
class BatteryStatus(Fact):
    """
    Represents the current battery status with the remaining battery percentage.
    """
    percent = Field(float, mandatory=True)

class SensorAnomalyStatus(Fact):
    """
    Represents the sensor anomaly status with a confidence level of anomaly detection.
    The confidence level ranges from 0.0 to 1.0.
    """
    confidence = Field(float, mandatory=True)

class BatteryState(Fact):
    """
    Represents the battery state as a numeric value and description.
    This can be normal, mild, severe, or critical, represented numerically from 0 to 3.
    """
    state_value = Field(int, mandatory=True)
    state_description = Field(str, mandatory=True)

class SensorAnomalyState(Fact):
    """
    Represents the sensor anomaly state as a numeric value and description.
    Similar to BatteryState, this can range from normal (0) to critical (3) based on the anomaly's severity.
    """
    state_value = Field(int, mandatory=True)
    state_description = Field(str, mandatory=True)

class OverallState(Fact):
    """
    Represents the overall state of the drone, determined by the highest severity level
    among BatteryState and SensorAnomalyState.
    """
    state_value = Field(int, mandatory=True)
    state_description = Field(str, mandatory=True)


# Defining a mapping between state values and descriptions
STATE_MAP = {
    0: "Normal",
    1: "Mild",
    2: "Severe",
    3: "Critical"
}

# Define the KnowledgeEngine
class DecisionEngine(KnowledgeEngine):
    """
    Knowledge engine for managing the drone's operational state based on battery status and sensor anomalies.
    """
    def __init__(self):
        super().__init__()
        self.logger = logger_instance.get_logger()
        self.reset()

    def get_fact(self, fact_type):
        """Retrieves the first fact of the specified type from the fact list."""
        for fact in self.facts.values():
            if isinstance(fact, fact_type):
                return fact
        return None
    
    def add_fact(self, fact):
        """Adds a new fact to the system."""
        self.declare(fact)

    def remove_fact(self, fact_type):
        """Remove all facts of a specific type from the system."""
        to_remove = [fact for fact in self.facts.values() if isinstance(fact, fact_type)]
        for fact in to_remove:
            self.retract(fact)

    def update_fact(self, fact_type, **kwargs):
        """
        Updates facts of a specific type. If the fact exists, it's updated with provided keyword arguments;
        otherwise, a new fact is created and added to the system.
        """
        self.remove_fact(fact_type)  # First, remove all existing facts of this type
        new_fact = fact_type(**kwargs)  # Create a new fact instance with the updated information
        self.add_fact(new_fact)  # Add the new fact to the system

    async def notify(self, data):
        """
        Notification handler for updates from providers (battery status or sensor anomalies).
        Updates the system facts based on the received data.
        """
        if data["use_case"] == "battery_status":
            self.update_fact(BatteryStatus, percent=data["percent"])
        if data["use_case"]  == "sensor_anomaly":
            self.update_fact(SensorAnomalyStatus, confidence=data["confidence"])
        #print("======================================================================")
        self.run()
        #print(f"\nFacts:\n{self.facts}")

    def update_state(self, fact_type, new_state_value):
        """
        Updates the state of a given type only if it has changed.
        If the current state is not present or differs from the new state, the fact is updated.
        """
        current_state = self.get_fact(fact_type)
        if current_state is None:
            self.declare(fact_type(state_value=new_state_value, state_description=STATE_MAP.get(new_state_value, "Unknown")))
        elif new_state_value != current_state["state_value"]:
            self.update_fact(fact_type, state_value=new_state_value, state_description=STATE_MAP.get(new_state_value, "Unknown"))
    
    @DefFacts()
    def _initial_action(self):
        yield OverallState(state_value=0, state_description=STATE_MAP.get(0, "Unknown"))
        self.logger.info("Overall state 0: Normal")

    # Rules to setup battery states with respect to the percent battery remaining
    @Rule(BatteryStatus(percent=P(lambda P: P > 75)))
    def battery_state_normal(self):
        self.update_state(BatteryState, 0)
        self.logger.info("Battery State 0: Normal")
    
    @Rule(BatteryStatus(percent=P(lambda P: 50 < P <= 75)))
    def battery_state_mild(self):
        self.update_state(BatteryState, 1)
        self.logger.info("Battery State 1: Mild")
    
    @Rule(BatteryStatus(percent=P(lambda P: 25 < P <= 50)))
    def battery_state_severe(self):
        self.update_state(BatteryState, 2)
        self.logger.info("Battery State 2: Severe")
    
    @Rule(BatteryStatus(percent=P(lambda P: P <= 25)))
    def battery_state_critical(self):
        self.update_state(BatteryState, 3)
        self.logger.info("Battery State 3: Critical")


    # Rules to setup sensor anomaly states with respect to the anomaly detection confidence level
    @Rule(SensorAnomalyStatus(confidence=P(lambda c: c <= 0.25)))
    def sensor_anomaly_state_normal(self):
        self.update_state(SensorAnomalyState, 0)
        self.logger.info("Sensor Anomaly State 0: Normal")
    
    @Rule(SensorAnomalyStatus(confidence=P(lambda c: 0.25 < c <= 0.5)))
    def sensor_anomaly_state_mild(self):
        self.update_state(SensorAnomalyState, 1)
        self.logger.info("Sensor Anomaly State 1: Mild")
    
    @Rule(SensorAnomalyStatus(confidence=P(lambda c: 0.5 < c <= 0.75)))
    def sensor_anomaly_state_severe(self):
        self.update_state(SensorAnomalyState, 2)
        self.logger.info("Sensor Anomaly State 2: Severe")
    
    @Rule(SensorAnomalyStatus(confidence=P(lambda c: 0.75 < c <= 1)))
    def sensor_anomaly_state_critical(self):
        self.update_state(SensorAnomalyState, 3)
        self.logger.info("Sensor Anomaly State 3: Critical")


    # Rule to determine overall state
    @Rule(BatteryState(state_value=P(lambda state_value: state_value >= 0)) | SensorAnomalyState(state_value=P(lambda state_value: state_value >= 0)))
    def determine_overall_state(self):
        """
        Determines the overall state of the drone based on the highest severity level
        between the current battery state and sensor anomaly state. This ensures that
        the drone's operational status reflects the most critical of the two assessments.
        """
        battery_state_fact = self.get_fact(BatteryState)
        sensor_anomaly_state_fact = self.get_fact(SensorAnomalyState)
        
        # Default to 0 if the facts are not found
        battery_state_value = battery_state_fact["state_value"] if battery_state_fact else 0
        sensor_anomaly_state_value = sensor_anomaly_state_fact["state_value"] if sensor_anomaly_state_fact else 0
        
        overall_state_value = max(battery_state_value, sensor_anomaly_state_value)
        
        # Update OverallState
        self.update_state(OverallState, overall_state_value)
        self.logger.info(f"Overall State {overall_state_value}: {STATE_MAP.get(overall_state_value, 'Unknown')}")

    # Rules to fire actions according to overall state
    @Rule(OverallState(state_value=0))
    def action_normal(self):
        self.logger.info("\033[92mAction: Continue mission\033[0m")
    
    @Rule(OverallState(state_value=1))
    def action_mild(self):
        self.logger.info("\033[93mAction: Consider returning to home soon\033[0m")

    @Rule(OverallState(state_value=2))
    def action_severe(self):
        self.logger.info("\033[91mAction: Plan to return to home immediately\033[0m")

    @Rule(OverallState(state_value=3))
    def action_critical(self):
        self.logger.info("\033[31mAction: Emergency landing is advised\033[0m")

import asyncio
from use_cases.battery_status import BatteryStatusProvider
from use_cases.sensor_anomaly import SensorAnomalyProvider

async def main():
    engine = DecisionEngine()
    battery_provider = BatteryStatusProvider(start_percent=100.0, step=-10.0, interval=1)
    battery_provider.add_listener(engine)
    sensor_anomaly_provider = SensorAnomalyProvider()
    sensor_anomaly_provider.add_listener(engine)

    
    # Run both providers concurrently
    await asyncio.gather(
        sensor_anomaly_provider.start(),
        battery_provider.start()
    )

if __name__ == "__main__":
    asyncio.run(main())