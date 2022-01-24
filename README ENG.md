# ezdate
NLP module for Hungarian date-entity recognition and translation to specific date values ​​\

## Installation
pip install hundate

Prerequisite: Python 3.7 or later

## Importing
- from hundate import ezdate \
   Reference: ezdate.text2date ()
- from hundate import ezdate as d \
   Reference: d.text2date ()
- from hundate.ezdate import text2date \
   Reference: text2date ()

## Area of ​​application
- NLP applications, date extraction, interpretation of natural language phrases
- chatbot applications

## Abilities
- interpretation of relational date expressions
- contextual date determinations
- can handle complex and even multiple embedded date expressions
- handles textual numbers, Roman numerals, serial numbers, conjugations and synonyms related to dates
- in addition to individual dates, the algorithm recognizes date ranges

**What can't handle**:
- only date identification, does not handle intraday periods and hour-minute timings
- optimized for handling input of limited size (up to a few sentences)

**Improvement options**:
- allow small misspellings when identifying date words (fuzzy search)

## Examples
- 'next weekend after Christmas'
- 'at the beginning of the third week of the second half of 2023'
- 'three days before Friday last week'
- 'in the middle of the last century', 'in the early 70's'
- 'in two years' time in October'
- 'two months ago, on the 5th'

  See examples in ezdate_teszt.py


## Functions in the module
- **text2date**(): ("Text to date") Translate Hungarian datetime expressions to special date or date range


## Details

**text2date** (text, dt0=None, context = '', outtype = 'first'):
- **text**: usually a multi-word expression or sentence
        The sentence can contain words other than timestamps and numbers (the date can be anywhere within the text).
- **dt0**: the starting date for relational date definitions.
        If not specified, it is today.
- **tense**: 'future' / 'past'. In case of unclear timings, the function should prefer a future or past date
- **outtype**:
    - '**first**': return = '', '2021.10.12', '2021.12.10-2021.12.20' The first occurring date or date range.
    - '**first+**': same as first, but also enters the pattern and the output value of wildcards at the end of the string.
              Example: '2021.10.12 pattern: [number] [month name] [number] outvalues: [2021,' October ',' twelfth ']
    - '**all**': '2021.10.12,2021.12.10-2021.12.20'
