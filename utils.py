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
    return '\'' + item + '\''

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