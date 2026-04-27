
import collections.abc

class PromptParserService:
    def parse(self, prompt_object: dict) -> str:
        """
        Recursively parses a dictionary, finds all keys named 'value',
        and concatenates their string or list-of-string values into a single
        comma-separated string.
        """
        parts = []

        def find_values(data):
            """
            Inner recursive function to traverse the data structure.
            """
            # If the data is a dictionary or a similar mapping object
            if isinstance(data, collections.abc.Mapping):
                # Check if this dictionary has our target 'value' key.
                if 'value' in data and data['value'] is not None:
                    value = data['value']
                    # If the value is a non-empty string, add it to our parts.
                    if isinstance(value, str) and value.strip():
                        parts.append(value.strip())
                    # If the value is a list, process its items.
                    elif isinstance(value, list):
                        # Convert all non-empty items to strings and filter them out.
                        str_values = [str(v).strip() for v in value if v]
                        if str_values:
                            # Join the list items with a comma and add as a single part.
                            parts.append(', '.join(str_values))
                    # Once we extract a 'value', we don't need to dig deeper in this branch.
                else:
                    # If it's a structural dictionary (e.g., a category), search its children.
                    for v in data.values():
                        find_values(v)
            
            # If the data is a list, iterate over its items to find more structures.
            elif isinstance(data, list):
                for item in data:
                    find_values(item)

        find_values(prompt_object)
        
        # Join all the collected parts, filtering out any empty strings that might have slipped through.
        return ", ".join(filter(None, parts))

# Create a singleton instance for easy importing and use across the application.
prompt_parser_service = PromptParserService()
