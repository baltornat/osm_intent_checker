import re


# Function that converts values with suffixes to the corresponding value in bytes
def convert(string):
    suffixes = {
        'Ki': 2 ** 10,
        'Mi': 2 ** 20,
        'Gi': 2 ** 30,
        'Ti': 2 ** 40,
        'Pi': 2 ** 50,
        'Ei': 2 ** 60,
        'm': 10 ** -3,
        'k': 10 ** 3,
        'M': 10 ** 6,
        'G': 10 ** 9,
        'T': 10 ** 12,
        'P': 10 ** 15,
        'E': 10 ** 18
    }
    # Extract the numerical value and suffix from the input string
    match = re.match(r'(\d+(?:\.\d+)?)\s*([a-zA-Z]*)', string)
    value = float(match.group(1))
    suffix = match.group(2)
    # Convert the numerical value
    if suffix in suffixes:
        multiplier = suffixes[suffix]
        new_value = float(value * multiplier)
    else:
        new_value = float(value)
    return new_value


# Function that parses a list to extract a specific tag
def find_nested_tags(data, tag_name):
    result = []
    # If data is of type dict then True
    if isinstance(data, dict):
        for key, value in data.items():
            if key == tag_name:
                # Append to the list the value
                result.append(value)
            else:
                # Concat to the list the nested result
                result += find_nested_tags(value, tag_name)
    # If data is of type list then True
    elif isinstance(data, list):
        for item in data:
            result += find_nested_tags(item, tag_name)
    return result
