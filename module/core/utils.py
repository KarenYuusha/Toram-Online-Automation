import re
from difflib import get_close_matches
from datetime import datetime
import os


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


def find_closest_match(input_text, correct_names, verbose=False):
    # Get the closest match from the list
    closest_matches = get_close_matches(
        input_text, correct_names, n=1, cutoff=0.6)
    if closest_matches:
        return closest_matches[0]
    else:
        if verbose:
            print(f"No close match found for: {input_text}")
        return input_text


def log_stack(user_name, stack_count, item_name='summer shell', log_file="gift.log", max_size_mb=5):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"User: {user_name} | {item_name} | Stack: {stack_count} | {now}\n"

    # Check file size before writing
    if os.path.exists(log_file) and os.path.getsize(log_file) > max_size_mb * 1024 * 1024:
        os.rename(log_file, log_file.replace(
            ".log", f"_{now.replace(':','-')}.log"))

    with open(log_file, "a", encoding="utf-8") as f:
        f.write(log_entry)


def add_to_log(user_name, stack_count, item_name='summer shell', log_file='gift.log'):
    user_name = os.path.splitext(os.path.basename(user_name))[0]
    log_stack(user_name, stack_count, item_name, log_file)
