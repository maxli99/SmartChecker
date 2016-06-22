import textfsm

fsm = textfsm.TextFSM(open('b6j.fsm'))
text_output = '\n'.join(open('ZB6J.txt'))
print fsm.ParseText(text_output)
