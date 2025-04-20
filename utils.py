from groq import Groq
from enum import Enum
from pydantic import BaseModel


def generate_response_router(messages, client, response_model):
    chat = client.chat.completions.create(
        model = 'meta-llama/llama-4-scout-17b-16e-instruct',
        messages = messages,
        response_model = response_model,
        temperature = 1,
        max_completion_tokens = 200,
    )
    choice = chat.choice.value
    prompt = chat.prompt
    phase = chat.phase.value
    return choice, prompt, phase

def generate_response_roleplay(messages, client):
    chat = client.chat.completions.create(
        model='meta-llama/llama-4-scout-17b-16e-instruct',
        messages=messages,
        temperature=1,
        max_completion_tokens=500,
    )
    return chat.choices[0].message.content

def role(prompt, phase):
    message = {'role': 'system', 'content': f'Phase: {phase}, Role: {prompt}'}
    return message

def format_response(response, choice):
    message = {'role': 'user', 'content': f'{choice}: {response}'}
    return message

def summarize_case(case, client):
    chat = client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages=[{'role' : 'system', 'content': 'You have the responsibility to summarize legal cases in the most unbiased way possible. Remove the verdict from the case when summarizing and put an emphasis on facts'},
                  {'role' : 'user', 'content': case}],
        temperature=0.5,
        max_completion_tokens=8000,
    )
    return chat.choices[0].message.content

def granted_rejected(order, patched_client, AcceptOrReject):
    chat=patched_client.chat.completions.create(
        model='llama-3.1-8b-instant',
        messages = order,
        response_model = AcceptOrReject,
    )
    return chat.result.value


if __name__ == '__main__':
    with open('./raw_case.txt', 'r') as f:
        content = f.read()
    client = Groq(
        api_key=''
    )
    summarize_case(content, client)


