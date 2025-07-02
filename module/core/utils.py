import re
from difflib import get_close_matches


def load_abbreviations(file_path):
    abbreviation_map = {}
    with open(file_path, 'r') as file:
        for line in file:
            terms, abbreviation = line.strip().split(':')
            for term in terms.split(','):
                abbreviation_map[term.lower().strip()] = abbreviation.strip()
    return abbreviation_map

def create_regex(abbreviation_map):
    # Create a single regex pattern for all terms
    terms_pattern = '|'.join(re.escape(term) for term in abbreviation_map)
    return re.compile(r'\b(' + terms_pattern + r')\b', re.IGNORECASE)

def convert_to_abbreviation(text, abbreviation_map, pattern):
    # Use the regex pattern to find and replace abbreviations
    return pattern.sub(lambda match: abbreviation_map[match.group(0).lower()], text)

def get_abbreviation(term, file_path):
    abbreviation_map = load_abbreviations(file_path)
    return abbreviation_map.get(term.lower())

def find_closest_match(input_text, correct_names):
    # Get the closest match from the list
    closest_matches = get_close_matches(input_text, correct_names, n=1, cutoff=0.6)
    if closest_matches:
        return closest_matches[0]
    else:
        print(f"No close match found for: {input_text}")
        return input_text