from clips import Environment, Symbol

env = Environment()

# Load the CLIPS file containing your rules and templates
env.load('/home/selinashrestha/Documents/SRTA/Code/decision-engine/clipspy/templates.clp')
env.load('/home/selinashrestha/Documents/SRTA/Code/decision-engine/clipspy/rules.clp')

# Turn on watching for facts and rules using the eval method
env.eval('(watch facts)')
env.eval('(watch rules)')

# Function to assert facts from Python
def assert_fact(env, fact_name, **kwargs):
    # Construct the fact string
    fact_str = f"({fact_name} "
    for key, value in kwargs.items():
        fact_str += f"({key} {value}) "
    fact_str += ")"
    
    # Assert the fact in the environment
    env.assert_string(fact_str)

def add_fact(env, fact_type, **kwargs):
    env.find_template(fact_type).assert_fact(**kwargs)

def update_fact(env, template_name, **kwargs):
    """
    Update the existing fact of the specified template with new values, or create it if it does not exist.

    :param template_name: The name of the template (fact type).
    :param kwargs: Keyword arguments representing the slots to update or create with their new values.
    """
    # Search for the existing fact of the given template
    existing_fact = next((fact for fact in env.facts() if fact.template.name == template_name), None)
    
    if existing_fact:
        # If the fact exists, modify its slots
        existing_fact.modify_slots(**kwargs)
    else:
        # If the fact does not exist, add a new fact
        add_fact(env, template_name, **kwargs)

# Example of asserting a fact
#env.find_template('BatteryStatus').assert_fact(percent=80.0)
#env.find_template('SensorAnomalyStatus').assert_fact(confidence=0.45)
#assert_fact(env, 'BatteryStatus', percent=80.0)
#assert_fact(env, 'SensorAnomalyStatus', confidence=0.45)

env.reset()

for percent in range(100, 0, -20):
    print("======================================================================")
    update_fact(env, 'BatteryStatus', percent=float(percent))    
    # Run the CLIPS inference engine
    env.run()
    """
    # Extract and print facts (for demonstration)
    for fact in env.facts():
        print(fact)
    """

"""
print("======================================================================")
update_fact(env, 'BatteryStatus', percent=80.0)    
# Run the CLIPS inference engine
env.run()
# Extract and print facts (for demonstration)
for fact in env.facts():
    print(fact)

print("======================================================================")
update_fact(env, 'BatteryStatus', percent=40.0)    
# Run the CLIPS inference engine
env.run()
# Extract and print facts (for demonstration)
for fact in env.facts():
    print(fact)
"""


