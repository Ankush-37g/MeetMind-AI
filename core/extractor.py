#Actionableitems , decision , questions 
from langchain_mistralai import ChatMistralAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_text_splitters import RecursiveCharacterTextSplitter
import os 


def get_llm():
    return ChatMistralAI(model = "mistral-small-latest", mistral_api_key = os.getenv("MISTRAL_API_KEY"),temperature=0.2)


def split_transcript(transcript: str) -> list:

    splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ".", " "],
        chunk_size=3000,
        chunk_overlap=200,
    ) 
    return splitter.split_text(transcript)


def build_chain(system_prompt : str):

    llm = get_llm()
    return (
        RunnablePassthrough() | RunnableLambda(lambda x : {"text" : x}) |ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human","{text}"),
    ]) | llm |StrOutputParser()
    )


def _map_reduce_extract(transcript: str, map_system_prompt: str, reduce_system_prompt: str) -> str:

    chunks = split_transcript(transcript)
    if not chunks:
        return ""
    
    map_chain = build_chain(map_system_prompt)
    extracted_chunks = [map_chain.invoke(c) for c in chunks]
    
    combined = "\n\n".join(extracted_chunks)
    
    if len(chunks) == 1:
        return extracted_chunks[0]

    reduce_chain = build_chain(reduce_system_prompt)
    return reduce_chain.invoke(combined)


def extract_action_items(transcript:str)->str:

    map_prompt = (
        "You are an expert meeting analyst. From this portion of the meeting transcript, "
        "extract all action items. For each provide:\n"
        "- Task description\n"
        "- Owner (who is responsible)\n"
        "- Deadline (if mentioned, else write 'Not specified')\n\n"
        "Format as a numbered list. If none found say 'No action items found.'"
    ) 
    reduce_prompt = (
        "You are an expert meeting analyst. Combine these partial lists of action items "
        "extracted from different parts of a meeting into a single consolidated numbered list. "
        "Remove any duplicates. If there are no action items at all, say 'No action items found.'"
    )
    return _map_reduce_extract(transcript, map_prompt, reduce_prompt)


def extract_key_decisions(transcript: str) -> str:

    map_prompt = (
        "You are an expert meeting analyst. From this portion of the meeting transcript, "
        "extract all key decisions made. Format as a numbered list. "
        "If none found say 'No key decisions found.'"
    )
    reduce_prompt = (
        "You are an expert meeting analyst. Combine these partial lists of key decisions "
        "extracted from different parts of a meeting into a single consolidated numbered list. "
        "Remove any duplicates. If there are no key decisions at all, say 'No key decisions found.'"
    )
    return _map_reduce_extract(transcript, map_prompt, reduce_prompt)


def extract_questions(transcript: str) -> str:

    map_prompt = (
        "From this portion of the meeting transcript, extract all unresolved questions "
        "or topics needing follow-up. Format as a numbered list. "
        "If none found say 'No open questions found.'"
    )
    reduce_prompt = (
        "Combine these partial lists of unresolved questions and topics needing follow-up "
        "into a single consolidated numbered list. "
        "Remove any duplicates. If there are no open questions at all, say 'No open questions found.'"
    )
    return _map_reduce_extract(transcript, map_prompt, reduce_prompt)