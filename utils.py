from pyparsing import Forward, Word, nestedExpr, alphanums

def parse_predicates(pred_str):
    pred = pred_str.split('(')
    values = pred[1].split(',')
    pred = pred[0]
    values[-1] = values[-1].strip(')')
    values = [value.strip() for value in values]
    return pred, values

def add_quote_pos(pred:str, pos):
    attr, values = parse_predicates(pred)
    values[pos] = add_quote(values[pos])
    return attr + '(' + ', '.join(values) + ')'

def add_quote(item):
    item = item.replace('\'', '\\\'')
    if item.isdigit():
        return item
    return '\'' + item + '\''

def parsing_states(item):
    enclosed = Forward()
    nestedParens = nestedExpr('(', ')', content=enclosed) 
    nestedBrackets = nestedExpr('[', ']', content=enclosed) 
    #enclosed << (nestedParens)
    enclosed << (Word(alphanums+'._ -+\'?!&') | ',' | nestedParens | nestedBrackets)
    return enclosed.parseString(item).asList()

def add_quote_state(item):
    nested = parsing_states(item)
    for states in nested:
        str_values = []
        state = [v for v in states if type(v) == list]
        attr = [a for a in states if type(a) != list and a != ',']
        for values in state:
            added_value = []
            for value in values:
                if type(value) != list:
                    if value != ',':
                        added_value.append(add_quote(value))
                else:
                    sub_str_values = []
                    sub_state = [v for v in value if type(v) == list]
                    sub_attr = [a for a in value if type(a) != list and a != ',']
                    for sub_values in sub_state:
                        sub_added_value = []
                        for sub_value in sub_values:
                            if sub_value != ',':
                                sub_added_value.append(sub_value)
                        sub_str_values.append('(' + add_quote(sub_added_value[0]) + ',' + add_quote(sub_added_value[1]) + ',' + add_quote(', '.join((sub_added_value[2:]))) + ')')
                    sub_sentences = [sub_attr[i] + sub_str_values[i] for i in range(len(sub_attr))]
                    added_value.append('[' + ','.join(sub_sentences) + ']')
            str_values.append('(' + ','.join(added_value) + ')')
        sentences = [attr[i] + str_values[i] for i in range(len(attr))]
        sentences = list(set(sentences))
    return '.\n'.join(sentences) + '.' if sentences else ''

def split_predicate(preds):
    '''
    input: a string of predicates separated by ','
    '''
    preds = preds.split(')')
    preds.remove('')
    preds = [pred + ')' for pred in preds]
    preds = [pred.strip(', ') for pred in preds]
    return preds

def split_attr_value(pred):
    '''
    input: a predicate
    '''
    pred = pred.split('(')
    attr = pred[0]
    values = pred[1].strip(')')
    return (attr, values)

def new_query(input):
    '''
    input: a string of predicates separated by '.'
    '''
    preds = input.split('.')
    preds = [pred.strip() for pred in preds]
    new_preds = []
    for pred in preds[:-1]:
        if pred.startswith('another_option') or pred.startswith('view_history'):
            new_preds.append(pred)
        else:
            new_preds.append('new_' + pred)
    return '. '.join(new_preds) + '.'

def concat_preds(pred, values):
    '''
    concatenate the predicate name with its values to get the full formatted predicate.
    pred: predicate name.
    values: a list of predicate values.
    '''
    result = ''
    value_list = []
    if not values:
        return result
    for item in values:
        value_list.append(',,,'.join(list(item.values())))
    value_list = list(dict.fromkeys(value_list))
    value_list = [item.split(',,,') for item in value_list]
    for item in value_list:
        result += pred + '(' + ','.join([add_quote(value) for value in item]) + '). '
    return result

if __name__ == '__main__':
    #nested_list = add_quote_state("[history(1,[recommend(16,name,Papa Johns),recommend(16,address,2770 Waterview Pkwy, Richardson, TX 75080),recommend(16,distance,in campus),satisfy_require(16,food type,pizza),satisfy_require(16,price range,cheap),satisfy_require(16,customer rating,low)]),hist_current(2)]")
    nested_list = add_quote_state("[former_state(query,name,None),former_state(query,address,None),former_state(query,distance,None),former_state(require,food type,pizza),former_state(require,price range,cheap),former_state(require,customer rating,low)]")
    print(nested_list)