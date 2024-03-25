from colorama import Fore, Style
from call_gpt import predicate_gen, sentence_diversity, sentence_gen, chat, query_confirm, change_mind_confirm, irrelevant_reply
from reasoner import reasoner
from filter import get_predicates, filter

paths = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions.pl', 'src/update.pl', 'src/preference.pl', 'src/extra_preference.pl', 'src/results.pl', 'data/log.pl', 'src/query.pl']

attrs, values = get_predicates()
r = reasoner(paths)

session_continues = True
mode = 'recommend'
confirm = ''
reply = 'Hello what can I do for you?'
while(session_continues):
    reply = sentence_diversity(reply).strip()
    print('\n' + Fore.YELLOW + 'Bot:' + Style.RESET_ALL)
    if confirm:
        print(confirm + ' ' + reply + Fore.CYAN + '\n\nYou: ' + Style.RESET_ALL)
        confirm = ''
    else:
        print(reply + Fore.CYAN + '\n\nYou: ' + Style.RESET_ALL)
    query = input()
    
    if mode == 'ask':
        query = '[begin context] ' + reply + ' [end context] ' + query
    query_predicates = predicate_gen(query).strip()
    print(Fore.GREEN + '\n[extracted semantics] ' + Style.RESET_ALL + query_predicates)
    
    query_predicates = filter(query_predicates, attrs, values)

    if query_predicates == 'quit.':
        session_continues = False
        print('\n' + Fore.YELLOW + 'Bot:' + Style.RESET_ALL + '\n' + chat(query + 'Please quit.'))
        continue

    if query_predicates == 'irrelevant.':
        #irr_reply = chat(query)
        #irr_reply = irrelevant_reply(query)
        irr_reply = 'Sorry, I am just a concierge suggesting venues for foods and drinks. For other things, please ask other people for help.'
        if mode == 'ask':
            reply = irr_reply + reply
        else:
            reply = irr_reply + ' What can I help you with?'
    elif query_predicates == 'thank.':
        reply = 'You are welcome. It\'s my pleasure to help. What else can I help you?'
    else:
        reply_predicates = r.reason(query_predicates)
        if not reply_predicates:
            reply = 'Sorry could you please say that again?'
        elif type(reply_predicates) == dict and 'Success' in reply_predicates:
            reply = 'Sorry, but we can\'t find the result for your requirement. We can find result with ' + reply_predicates['Success'] + ', but no venue has ' + reply_predicates['Fail'] + '.'
            mode = 'recommend'
        else:
            confirm = query_confirm(query_predicates)
            mode = reply_predicates['Mode']
            if mode == 'change':
                mode = 'ask'
                print(Fore.GREEN + '\n[preference confirming] ' + Style.RESET_ALL + reply_predicates['Output'])
                reply = change_mind_confirm(reply_predicates['Output'])

            if mode == 'ask':
                reply = 'Do you have any preference for the ' + reply_predicates['Output'] + ' of the place?'
            
            if mode == 'recommend':
                reply = sentence_gen(reply_predicates['Output'][1:-1]).strip() + ' Do you like it?'
