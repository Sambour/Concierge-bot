import subprocess
import utils
from preference import get_prefer

class reasoner():
    def __init__(self, paths):
        self.instant_path = paths[0]
        self.memory_path = paths[1]
        self.knowledge_path = paths[2]
        self.function_path = paths[3]
        self.update_path = paths[4]
        self.preference_path = paths[5]
        self.extra_preference_path = paths[6]
        self.result_path = paths[7]
        self.review_path = paths[8]
        self.command_path = paths[9]

        with open(self.memory_path, 'w') as f:
            f.write('')
        
        with open(self.result_path, 'w') as f:
            f.write('')

        with open(self.review_path, 'w') as f:
            f.write('')
    

    def call(self, options: list, num_result):
        
        parameters = ['scasp']
        parameters.extend(options)
        parameters.append(num_result)
        call = subprocess.Popen(
            parameters, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
            text=True, universal_newlines=True
            )
        
        output, _ = call.communicate(timeout=10800)

        if 'BINDINGS' in output:
            if num_result == '-n1':
                output = output[output.find('BINDINGS') + 10:-2].strip()
                output = output.split('\n')
                output = [item.split(' = ') for item in output]
                output = {name:value.strip() for [name, value] in output}
            elif num_result == '-n0':
                options = []
                output = output.split('ANSWER:')[1:]
                for option in output:
                    opt = option[option.find('BINDINGS') + 10:-2].strip()
                    opt = opt.split('\n')
                    opt = [item.split(' = ') for item in opt]
                    opt = {name:value.strip() for [name, value] in opt}
                    options.append(opt)
                output = options
        elif 'no models' in output:
            output = {}
        
        else:
            output = None

        return output 
    
    
    def reason(self, input):
        '''
        input style: aAA(aaa), bBB(bbb), cCC(ccc)
        output style: a dict of mode and output. None for error cases.
        '''
        
        # write the input to the file.
        with open(self.instant_path, 'w') as f:
            f.write(utils.new_query(input) + '\n')
        # update state memory
        state = ''
        prefer = ''
        change = ''
        # update query
        with open(self.command_path, 'w') as f:
            f.write('?- next_query(X).\n')
        output = self.call([self.instant_path, self.memory_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('query', output)
        # update preference
        with open(self.command_path, 'w') as f:
            f.write('?- next_prefer(X).\n')
        output = self.call([self.instant_path, self.memory_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('prefer', output)
        prefer = [list(item.values())[0] for item in output]
        with open(self.command_path, 'w') as f:
            f.write('?- next_not_prefer(X).\n')
        output = self.call([self.instant_path, self.memory_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('not_prefer', output)
        prefer.extend([list(item.values())[0] for item in output])

        #update preference rules
        prefer = list(set(prefer))
        add_prefer_rule = get_prefer(self.preference_path, prefer)
        with open(self.extra_preference_path, 'w') as f:
            f.write(add_prefer_rule)
        
        # update requirements
        with open(self.command_path, 'w') as f:
            f.write('?- next_require(Attr, Value).\n')
        output = self.call([self.instant_path, self.memory_path, self.preference_path, self.extra_preference_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('require', output)
        with open(self.command_path, 'w') as f:
            f.write('?- next_not_require(Attr, Value).\n')
        output = self.call([self.instant_path, self.memory_path, self.preference_path, self.extra_preference_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('not_require', output)
        # update another_option and view_history
        with open(self.command_path, 'w') as f:
            f.write('?- next_another_option(X).\n')
        output = self.call([self.instant_path, self.memory_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('another_option', output)
        with open(self.command_path, 'w') as f:
            f.write('?- next_answer_current(X).\n')
        output = self.call([self.instant_path, self.memory_path, self.update_path, self.command_path], '-n0')
        state += utils.concat_preds('answer_current', output)

        # change mind check
        with open(self.command_path, 'w') as f:
            f.write('?- change_req(Attr, Value).\n')
        output = self.call([self.instant_path, self.memory_path, self.preference_path, self.extra_preference_path, self.update_path, self.command_path], '-n0')
        change = utils.concat_preds('ask_still_want', output)
        with open(self.command_path, 'w') as f:
            f.write('?- change_prefer(X).\n')
        output = self.call([self.instant_path, self.memory_path, self.preference_path, self.extra_preference_path, self.update_path, self.command_path], '-n0')
        change += utils.concat_preds('ask_still_prefer', output)

        if state:
            cur_state = state
        else:
            return None
        
        with open(self.memory_path, 'w') as f:
            f.write(cur_state + '\n')

        # view the history recommendation
        with open(self.command_path, 'w') as f:
            f.write('?- view_history(X).\n')
        history = self.call([self.instant_path, self.command_path], '-n1')
        if history:
            with open(self.command_path, 'w') as f:
                f.write('?- view(' + history['X'] + ', I, State).\n')
            current_view = self.call([self.function_path, self.review_path, self.command_path], '-n1')
            if current_view:
                with open(self.command_path, 'w') as f:
                    f.write('?- history(I, State).\n')
                histories = self.call([self.review_path, self.command_path], '-n0')
                histories = utils.concat_preds('history', histories)
                histories += '\ncurrent(' + current_view['I'] + ').\n'
                with open(self.review_path, 'w') as f:
                    f.write(histories)
                return {'Mode':'recommend', 'Output':current_view['State']}
            else:
                return None
        
        # ask if change mind
        if change:
            output = {'Mode':'change', 'Output':change}
            return output
        
        # do the recommendation
        with open(self.command_path, 'w') as f:
            f.write('?- next_action(Mode, Output).\n')
        results = self.call([self.memory_path, self.knowledge_path, self.function_path, self.result_path, self.command_path], '-n0')

        # save the results to result path.
        if results:
            output = results[0]
            if output['Mode'] == 'recommend':
                numbers = [result['Output'] for result in results]
                res = []
                [res.append(x) for x in numbers if x not in res]
                numbers = res
                selected = numbers[0]
                numbers.remove(selected)
                numbers_str = ''
                numbers_str += 'current(' + selected + ').\n'
                for number in numbers:
                    numbers_str += 'result(' + number + ').\n'
                with open(self.result_path, 'w') as f:
                    f.write(numbers_str)

        # check and explain
        
        if output and ('Output' not in output or not output['Output']):
            return None
        if output and output['Mode'] == 'recommend':
            # Looking up the queried information of the result place.
            with open(self.command_path, 'w') as f:
                f.write('?- look_up(' + output['Output'] + ', Attr, Value).\n')
            recommend_output = self.call([self.memory_path, self.knowledge_path, self.function_path, self.command_path], '-n0')
            recommend_output = utils.concat_preds('recommend', recommend_output)

            # Querying for explanation
            with open(self.command_path, 'w') as f:
                f.write('?- explain(' + output['Output'] + ', Attr, Value).\n')
            explain = self.call([self.memory_path, self.knowledge_path, self.extra_preference_path, self.preference_path, self.function_path, self.command_path], '-n0')
            explain = utils.concat_preds('satisfy_require', explain)
            
            output = recommend_output + explain
            output = {'Mode':'recommend', 'Output':output}

            # Update the review file.
            with open(self.command_path, 'w') as f:
                f.write('?- history(I, State).\n')
            history = self.call([self.review_path, self.command_path], '-n0')
            if history:
                history_str = utils.concat_preds('history', history)
                current = len(history) + 1
                history_str += ' history(' + str(current) + ', [' + output['Output'].replace('.', ',').strip(', ') + ']).\n'
                history_str += 'current(' + str(current + 1) + ').\n'
            else:
                history_str = 'history(' + str(1) + ', [' + output['Output'].replace('.', ',').strip(', ') + ']).\n'
                history_str += 'current(' + str(2) + ').\n'
            with open(self.review_path, 'w') as f:
                f.write(history_str)

            with open(self.command_path, 'w') as f:
                f.write('')
        
        if output == {}:
            # Querying for explanation
            with open(self.command_path, 'w') as f:
                f.write('?- explain_fail(Success, Fail).\n')
            explain = self.call([self.memory_path, self.knowledge_path, self.function_path, self.command_path], '-n1')
            output = {'Success':explain['Success'][1:-1], 'Fail':explain['Fail']}

        return output


if __name__ == "__main__":
    names = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions.pl', 'src/update.pl', 'src/preference.pl', 'src/extra_preference.pl', 'src/results.pl', 'data/log.pl', 'src/query.pl']
    r = reasoner(names)
    
    prefer = ['kebob']
    print(get_prefer(r.preference_path, prefer))