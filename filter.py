import pandas as pd
from sys import argv

from utils import add_quote

def get_predicates():
    '''
    This step generates the restaurants' information from a .csv file.
    It also returns all the predicate names as well as their values.
    '''
    data = pd.read_csv('data/knowledge.csv')
    attrs = list(data.columns)[1:]
    context = ''
    context_list = []

    for index, row in data.iterrows():
        for attr in attrs:
            if attr == 'open hours':
                for value in values:
                    context += 'place' + '(' + str(index) + ',\'' + attr + '\',\'' + str(row[attr]) + '\'). '
                    context_list.append([attr, index, row[attr]])
            else:
                values = str(row[attr])
                values = values.split('*/*')
                for value in values:
                    context += 'place' + '(' + str(index) + ',\'' + attr + '\',\'' + value + '\'). '
                    context_list.append([attr, index, row[attr]])
        context += '\n'

    # Write down the knowledge base to prolog format. The only place to generate knowledge base.
    with open('data/knowledge.pl', 'w') as f:
        f.write(context)
    
    return attrs, context_list


def match_predicates(attr:str, values:list):
    if attr.startswith('not '):
        attr = attr[4:]
        return 'not_require(' + add_quote(attr) + ',[' + ','.join([add_quote(x) for x in values]) + '])'
    else:
        return 'require(' + add_quote(attr) + ',[' + ','.join([add_quote(x) for x in values]) + '])'


def parse_predicates(inputs:str, attrs, values):
    '''
    Parse the string of input predicates.
    Only accept a series of predicates such as 'aaa(bbb), ccc(ddd), ..., mmm(nnn)'.
    This parsing step only check whether the predicate name is valid.
    Any deep syntax check should be done by prolog/s(CASP) itself.
    '''
    attrs = [x + '(' for x in attrs]
    attrs.append('prefer(')
    attrs.append('another_option(')

    # Only accept a series of predicates such as 'aaa(bbb), ccc(ddd), ..., mmm(nnn)'.
    preds = inputs.split(')')
    output = ''
    for pred in preds:
        pred = pred.strip(',').strip()
        pred_dict = {}

        # Make sure that the predicate name is valid.
        in_list = any([pred.startswith(x) for x in attrs]) or any([pred.startswith('not ' + x) for x in attrs])
        if in_list:
            pred_split = pred.split('(')
            pred_values = pred_split[1].split(', ')
            pred_values = [x.strip() for x in pred_values]
            if pred_split[0] not in pred_dict:
                pred_dict[pred_split[0]] = []
            pred_dict[pred_split[0]].extend(pred_values)
        else:
            continue
        
        # The case when querying for another available recommendation:
        # If only querying for next choice without extra requirements, respond it;
        # otherwise, ignore the next option request, i.e. update the requirement and search again.
        if len(pred_dict) == 1 and 'another_option' in pred_dict:
            return 'another_option'
        elif 'another_option' in pred_dict:
            pred_dict.pop('another_option')
        
        # Generate the 'require()' predicate sequence.
        for pred in pred_dict:
            p_pred = match_predicates(pred, pred_dict[pred])
            if p_pred:
                output += p_pred + ', '
    if output:
        output = output.strip(', ')
    return output

def filter(input, attrs, values):
    '''
    Has three return status: 
    appreciation, which returns 'appreciation'
    predicates, which directly gives the predicates;
    irrelevant, where any non-predicate text is generated, or the predicates cannot be correctly parsed.
    '''
    
    if input == 'thank':
        return input
    preds = parse_predicates(input, attrs, values)
    if not preds:
        return 'irrelevant'
    else:
        return preds


if __name__ == "__main__":
    attrs, values = get_predicates()
    print(filter(argv[1], attrs, values))