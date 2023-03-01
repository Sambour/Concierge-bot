from call_gpt import predicate_gen, sentence_diversity, sentence_gen
from reasoner import reasoner
from filter import get_predicates, filter

paths = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions.pl', 'src/results.pl', 'src/query.pl']

attrs, values = get_predicates()
r = reasoner(paths)

session_continues = True
mode = 'recommend'
reply = 'Hello what can I do for you?'
while(session_continues):
    reply = sentence_diversity(reply).strip()
    print('\nBot:\n' + reply + '\n\nYou: ')
    query = input()
    if query == 'end':
        session_continues = False
        continue
    
    if mode == 'ask':
        query = reply + query
    query_predicates = predicate_gen(query).strip()
    query_predicates = filter(query_predicates, attrs, values)

    if query_predicates == 'irrelevant':
        reply = 'Sorry, I am only a concierge helping with recommending restaurants, pubs, food shops, etc., could you please repeat what you are looking for?'
    elif query_predicates == 'thank':
        reply = 'You are welcome. It\'s my pleasure to help.'
    else:
        reply_predicates = r.reason(query_predicates)
        if reply_predicates == {}:
            reply = 'Sorry, but we can\'t find the result for your requirement.'
        elif not reply_predicates:
            reply = 'Sorry could you please say that again?'
        else:
            mode = reply_predicates['Mode']
            if mode == 'ask':
                reply = 'Do you have any preference for the ' + reply_predicates['Output'] + ' of the place?'
            
            if mode == 'recommend':
                reply = sentence_gen(reply_predicates['Output'][1:-1]).strip()
