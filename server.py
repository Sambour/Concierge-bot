import socket
from colorama import Fore, Style
from call_gpt import predicate_gen, sentence_diversity, sentence_gen, chat, query_confirm, change_mind_confirm
from reasoner_copy import reasoner
from filter import get_predicates, filter

paths = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions_copy.pl', 'src/update.pl', 'src/preference.pl', 'src/extra_preference.pl', 'src/results.pl', 'data/log.pl', 'src/query.pl']

attrs, values = get_predicates()

# get the hostname
host = "10.176.167.188"
port = 63315  # initiate port no above 1024

server_socket = socket.socket()  # get instance
# look closely. The bind() function takes tuple as argument
server_socket.bind((host, port))  # bind host address and port together

while(True):
    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    conn, address = server_socket.accept()  # accept new connection

    r = reasoner(paths)
    session_continues = True
    mode = 'recommend'
    confirm = ''
    reply = 'Hello what can I do for you?'
    while session_continues:
        #generate response
        reply = sentence_diversity(reply).strip()
        if confirm:
            response = confirm + ' ' + reply
            confirm = ''
        else:
            response = reply
        
        # send data to the client
        conn.send(response.encode())

        # receive data stream. it won't accept data packet greater than 1024 bytes
        query = conn.recv(4096).decode()
        if not query:
            # if data is not received break
            break
        
        if mode == 'ask':
            query = '[begin context] ' + reply + ' [end context] ' + query
        
        query_predicates = predicate_gen(query).strip()
        query_predicates = filter(query_predicates, attrs, values)

        reply_predicates = r.reason(query_predicates)

        if not reply_predicates:
            reply = 'Sorry could you please say that again?'
        else:
            mode = reply_predicates['Mode']
            if mode == 'quit':
                session_continues = False
                response = chat(query + ' Please quit.')
                conn.send(response.encode())
                continue
            elif mode == 'irrelevant':
                #irr_reply = chat(query)
                #irr_reply = irrelevant_reply(query)
                irr_reply = 'Sorry, I am just a concierge suggesting venues for foods and drinks. For other things, please ask other people for help.'
                if 'Question' in reply_predicates:
                    reply = irr_reply + ' Do you have any preference for the ' + reply_predicates['Question'] + ' of the place?'
                    mode = 'ask'
                else:
                    reply = irr_reply + ' What can I help you with?'
            elif mode == 'thank':
                thank_reply = 'You are welcome. It\'s my pleasure to help.'
                if 'Question' in reply_predicates:
                    reply = thank_reply + ' Do you have any preference for the ' + reply_predicates['Question'] + ' of the place?'
                    mode = 'ask'
                else:
                    reply = thank_reply + ' What can I help you with?'
            elif mode == 'fail':
                    reply = 'Sorry, but we can\'t find the result for your requirement. We can find result with ' + reply_predicates['Results'] + ', but no venue has ' + reply_predicates['Value'] + '.'
                    mode = 'recommend'
            else:
                confirm = query_confirm(query_predicates)
                if mode == 'change_mind':
                    mode = 'ask'
                    reply = change_mind_confirm(reply_predicates['Value'][1:-1])

                if mode == 'ask':
                    reply = 'Do you have any preference for the ' + reply_predicates['Value'] + ' of the place?'

                if mode == 'view_history':
                    reply = sentence_gen(reply_predicates['Value'][1:-1]).strip()
                
                if mode == 'recommend':
                    reply = sentence_gen(reply_predicates['Value'][1:-1]).strip() + ' Do you like it?'

    conn.close()  # close the connection