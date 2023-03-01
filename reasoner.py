import subprocess
import utils
import re

class reasoner():
    def __init__(self, paths):
        self.instant_path = paths[0]
        self.memory_path = paths[1]
        self.knowledge_path = paths[2]
        self.function_path = paths[3]
        self.result_path = paths[4]
        self.command_path = paths[5]

        with open(self.memory_path, 'w') as f:
            f.write('state([]).\n')
    
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

        # if querying for the next choice, just go next
        if input == 'another_option':
            with open(self.command_path, 'w') as f:
                f.write('?- load(Mode, Output).\n')
            output = self.call([self.knowledge_path, self.memory_path, self.function_path, self.result_path, self.command_path], '-n1')
            if output:
                with open(self.result_path, 'r') as f:
                    options = f.readlines()
                with open(self.result_path, 'w') as f:
                    f.writelines(options[1:])
        
        else:
            # write the input to the file.
            with open(self.instant_path, 'w') as f:
                f.write('info_list([' + input + ']).\n')
            with open(self.result_path, 'w') as f:
                f.write('')
            # update state memory
            with open(self.command_path, 'w') as f:
                f.write('?- info_list(L1), state(L2), write_state(L1, L2, State).\n')
            output = self.call([self.instant_path, self.memory_path, self.function_path, self.command_path], '-n1')

            if output:
                m_cur_state = ''
                cur_state = output['State']
                cur_state = cur_state.split('),')
                for pred in cur_state:
                    pred_part = pred.split(',[')
                    value_part = pred_part[1]
                    pred_part = pred_part[0].split('(')
                    m_cur_state += pred_part[0] + '(' + utils.add_quote(pred_part[1].strip()) + ',[' \
                        + ','.join([utils.add_quote(value.strip().strip(']')) for value in value_part.split(',')]) + ']),'
                cur_state = m_cur_state[:-6] + '\'])]'
            else:
                return None
            
            with open(self.memory_path, 'w') as f:
                f.write('state(' + cur_state + ').\n')
            
            # do the recommendation
            with open(self.command_path, 'w') as f:
                f.write('?- next_action(Mode, Output).\n')
            output = self.call([self.memory_path, self.knowledge_path, self.function_path, self.command_path], '-n0')

            # save the other results to result path.
            if output:
                result_list = output
                output = result_list[0]
                if output['Mode'] == 'recommend':
                    if len(result_list) > 1:
                        result_list = [result for result in result_list if result['Output'] != '[]']
                        numbers = [re.findall(r'\d+', result['Output'])[0] for result in result_list]
                        selected = numbers[0]
                        numbers = list(set(numbers))
                        numbers.remove(selected)
                        if numbers:
                            for number in numbers:
                                with open(self.result_path, 'a') as f:
                                    f.write('result(' + number + ').\n')

        # check and explain
        
        if output and ('Output' not in output or not output['Output']):
            return None
        if output and output['Mode'] == 'recommend':
            # The following steps are basically adding quote mark to the predicate values so that they can be accepted by scasp.
            recommend_output = output['Output'].strip('[]')
            recommend_output = utils.split_predicate(recommend_output)
            recommend_output = [utils.split_attr_value(pred) for pred in recommend_output]
            recommend_output_attr = [pred[0] for pred in recommend_output]
            recommend_output_values = [pred[1].split(',') for pred in recommend_output]
            recommend_output_values = [[values[0].strip(), utils.add_quote(values[1].strip()), utils.add_quote(','.join(values[2:]).strip())] for values in recommend_output_values]
            recommend_output = ''
            for idx in range(len(recommend_output_attr)):
                recommend_output += recommend_output_attr[idx] + '(' + ','.join(recommend_output_values[idx]) + '), '
            recommend_output = recommend_output.strip(', ')
            recommend_output = '[' + recommend_output + ']'

            # Querying for explanation
            with open(self.command_path, 'w') as f:
                f.write('?- explain(' + recommend_output + ', Output).\n')
            explain = self.call([self.memory_path, self.knowledge_path, self.function_path, self.command_path], '-n1')
            
            output = '[' + output['Output'][1:-1] + ', ' + explain['Output'][1:-1] + ']'
            output = {'Mode':'recommend', 'Output':output}

            with open(self.command_path, 'w') as f:
                f.write('')

        return output


if __name__ == "__main__":
    names = ['data/info_list.pl', 'data/state.pl', 'data/knowledge.pl', 'src/functions.pl', 'src/query.pl']
    r = reasoner(names)
    output = r.call(['data/info_list.pl', 'data/state.pl', 'src/functions.pl', 'src/query.pl'], '-n0')
    
    m_cur_state = ''
    cur_state = output['State']
    cur_state = cur_state.split('),')
    for pred in cur_state:
        pred_part = pred.split(',')
        m_cur_state += pred_part[0] + ',\'' + pred_part[1] + '\'),'
    cur_state = m_cur_state[:-2]
    print(cur_state)