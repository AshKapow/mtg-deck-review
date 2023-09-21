# MTG Deck Review Tool

The MTG Deck Review Tool is a Python application that allows you to validate Magic: The Gathering (MTG) decks against specific formats and review their contents.

## Installation

1. Clone this repository to your local machine:
```
git clone https://github.com/ashkapow/mtg-deck-review.git
```

2. Navigate to the project directory:
```
cd mtg-deck-review
```

3. Create a virtual environment (optional but recommended):
```
python -m venv venv
```

4. Activate the virtual environment:

- On Windows:
```
venv\Scripts\Activate
```

- On macOS and Linux:
```
source venv/bin/activate
```

5. Install the required Python packages:
```
pip install -r requirements.txt
```

## Configuration

1. Create a `config.py` file in the project directory.

2. Obtain an API key from OpenAI by following the instructions on their website: [OpenAI API](https://platform.openai.com/account/api-keys).

3. Add your OpenAI API key to the config.py file as follows:
```
OPENAI_API_KEY = 'your-api-key-here'
```
This OpenAI API key is required for certain functionalities in the project, including the deck review feature that utilizes the OpenAI GPT-3 model.

## Usage
Deck Structure
Decks should be defined in .txt files following the format:
```
Quantity CardName [CardSet]
```

Where:
- `Quantity` is the number of cards of that type in the deck.
- `CardName` is the name of the card.
- `CardSet` (optional) is the card set or edition.

Example:
```
3 Lightning Bolt [M10]
2 Counterspell
4 Forest
```

### Review a Deck
The review function allows you to get insights and recommendations about the contents of your deck. It utilises the OpenAI GPT-3 model to provide suggestions such as adding cards, removing cards, or making improvements to your deck composition. The review function is particularly useful for fine-tuning your deck or exploring creative ideas.

To review the contents of a deck, use the following command:
```
python main.py review <deck_file>
```

Replace `<deck_file>` with the path to your deck file.

Keep in mind that the quality of the suggestions may vary, and it's always a good practice to use your judgment when making changes to your deck based on the recommendations.


### Validate a Deck
To validate a deck against a specific format, use the following command:
```
python main.py validate <format_type> <deck_file>
```

Replace <format_type> with the desired format (e.g., commander) and <deck_file> with the path to your deck file.

# Feedback
If you encounter any issues or have suggestions for improvements, please feel free to open an issue on the GitHub repository.

# Author
This project was developed by Ash Powell. If you have any questions, suggestions, or feedback, you can reach out me via email at [ash@thekapow.com] or visit [GitHub profile](https://github.com/ashkapow).
