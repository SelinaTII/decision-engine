# Make a subclass of KnowledgeEngine, use Rule to decorate its methon
# Then instantiate it, populate it with facts, and run it

from experta import *
class Greetings(KnowledgeEngine):
    @DefFacts()
    def _initial_action(self):
        yield Fact(action="greet")

    
    @Rule(Fact(action="greet"), 
          NOT(Fact(name=W())))
    def ask_name(self):
        name_input = input("What's your name?")
        self.declare(Fact(name=name_input))
    
    @Rule(Fact(action="greet"), 
          NOT(Fact(location=W())))
    def ask_location(self):
        location_input = input("Where are you?")
        self.declare(Fact(location=location_input))

    @Rule(Fact(action="greet"), 
          Fact(name=MATCH.name),  # Use MATCH to bind the fact's value to a variable
          Fact(location=MATCH.location))
    def greet(self, name, location):  # Access the matched values as parameters
        print(f"Hi {name}! How is the weather in {location}?")

engine = Greetings()
engine.reset() # Prepare the engine for the execution.
engine.run() # Run it!