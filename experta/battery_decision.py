from experta import *
import threading
import time

# Shared resource and condition
battery_data = {'percent': 100.0}
battery_data_condition = threading.Condition()


class BatteryProvider(threading.Thread):
    def __init__(self, start_percent=100.0, step=-5.0, interval=2, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.battery_percent = start_percent
        self.step = step
        self.interval = interval
        self.running = True

    def run(self):
        global battery_data, battery_data_condition
        while self.running and self.battery_percent >= 0:
            with battery_data_condition:
                battery_data['percent'] = self.battery_percent
                battery_data_condition.notify_all()  # Notify the engine of the update
            print(f"Simulated battery level: {self.battery_percent}%")
            self.battery_percent += self.step
            time.sleep(self.interval)

    def stop(self):
        self.running = False
"""
class BatteryProvider(threading.Thread):
    def __init__(self, start_percent=50.0, decrease_step=-5.0, increase_step=5.0, interval=2, change_condition=40, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.battery_percent = start_percent
        self.decrease_step = decrease_step
        self.increase_step = increase_step
        self.interval = interval
        self.change_condition = change_condition
        self.running = True
        self.increasing = False  # Track whether the battery is increasing or decreasing

    def run(self):
        global battery_data, battery_data_condition
        while self.running:
            with battery_data_condition:
                battery_data['percent'] = self.battery_percent
                battery_data_condition.notify_all()  # Notify the engine of the update
            
            print(f"Simulated battery level: {self.battery_percent}%")

            # Check condition to switch between increasing and decreasing
            if self.increasing:
                self.battery_percent += self.increase_step
                if self.battery_percent >= 100:
                    self.increasing = False  # Switch to decreasing once fully charged
            else:
                self.battery_percent += self.decrease_step
                if self.battery_percent <= self.change_condition:
                    self.increasing = True  # Switch to increasing if below the change condition
            
            time.sleep(self.interval)

    def stop(self):
        self.running = False
"""

# Define facts
class BatteryRemaining(Fact):
    percent = Field(float, mandatory=True)

class BatteryStatus(Fact):
    state = Field(str, mandatory=True)

# Define the KnowledgeEngine
class DroneBatteryManager(KnowledgeEngine):
    
    @DefFacts()
    def _initial_action(self):
        yield BatteryRemaining(percent=100.00)
        yield BatteryStatus(state="Normal")
    

    last_state = None

    # Function to update state only if changed
    def update_state(self, new_state):
        if self.last_state is None or new_state != self.last_state:
            fact_id = self.fact_id_for_state(self.last_state)
            if fact_id is not None:  # Check if the fact ID exists before retracting
                self.retract(fact_id)
            self.declare(BatteryStatus(state=new_state))
            self.last_state = new_state

    # Helper function to find the fact ID for a given state
    def fact_id_for_state(self, state):
        for fact_id, fact in self.facts.items():
            if isinstance(fact, BatteryStatus) and fact["state"] == state:
                return fact_id
        return None 
    
    # Rules to setup battery states with respect to the percent battery remaining
    @Rule(BatteryRemaining(percent=P(lambda P: P > 75)))
    def state_normal(self):
        print("State: Normal")
        self.update_state("Normal")
    
    @Rule(BatteryRemaining(percent=P(lambda P: 50 < P <= 75)))
    def state_mild(self):
        print("State: Mild")
        self.update_state("Mild")
    
    @Rule(BatteryRemaining(percent=P(lambda P: 25 < P <= 50)))
    def state_severe(self):
        print("State: Severe")
        self.update_state("Severe")
    
    @Rule(BatteryRemaining(percent=P(lambda P: P <= 25)))
    def state_critical(self):
        print("State: Critical")
        self.declare(BatteryStatus(state="Critical"))

    # Rules to fire actions according to battery states
    @Rule(BatteryStatus(state="Normal"))
    def action_normal(self):
        print("Continue mission")
    
    @Rule(BatteryStatus(state="Mild"))
    def action_mild(self):
        print("Consider returning to home soon")

    @Rule(BatteryStatus(state="Severe"))
    def action_severe(self):
        print("Plan to return to home immediately")

    @Rule(BatteryStatus(state="Critical"))
    def action_critical(self):
        print("Emergency landing is advised")

    def run_engine(self):
        global battery_data, battery_data_condition
        while True:
            with battery_data_condition:
                battery_data_condition.wait()  # Wait for an update
                battery_percent = battery_data['percent']

            #self.reset()  # Reset the engine for the new data
            # Retrieve all BatteryRemaining facts
            battery_remaining_facts = [fact for fact in self.facts.values() if isinstance(fact, BatteryRemaining)]
            
            # Retract all existing BatteryRemaining facts
            for fact in battery_remaining_facts:
                self.retract(fact)

            # Declare a new BatteryRemaining fact with the updated percent
            self.declare(BatteryRemaining(percent=battery_percent))
            self.run()
            print(self.facts)
            


# Create an instance of the engine
engine = DroneBatteryManager()

# Create and start the battery provider thread
#battery_provider = BatteryProvider(start_percent=100.0, step=-10.0, interval=2)
battery_provider = BatteryProvider()
battery_provider.start()

# Start the engine in a separate thread
engine.reset()
engine_thread = threading.Thread(target=engine.run_engine)
engine_thread.start()

# Simulation runs until the battery provider stops
try:
    battery_provider.join()
except KeyboardInterrupt:
    print("Stopping simulation...")
    battery_provider.stop()

print("Simulation finished. Stopping engine listener...")
# Stop the engine listener thread
with battery_data_condition:
    battery_data_condition.notify_all()  # Ensure the engine thread exits the wait state
engine_thread.join()


"""
# Reset the engine (required before starting the engine)
engine.reset()

# Insert facts based on current situations
engine.declare(BatteryRemaining(percent=45.0)) # Example: 60% battery remaining

# Run the engine to evaluate the rules
engine.run()
print(engine.facts)
"""