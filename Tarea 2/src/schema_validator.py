# Typing Imports #
from typing import Any, Callable

def __schema_validator_function(data: Any, schema: Any) -> bool:

    # Checking all instances of dictionary schema #
    if isinstance(schema, dict):

        # Return false if the data is nota also a instance of dictionrary #
        if not isinstance(data, dict):
            return False
    
        # Iterate through keys in the schema #
        for key, expected_schema in schema.items():

            # If the key does not exist in data atomatically fail #
            if key not in data:
                return False

            # Iterate through sub items #
            if not __schema_validator_function(data[key], expected_schema):
                return False
        
        return True

    # Accept all instances of List in schema acts like List[any]
    if schema is list:
        return isinstance(data, list)

    # Accept all instances of List in schema [int], [str], [etc]
    if isinstance(schema, list):

        # Data must be a list #
        if not isinstance(data, list):
            return False

        # Empty list can be valid #
        if len(schema) == 0:
            return True

        # List should have at least one element if its not empty #
        if len(schema) != 1:
            return False


        # We get the type from the list
        schema_item = schema[0]

        # Iterate every item and check if its compliant with the same type for the data
        return all(__schema_validator_function(item, schema_item) for item in data)

    # Check for individual types #
    if isinstance(schema, type):
        return isinstance(data, schema)
    
    # Final check in case schema is just an item #
    return data == schema


# Decorator fabric #
def schema_validator(schema:dict):

    # Decorator defintion #
    def schema_decorator(decorated_function:Callable):

        # Decorator running function #
        def schema_function(*args):
            result = decorated_function(args[0])

            if(__schema_validator_function(result, schema) == False):
                return None
            
            return result
        
        return schema_function
    return schema_decorator