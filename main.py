from groq import Groq
import instructor
from pydantic import BaseModel
from enum import Enum
from utils import generate_response_router, generate_response_roleplay, role, format_response, summarize_case, granted_rejected
import json
import pandas as pd

"""
Creating a router LLM that applies its creativity on the structure and the flow 
of the case. It decides which next person to call, designs a prompt for the person according to the context
and changes/progresses the phase of the trial going on.
"""
outs = []
# Creating the custom Dtypes
class ChoiceForNextPerson(str, Enum):
    defendant = 'defendant'
    judge = 'judge'
    plaintiff = 'plaintiff'
    prosecutor = 'prosecutor'
    defence_attorney = 'defense attorney'
    expert_witness = 'expert witness'
    surprise_witness = 'surprise witness'
    juror = 'juror'
    courtroom_heckler = 'courtroom heckler'

class Phase(str, Enum):
    opening   = 'opening statements'
    inter_args  = 'witness interrogations and arguments'
    closing  = 'closing statements'
    verdict  = 'verdict'


class RouterStructuredOut(BaseModel):
    choice : ChoiceForNextPerson
    prompt : str
    phase : Phase

class AcceptOrReject(Enum):
    accept = 1
    denied = 0

class FinalOut(BaseModel):
    result : AcceptOrReject


# Creating the router LLM
client = Groq(
    api_key= ''
)

patched_client = instructor.from_groq(client)

cases_df = pd.read_csv('/Users/yash/Downloads/cases_final.csv')
for case in range(len(cases_df['text'])):
    summary = summarize_case(cases_df['text'][case], client)


    with open('router_prompt_new.txt', 'r') as f:
        router_init_prompt = f.read()

    with open('roleplay_init_prompt.txt', 'r') as f:
        roleplay_init_prompt = f.read()

    router_init_prompt = router_init_prompt + summary
    roleplay_init_prompt = roleplay_init_prompt + summary

    roleplay_context = [{'role': 'system', 'content': ''},
                        {'role': 'user', 'content': 'Begin the Simulation'}]
    router_context = [{'role': 'system', 'content': router_init_prompt},
                      {'role': 'user', 'content': 'Begin the Simulation'}]
    transcript = []
    roleplay_init_prompt_base = roleplay_init_prompt
    choice = None
    iters = 0

    while choice != 'verdict':
        choice, prompt, phase = generate_response_router(router_context, patched_client, RouterStructuredOut)
        roleplay_content = roleplay_init_prompt + role(prompt, phase)['content']
        roleplay_context[0] ={'role' : 'system', 'content': roleplay_content}
        response = generate_response_roleplay(roleplay_context, client)
        text_response = response
        response = format_response(response, choice)
        roleplay_context.append(response)
        router_context.append(response)
        transcript.append(response)
        roleplay_init_prompt = roleplay_init_prompt_base
        if len(roleplay_context) > 3:
            roleplay_context.pop(1)
        if len(router_context) > 3:
            router_context.pop(1)
        print(response)
        iters = iters + 1
        #TODO create LLM to make the verdict loop complete

    roleplay_context[0] = {'role': 'system', 'content': 'You are a decider. You have to decide between two things after analysing the context. If you see that the demands for the plantiff were accepted then output 1 and if they were not then output 0'}
    val = granted_rejected(roleplay_context, patched_client, FinalOut)

    with open('transcript.json', 'w') as f:
        json.dump(roleplay_context, f)

    with open('Case.txt', 'w') as f:
        for i in range(len(transcript)):
            f.write(f'{transcript[i]['content']}\n')

    outs.append({'ID': cases_df['id'][case], 'VERDICT': val})
    df_out = pd.DataFrame(outs, index = None)
    df_out.to_csv('hi.csv')