from clips import Environment, Symbol
import os

# Retrieve the path to the directory containing this script.
# This is used for loading external CLIPS template and rule files.
path_to_current_dir = os.path.dirname(__file__)
DEBUG = False

def action_for_normal_state():
    """
    Insert actions for normal state here.
    Currently prints a green colored message indicating normal operational state.
    """
    print("\033[92mAction: Continue mission\033[0m")

def action_for_mild_state():
    """
    Insert actions for mild state here.
    Currently prints a yellow colored message suggesting consideration of returning home soon.
    """
    print("\033[93mAction: Consider returning to home soon\033[0m")

def action_for_severe_state():
    """
    Insert actions for severe state here.
    Currently prints a light red colored message advising planning for immediate return to home.
    """
    print("\033[91mAction: Plan to return to home immediately\033[0m")

def action_for_critical_state():
    """
    Insert actions for critical state here.
    Currently prints a red colored message strongly advising emergency landing.
    """
    print("\033[31mAction: Emergency landing is advised\033[0m")


class DecisionEngine():
    """
    A decision-making engine that integrates with a CLIPS environment for rule-based logic.

    The engine is capable of registering Python functions as actions for CLIPS rules, 
    managing facts within the CLIPS environment, and handling notifications from 
    external data providers such as battery status and sensor anomalies.

    Methods:
        __init__: Initializes the engine and loads CLIPS templates and rules.
        register_python_functions: Registers a list of Python functions with the CLIPS environment.
        add_fact: Adds a new fact to the CLIPS environment.
        update_fact: Updates an existing fact or adds it if it doesn't exist.
        notify: Handles notifications from data providers and updates the system facts accordingly.
    """
    def __init__(self) -> None:
        """Initializes the decision engine, loading the necessary CLIPS templates and rules."""
        self.env = Environment()
        # Register python functions in CLIPS environment so that they can be called as actions when rules are fired
        self.register_python_functions([action_for_normal_state, action_for_mild_state, action_for_severe_state, action_for_critical_state])
        # Load the CLIPS file containing the templates and rules
        self.env.load(f'{path_to_current_dir}/clipspy/templates.clp')
        self.env.load(f'{path_to_current_dir}/clipspy/rules.clp')
        if DEBUG:
            # Turn on watching for facts and rules using the eval method
            self.env.eval('(watch facts)')
            self.env.eval('(watch rules)')
        self.env.reset()

    def register_python_functions(self, functions):
        """
        Registers Python functions as callable actions within the CLIPS environment.

        Parameters:
            functions (list): A list of Python function objects to register.
        """
        for function in functions:
            self.env.define_function(function)

    def add_fact(self, template_name, **kwargs):
        """
        Adds a new fact to the CLIPS environment based on a template.

        Parameters:
            template_name (str): The name of the template to use for the fact.
            **kwargs: Keyword arguments representing the slots of the fact and their values.
        """
        self.env.find_template(template_name).assert_fact(**kwargs)

    def update_fact(self, template_name, **kwargs):
        """
        Updates an existing fact if it exists, or adds a new one if it doesn't.

        Parameters:
            template_name (str): The name of the template to use for the fact.
            **kwargs: Keyword arguments representing the slots to update or create with their new values.
        """
        # Search for the existing fact of the given template
        existing_fact = next((fact for fact in self.env.facts() if fact.template.name == template_name), None)
        
        if existing_fact:
            # If the fact exists, modify its slots
            existing_fact.modify_slots(**kwargs)
        else:
            # If the fact does not exist, add a new fact
            self.add_fact(template_name, **kwargs)

    async def notify(self, data):
        """
        Notification handler that updates system facts based on data from providers.

        Parameters:
            data (dict): A dictionary containing the data from the provider, including
                         a use case identifier and relevant values.
        """
        if data["use_case"] == "battery_status":
            try:
                self.update_fact('BatteryStatus', percent=data["percent"])
            except AttributeError:
                self.add_fact('BatteryStatus', percent=data["percent"])
        if data["use_case"]  == "sensor_anomaly":
            try:
                self.update_fact('SensorAnomalyStatus', confidence=data["confidence"])
            except AttributeError:
                self.add_fact('SensorAnomalyStatus', confidence=data["confidence"])
        #print("======================================================================")
        self.env.run()
        """
        # Extract and print facts (for demonstration)
        for fact in self.env.facts():
            print(fact)
        """


import asyncio
from use_cases.battery_status import BatteryStatusProvider
from use_cases.sensor_anomaly import SensorAnomalyProvider

async def main():
    """
    Main coroutine that initializes the decision engine and starts the data providers.
    """
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