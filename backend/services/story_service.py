import re
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

from backend.config import settings

def clean_markdown(text: str) -> str:
    """Removes common markdown formatting from a string using regex."""
    # Remove bold, italics, strikethrough
    text = re.sub(r'(\*\*|__)(.*?)(\*\*|__)', r'\2', text)
    text = re.sub(r'(\*|_)(.*?)(\*|_)', r'\2', text)
    text = re.sub(r'~~(.*?)~~', r'\1', text)
    # Remove headings
    text = re.sub(r'^#+\s+', '', text, flags=re.MULTILINE)
    # Remove list item markers
    text = re.sub(r'^\s*[-*+]\s+', '', text, flags=re.MULTILINE)
    return text.strip()


async def generate_story_from_prompt(prompt: str) -> str:
    """
    Sends a prompt to an AI model using LangChain and returns the generated story plot.
    """
    try:
        llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.7,
            groq_api_key=settings.groq_api_key
        )

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", "You are a creative storyteller for comics. Based on the user's prompt, write a short, compelling plot. The plot should be structured in 3 acts: Act 1 (Setup), Act 2 (Confrontation), and Act 3 (Resolution). IMPORTANT: Do not use any markdown formatting (like asterisks or hashes). Return only plain text."),
            ("user", "{user_prompt}")
        ])

        output_parser = StrOutputParser()

        chain = prompt_template | llm | output_parser

        generated_plot = await chain.ainvoke({"user_prompt": prompt})
        
        cleaned_plot = clean_markdown(generated_plot)
        
        return cleaned_plot

    except Exception as e:
        print(f"An error occurred with the AI model: {e}")
        return "Error: Could not generate story from the AI model."
