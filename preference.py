from call_gpt import preference_classify
from utils import add_quote


def extract_prefer_preds(path):
    with open(path, 'r') as f:
        lines = f.readlines()
    
    classes = []
    for line in lines:
        if line.startswith('entail') and 'food type' in line:
            classes.append(line.split("'food type', ")[1].strip(').'))
    
    return classes


def get_prefer(preference_path, prefer_list):
    classes = extract_prefer_preds(preference_path)
    output = ''
    for p in prefer_list:
        if p not in classes:
            cuisines = preference_classify(', '.join(classes), p)
            cuisines = [x.strip() for x in cuisines.split(',')]
            cuisines = [x for x in cuisines if x]
            prefer = add_quote(p)
            for c in cuisines:
                cuisine = add_quote(c)
                pos_rule = "new_require('food type', " + cuisine + ") :- new_prefer(" + prefer + "), not not_require('food type', " + cuisine + ").\n"
                neg_rule = "new_not_require('food type', " + cuisine + ") :- new_not_prefer(" + prefer + "), not require('food type', " + cuisine + ").\n"
                ent_rule = "entail(prefer(" + prefer + "), require('food type', " + cuisine + ")).\n"

                output += pos_rule + neg_rule + ent_rule
    return output