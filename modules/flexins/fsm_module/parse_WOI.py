import textfsm

fsm = textfsm.TextFSM(open('trial.fsm'))
text_output = '\n'.join(open('ZWOI.txt'))
print fsm.ParseText(text_output)
