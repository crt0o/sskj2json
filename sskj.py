from enum import Enum
import requests
from bs4 import BeautifulSoup
import re
import json

# --- Enums ---

class WordType(int, Enum):
    NONE = 0 # No word type specified
    NOUN = 1 # Noun
    VERB = 2 # Verb
    ADV = 3 # Adverb
    PART = 4 # Particle
    CONJ = 5 # Conjunction
    INT = 6 # Interjection
    ADJ = 7 # Adjective
    PREP = 8 # Preposition
    PRED = 9 # Predicative verb
    NUM = 10 # Numeral
    PRO = 11 # Pronoun
    ATTR = 12 # Attribute

class WordGender(int, Enum):
    M = 0 # Masculine
    F = 1 # Feminine
    N = 2 # Neuter

class WordAspect(int, Enum):
    IND = 0 # Indeterminate
    DET = 1 # Determinate
    BOTH = 2 # Both

# --- Constants ---

TYPE_STRING_TABLE = {
    '': WordType.NONE,
    'm': WordType.NOUN,
    'ž': WordType.NOUN,
    's': WordType.NOUN,
    'dov.': WordType.VERB,
    'nedov.': WordType.VERB,
    'dov. in nedov.': WordType.VERB,
    'nedov. in dov.': WordType.VERB,
    'prisl.': WordType.ADV,
    'člen.': WordType.PART,
    'vez.': WordType.CONJ,
    'prid.': WordType.ADJ,
    'v prid. rabi': WordType.ADJ,
    'medm.': WordType.INT,
    'predl.': WordType.PREP,
    'povdk.': WordType.PRED,
    'štev.': WordType.NUM,
    'zaim.': WordType.PRO,
    'kot prilastek': WordType.ATTR
}

GENDER_STRING_TABLE = {
    'm': WordGender.M,
    'ž': WordGender.F,
    's': WordGender.N
}

ASPECT_STRING_TABLE = {
    'dov.': WordAspect.DET,
    'nedov.': WordAspect.IND,
    'dov. in nedov.': WordAspect.BOTH,
    'nedov. in dov.': WordAspect.BOTH
}

# --- Functions ---

# Get a page from fran.si (contains 20 entries)
def get_page(n: int) -> str:
    res: requests.Response = requests.get('https://fran.si/iskanje', {
        'page': n,
        'FilteredDictionaryIds': 133,
        'View': 0,
        'Query': '*'
    })

    return res.text

# Scrape data about the entries from the page text
def scrape_page(text: str) -> dict:
    soup = BeautifulSoup(text, 'html.parser')

    entries = soup.find_all('div', 'entry-content')

    entries_scraped: list = []

    for entry in entries:
        entry_scraped: dict = {}

        # The word itself, including diacritics
        entry_scraped['uname'] = (uname := entry.find('span', 'font_xlarge').a.string)

        # A version without them (excluding č, š and ž)
        name = re.sub(r'á|à|â', 'a', uname)
        name = re.sub(r'é|è|ê', 'e', name)
        name = re.sub(r'ì|í|î', 'e', name)
        name = re.sub(r'ò|ó|ô', 'e', name)
        name = re.sub(r'ù|ú|û', 'e', name)
        name = re.sub(r'À|Á|Â', 'A', name)
        name = re.sub(r'È|É|Ê', 'E', name)
        name = re.sub(r'Ì|Í|Î', 'I', name)
        name = re.sub(r'Ò|Ó|Ô', 'O', name)
        name = re.sub(r'Ù|Ú|Û', 'U', name)
        name = re.sub(r'ŕ', 'r', name)
        name = re.sub(r'Ŕ', 'R', name)

        entry_scraped['name'] = name
        entry_scraped['n'] = int(n.string) if (n := entry.find('span', 'color_lightdark font_xsmal sup')) != None else 1
        
        # Try to find the header
        header = entry.find('span', attrs={'data-group': 'header'})

        # If not found, entry is a redirect
        if header == None:
            entry_scraped['ref'] = entry.find('span', attrs={'class': 'color_dark', 'data-group': 'other'}).a.string
            entries_scraped.append(entry_scraped)
            continue
        else:
            entry_scraped['ref'] = None
        
        # Word type
        type_string = type_span.span.string.strip() if (type_span := header.find('span', attrs={'data-group': 'header qualifier'})) != None else ''
        entry_scraped['type_'] = (type_ := TYPE_STRING_TABLE[type_string])

        # Grammatical gender
        entry_scraped['gender'] = GENDER_STRING_TABLE[type_string] if type_ == WordType.NOUN else None

        # Grammatical aspect
        entry_scraped['aspect'] = ASPECT_STRING_TABLE[type_string] if type_ == WordType.VERB else None

        # Pitch accent
        accent_span = header.find('span', attrs={'title': 'Tonemski naglas'})

        entry_scraped['accent'] = []

        if accent_span != None:
            accent_strings = re.split(r'\s+', accent_span.string)
            for accent_string in accent_strings:
                entry_scraped['accent'].append(re.sub(r'\s+|;|,', '', accent_string))

        # Additional forms
        form_spans = header.find_all('span', attrs={'title': 'Oblika'})
        entry_scraped['forms'] = []
        
        for form_span in form_spans:
            entry_scraped['forms'] += re.split(r'\s+', form_span.string.strip())

        # Qualifiers
        qualifier_spans = header.find_all('span', attrs={'data-group': 'qualifier header '})
        entry_scraped['qualifiers'] = []

        for qualifier_span in qualifier_spans:
            if (title := qualifier_span['title']) != 'Kvalifikator, pojasnilo' and title != 'množina' and title != 'dvojina':
                entry_scraped['qualifiers'].append(re.sub(r'\s+', '', qualifier_span.string).strip())

        # Pronunciations
        pronunciation_spans = header.find_all('span', attrs={'title': 'Izgovor'})

        entry_scraped['pronunciation'] = []

        for pronunciation_span in pronunciation_spans:
            entry_scraped['pronunciation'] += re.split(r'\s+', pronunciation_span.string.strip())

        # The full header, unprocessed
        entry_scraped['header_plain'] = re.sub(r'\xa0', ' ', header.get_text().strip())

        entries_scraped.append(entry_scraped)

    return entries_scraped

# --- Main ---

# Process all 4884 pages and write them to a file
def main() -> None:
    with open('sskj.json', 'w') as f:
        f.write('[')
        
        for i in range(1, 4885):
            while True:
                try:
                    text = get_page(i)
                    break
                except:
                    continue
                    
            scraped = scrape_page(text)
            scraped_json = json.dumps(scraped)
            f.write(scraped_json[1:-1])

            if i < 4884:
                f.write(', ')

            print(i)
        
        f.write(']')

if __name__ == '__main__':
    main()