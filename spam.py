from groq import Groq
from enum import Enum
from pydantic import BaseModel
import pandas as pd
import instructor
from tqdm import tqdm


class AcceptOrReject(Enum):
    accept = 1
    denied = 0

class FinalOut(BaseModel):
    result : AcceptOrReject

def granted_rejected(case, patched_client, AcceptOrReject):
    chat=patched_client.chat.completions.create(
        model='llama-3.3-70b-versatile',
        messages = [{'role': 'system', 'content': 'You are tasked with finding if the plantiffs request will be accepted or rejected. You will be provided with case details and you have to decide. If you believe that the request will be accepted then output 1 else output 0'},
                    {'role': 'user', 'content' : case}],
        response_model = AcceptOrReject,
    )
    return chat.result.value


def summarize_case(case, client):
    chat = client.chat.completions.create(
        model='meta-llama/llama-4-scout-17b-16e-instruct',
        messages=[{'role' : 'system', 'content': 'You have the responsibility to summarize legal cases in the most unbiased way possible. Remove the verdict from the case when summarizing and put an emphasis on facts'},
                  {'role' : 'user', 'content': case}],
        temperature=0.5,
        max_completion_tokens=8000,
    )
    return chat.choices[0].message.content

if __name__ == '__main__':
    client = Groq(api_key='')
    patched_client = instructor.from_groq(client)
    df = pd.read_csv('/Users/yash/Downloads/cases_final.csv')
    sample_list = []
    for i in tqdm(range(35, len(df['text']))):
        summary = summarize_case(df['text'][i], client)
        out = granted_rejected(summary, patched_client, FinalOut)
        sample_list.append({'ID' : df['id'][i], 'VERDICT' : out})
        print(out)
        df1 = pd.DataFrame(sample_list)
        df1.to_csv('./spam2.csv')
        if i > 50:
            break
    df1 = pd.DataFrame(sample_list)
    df1.to_csv('./spam2.csv')

