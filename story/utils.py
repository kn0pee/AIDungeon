 # coding: utf-8
import re
import yaml
from difflib import SequenceMatcher

YAML_FILE = "story/story_data.yaml"

from profanityfilter import ProfanityFilter
with open("story/extra_censored_words.txt", "r") as f:
    more_words = [l.replace("\n", "") for l in f.readlines()]

pf = ProfanityFilter(extra_censor_list=more_words)

def console_print(text, width=75):
    last_newline = 0
    i = 0
    while i < len(text):
        if text[i] == "\n":
            last_newline = 0
        elif last_newline > width and text[i] == " ":
            text = text[:i] + "\n" + text[i:]
            last_newline = 0
        else:
            last_newline += 1
        i += 1
    print(text)

def get_similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def get_num_options(num):

    while True:
        choice = input("Enter the number of your choice: ")
        try:
            result = int(choice)
            if result >= 0 and result < num:
                return result
            else:
                print("Error invalid choice. ")
        except ValueError:
            print("Error invalid choice. ")


def player_died(text):

    # reg_phrases = ["You[a-zA-Z ]* die.", "you[a-zA-Z ]* die.", "You[a-zA-Z ]* die ", "you[a-zA-Z ]* die ",]
    #
    # for phrase in reg_phrases:
    #     reg_expr = re.compile(phrase)
    #     matches = re.findall(reg_expr, text)
    #     if len(matches) > 0:
    #         return True

    dead_phrases = ["you die", "You die", "you died", "you are dead", "You died", "You are dead", "You're dead",
                    "you're dead", "you have died", "You have died", "you bleed out"]
    for phrase in dead_phrases:
        if phrase in text:
            return True
    return False

def player_won(text):

    won_phrases = ["live happily ever after", "you live forever"]
    for phrase in won_phrases:
        if phrase in text:
            return True
    return False

def remove_profanity(text):
    return text #pf.censor(text)


def cut_trailing_quotes(text):
    num_quotes = text.count('"')
    if num_quotes % 2 is 0:
        return text
    else:
        final_ind = text.rfind('"')
        return text[:final_ind]

    
def split_first_sentence(text):
    first_period = text.find('.')
    first_exclamation = text.find('!')
    
    if first_exclamation < first_period and first_exclamation > 0:
        split_point = first_exclamation+1
    elif first_period > 0:
        split_point = first_period+1
    else:
        split_point = text[0:20]
        
    return text[0:split_point], text[split_point:]

def cut_trailing_action(text):
    lines = text.split("\n")
    last_line = lines[-1]
    if "you ask" in last_line or "You ask" in last_line or "you say" in last_line or "You say" in last_line:
        text = "\n".join(lines[0:-1])
    return text
    
def cut_trailing_sentence(text):
    text = standardize_punctuation(text)
    last_punc = max(text.rfind('.'), text.rfind("!"), text.rfind("?"))
    if last_punc <= 0:
        last_punc = len(text)-1

    et_token = text.find("<")
    if et_token > 0:
        last_punc = min(last_punc, et_token-1)

    act_token = text.find(">")
    if act_token > 0:
        last_punc = min(last_punc, act_token-1)

    text = text[:last_punc]

    text = cut_trailing_quotes(text)
    text = cut_trailing_action(text)
    return text


def replace_outside_quotes(text, current_word, repl_word):
    text = standardize_punctuation(text)

    reg_expr = re.compile(current_word + '(?=([^"]*"[^"]*")*[^"]*$)')

    output = reg_expr.sub(repl_word, text)
    return output


def is_first_person(text):

    count = 0
    for pair in first_to_second_mappings:
        variations = mapping_variation_pairs(pair)
        for variation in variations:
            reg_expr = re.compile(variation[0] + '(?=([^"]*"[^"]*")*[^"]*$)')
            matches = re.findall(reg_expr, text)
            count += len(matches)

    if count > 3:
        return True
    else:
        return False


def is_second_person(text):
    count = 0
    for pair in second_to_first_mappings:
        variations = mapping_variation_pairs(pair)
        for variation in variations:
            reg_expr = re.compile(variation[0] + '(?=([^"]*"[^"]*")*[^"]*$)')
            matches = re.findall(reg_expr, text)
            count += len(matches)

    if count > 3:
        return True
    else:
        return False


def capitalize(word):
    return word[0].upper() + word[1:]
    

def mapping_variation_pairs(mapping):
    mapping_list = []
    mapping_list.append((" " + mapping[0]+" ", " " + mapping[1]+" "))
    mapping_list.append((" " + capitalize(mapping[0]) + " ", " " + capitalize(mapping[1]) + " "))

    # Change you it's before a punctuation
    if mapping[0] is "you":
        mapping = ("you", "me")
    mapping_list.append((" " + mapping[0]+",", " " + mapping[1]+","))
    mapping_list.append((" " + mapping[0]+"\?", " " + mapping[1]+"\?"))
    mapping_list.append((" " + mapping[0]+"\!", " " + mapping[1]+"\!"))
    mapping_list.append((" " + mapping[0] + "\.", " " + mapping[1] + "."))

    return mapping_list


first_to_second_mappings = [
    ("I'm", "you're"),
    ("Im", "you're"),
    ("Ive", "you've"),
    ("I am", "you are"),
    ("was I", "were you"),
    ("am I", "are you"),
    ("wasn't I", "weren't you"),
    ("I", "you"),
    ("I'd", "you'd"),
    ("i", "you"),
    ("I've", "you've"),
    ("was I", "were you"),
    ("am I", "are you"),
    ("wasn't I", "weren't you"),
    ("I", "you"),
    ("I'd", "you'd"),
    ("i", "you"),
    ("I've", "you've"),
    ("I was", "you were"),
    ("my", "your"),
    ("we","you"),
    ("we're", "you're"),
    ("mine","yours"),
    ("me", "you"),
    ("us", "you"),
    ("our", "your"),
    ("I'll", "you'll"),
    ("myself", "yourself")
]

second_to_first_mappings = [
    ("you're", "I'm"),
    ("your", "my"),
    ("you are", "I am"),
    ("you were", "I was"),
    ("are you", "am I"),
    ("you", "I"),
    ("you", "me"),
    ("you'll", "I'll"),
    ("yourself", "myself"),
    ("you've", "I've")
]

def capitalize_helper(string):
    string_list = list(string)
    string_list[0] = string_list[0].upper()
    return "".join(string_list)


def capitalize_first_letters(text):
    first_letters_regex = re.compile(r'((?<=[\.\?!]\s)(\w+)|(^\w+))')

    def cap(match):
        return (capitalize_helper(match.group()))

    result = first_letters_regex.sub(cap, text)
    return result

def standardize_punctuation(text):
    text = text.replace("’", "'")
    text = text.replace("`", "'")
    text = text.replace('“', '"')
    text = text.replace('”', '"')
    return text


def first_to_second_person(text):
    text = " " + text
    text = standardize_punctuation(text)
    for pair in first_to_second_mappings:
        variations = mapping_variation_pairs(pair)
        for variation in variations:
            text = replace_outside_quotes(text, variation[0], variation[1])

    return capitalize_first_letters(text[1:])

def second_to_first_person(text):
    text = " " + text
    text = standardize_punctuation(text)
    for pair in second_to_first_mappings:
        variations = mapping_variation_pairs(pair)
        for variation in variations:
            text = replace_outside_quotes(text, variation[0], variation[1])

    return capitalize_first_letters(text[1:])