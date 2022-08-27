# Structure

The product json file is structured as an array of objects which represent entries from the dictionary. They generally come in 2 forms:

## Ordinary entries

| Field | Description | Data type |
|-------|-------------|-----------|
| `uname` | The word itself including diacritics | `string` |
| `name` | The word, with diacritics stripped out (excluding č, š and ž) | `string` |
| `n` | The sequential number of the entry (used to differentiate between entries with identical spelling) | `number` |
| `ref` | Always `null` in ordinary entries, used to store redirects | `string` or `null` |
| `type_` | The type of the word encoded as an enum | `number` |
| `gender` | The grammatical gender of the word as an enum (only for nouns, otherwise `null`) | `number` or `null` |
| `aspect` | The grammatical aspect as an enum (only for verbs, otherwise `null`) | `number` or `null` |
| `accent` | The possible pitch accents (`[]` if none are listed) | `string[]` |
| `forms` | The additional forms (`[]` if none are listed) | `string[]` |
| `qualifiers` | Any style qualifiers (`[]` if none are listed) | `string[]` |
| `pronunciation` | Possible pronunciations (`[]` if none are listed) | `string[]` |
| `header_plain` | The entire unprocessed header | `string` |

## Redirect entries

| Field | Description | Data type |
|-------|-------------|-----------|
| `uname` | The word itself including diacritics | `string` |
| `name` | The word, with diacritics stripped out (excluding č, š and ž) | `string` |
| `n` | The sequential number of the entry (used to differentiate between entries with identical spellings) | `number` |
| `ref` | Points to the `uname` of the word the entry redirects to | `string` or `null` |

# Enums

## Type

| Type | Enumeration |
|------|-------------|
| None | 0 |
| Noun | 1 |
| Verb | 2 |
| Adverb | 3 |
| Particle | 4 |
| Conjunction | 5 |
| Interjection | 6 |
| Adjective | 7 |
| Preposition | 8 |
| Predicative verb | 9 |
| Numeral | 10 |
| Pronoun | 11 |
| Attribute | 12 |

## Gender

| Gender | Enumeration |
|--------|-------------|
| Masculine | 0 |
| Feminine | 1 |
| Neuter | 2 |

## Aspect

| Aspect | Enumeration |
|--------|-------------|
| Determinate | 0 |
| Indeterminate | 1 |
| Both | 2 |

# Notes

The scraper currently only extracts the word name and header. I will possibly add support for explanations later.
