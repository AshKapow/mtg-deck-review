import openai
import sys
import requests
import time
from collections import Counter, defaultdict
from cachetools import LRUCache, cached
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

# Cache with a TTL of 24 hours (86400 seconds)
card_legality_cache = LRUCache(maxsize=1000)

BASIC_LANDS = ["Plains", "Island", "Swamp", "Mountain", "Forest"]

def extract_card_details(card_detail):
    """
    Extracts the quantity, card name, and card set from a string in the format: "Quantity CardName [Card Set]"

    Args:
    - card_detail (str): The card detail in the format "Quantity CardName [Card Set]"

    Returns:
    - tuple: The extracted quantity, card name, and card set.
    """
    # Split the string by '[' to separate the card name from the card set
    parts = card_detail.split(" [", 1)
    if len(parts) == 2:
        card_name_with_quantity = parts[0].strip()
        card_set = parts[1].rstrip("]")  # Remove the closing bracket from the card set
        quantity, card_name = card_name_with_quantity.split(" ", 1)
        return int(quantity), card_name, card_set
    else:
        # Handle the case where there's no card set specified
        card_name_with_quantity = card_detail.strip()
        quantity, card_name = card_name_with_quantity.split(" ", 1)
        return int(quantity), card_name, None


@cached(card_legality_cache)
def validate_card_for_format(card_name, format_type, card_set=None):
    """
    Validates a single card for a specific format using the Scryfall API.

    Args:
    - card_name (str): Name of the card to validate.
    - format_type (str): The MTG format to validate against.
    - card_set (str, optional): The card set or edition.

    Returns:
    - bool: True if the card is legal for the format, False otherwise.
    """

    base_url = "https://api.scryfall.com/cards/search"
    if card_set:
        query = f'?q=name:"{card_name}"+set:{card_set}&unique=cards'
    else:
        query = f'?q=name:"{card_name}"&unique=cards'

    print(f"Fetching details for card: {card_name}")
    url = base_url + query
    response = requests.get(url)
    response_json = response.json()

    if (
        response.status_code != 200
        or "data" not in response_json
        or not response_json["data"]
    ):
        print(f"Error fetching data for card: {card_name}")
        return False

    # Assuming the first match is the desired card (this may need refinement)
    card_data = response_json["data"][0]
    result = card_data["legalities"][format_type] == "legal"

    return result


def validate_deck_for_format(deck_details, format_type):
    """
    Validates the deck for a specific format.
    
    Args:
    - deck_details (list): List of card details from the deck.
    - format_type (str): The MTG format to validate against.

    Returns:
    - list: List of cards that are not legal for the format.
    """
    illegal_cards = []
    card_counts = defaultdict(int)
    
    # Identify the format's specific rules
    if format_type == "commander":
        total_cards_required = 100
        max_duplicates = 1  # Only basic lands can appear more than once
    
    for card_detail in deck_details:
        quantity, card_name, card_set = extract_card_details(card_detail)
        card_counts[card_name] += quantity
        
        # Check card legality for the format
        if not validate_card_for_format(card_name, format_type, card_set):
            illegal_cards.append(f"{card_name} is not legal for {format_type} format.")
        
        # Check for duplicates in formats where it's not allowed
        if format_type == "commander" and card_counts[card_name] > max_duplicates and card_name not in BASIC_LANDS:
            illegal_cards.append(f"{card_name} appears {card_counts[card_name]} times in a Commander deck.")
    
    # Check total card count
    total_cards = sum(card_counts.values())
    if total_cards != total_cards_required:
        illegal_cards.append(f"{format_type.capitalize()} deck must have exactly {total_cards_required} cards. You have {total_cards} cards.")
    
    return illegal_cards


def ask_chatgpt_about_deck(deck_details):
    """
    Sends the MTG deck details to ChatGPT for analysis and suggestions.

    Args:
    - deck_details (str): A list of MTG cards.

    Returns:
    - str: The response from ChatGPT.
    """

    # Add context to the deck details
    context = """
    You are an expert on Magic: The Gathering (MTG). You are provided with a list of cards that form a deck. Your task is to:
    1. Review the deck.
    2. Provide a short paragraph summarizing the main mechanic of the deck.
    3. Suggest up to 5 cards that do not match the mechanic of the deck.
    4. Recommend up to 5 cards that could be added to improve the deck's synergy.
    
    Here are the cards in the deck:
    """
    prompt = (
        context + deck_details + "\n\nPlease provide your analysis and suggestions."
    )

    # Use the chat model endpoint
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
    )

    return response.choices[0].message["content"].strip()


def read_deck_from_file(file_name):
    """
    Reads the deck details from a given file.

    Args:
    - file_name (str): Name of the file containing deck details.

    Returns:
    - str: The contents of the file.
    """
    with open(file_name, "r") as file:
        return file.read()


if __name__ == "__main__":
    command = sys.argv[1]

    if command == "validate":
        format_type = sys.argv[2]
        file_name = sys.argv[3]
        deck_details = read_deck_from_file(file_name).splitlines()
        illegal_cards = validate_deck_for_format(deck_details, format_type)
        if illegal_cards:
            response = (
                f"The following cards are not legal for {format_type} format:\n"
                + "\n".join(illegal_cards)
            )
        else:
            response = f"All cards in the deck are legal for {format_type} format."
    elif command == "review":
        file_name = sys.argv[2]
        deck_details = read_deck_from_file(file_name)
        response = ask_chatgpt_about_deck(deck_details)
    else:
        print("Invalid command. Use 'validate' or 'review'.")
        sys.exit(1)

    print(response)
