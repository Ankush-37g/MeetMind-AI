from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.runnables import RunnablePassthrough, RunnableLambda

import os

def get_llm():
    return ChatMistralAI(api_key=os.getenv("MISTRAL_API_KEY"), model="mistral-small-latest", temperature=0.1)

def split_transcript(transcript: str)->list:

    splitter =  RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=3000,
        chunk_overlap=200,
    ) 

    return splitter.split_text(transcript)

def summarize(transcript: str)->str:
    llm = get_llm()

    prompt1 = ChatPromptTemplate.from_messages([
        ("system", "Summarize this portion of a meeting transcript concisely"),
        ("human", "{transcript}"),
    ])

    chain = prompt1 | llm | StrOutputParser()

    chunks = split_transcript(transcript)

    chunk_summaries = [chain.invoke({"transcript": c}) for c in chunks]

    combined = "\n\n".join(chunk_summaries)

    final_prompt = ChatPromptTemplate.from_messages([
        ("system", "You are an expert meeting summarizer.Combine these partial summaries into a single coherent meeting summary in bullet points."),
        ("human", "{summaries}"),
    ])

    final_chain = RunnablePassthrough() | RunnableLambda(lambda x: {"summaries" : x}) | final_prompt | llm | StrOutputParser()

    return final_chain.invoke(combined)


def generate_title(transcipt : str) -> str:
    """
    Generate a concise professional title for the meeting based on the transcript.
    """
    llm = get_llm()

    
    title_chain = (
        RunnablePassthrough() | RunnableLambda(lambda x:{"text":x}) | 
        ChatPromptTemplate.from_messages([
             (
                "system",
                "Based on the meeting transcript, generate a short professional meeting title "
                "(max 8 words). Only return the title, nothing else.",
            ),
            ("human", "{text}"),
        ])
        | llm
        |StrOutputParser()
    )

    return title_chain.invoke(transcipt[:2000])
    

    