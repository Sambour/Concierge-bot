import subprocess

parameters = ['scasp', 'data/info_list.pl', 'data/state.pl', 'src/functions.pl', '-n1']
call = subprocess.Popen(
    parameters, stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
    text=True, universal_newlines=True
    )

output, _ = call.communicate(timeout=10800)