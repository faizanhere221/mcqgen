import os
from dotenv import load_dotenv
from src.mcqgenerator.utils import read_file, get_table_data
from src.mcqgenerator.logger import logging
import os
os.environ.pop("SSL_CERT_FILE", None)
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate

# Load API Key from .env
load_dotenv()
Key = os.getenv("OPENAI_API_KEY")

# Initialize LLM
llm = ChatOpenAI(openai_api_key=Key, model="gpt-3.5-turbo", temperature=0.7)

# Prompt for quiz generation
TEMPLATE = """
Text: {text}
You are an expert MCQ maker. Given the above text, it is your job to 
create a quiz of {number} multiple choice questions for {subject} students in {tone}
tone. Make sure the questions are not repeated and check all the questions to be conforming the text as well.
Make sure to format your response like RESPONSE_JSON and use it as a guide.
Ensure to make {number} MCQs
### RESPONSE_JSON
{response_json}
"""

quiz_generation_prompt = PromptTemplate(
    input_variables=["text", "number", "subject", "tone", "response_json"],
    template=TEMPLATE
)

# Prompt for quiz evaluation
TEMPLATE2 = """
You are an expert English grammarian and writer. Given a Multiple Choice Quiz for {subject} students,
you need to evaluate the complexity of the question and give a complete analysis of the quiz. Only use at max 50 words for complexity.
If the quiz is not up to the cognitive and analytical abilities of the students,
update the quiz questions which need to be changed and change the tone such that it perfectly fits the student abilities.
Quiz_MCQs:
{quiz}

Check from an expert English writer of the above quiz:
"""

quiz_evaluation_prompt = PromptTemplate(
    input_variables=["subject", "quiz"],
    template=TEMPLATE2
)

# Define the chains
quiz_chain = quiz_generation_prompt | llm
review_chain = quiz_evaluation_prompt | llm

# Define wrapper function like `generate_evaluate_chain`
def generate_evaluate_chain(input_data):
    # Step 1: Generate Quiz
    quiz = quiz_chain.invoke({
        "text": input_data["text"],
        "number": input_data["number"],
        "subject": input_data["subject"],
        "tone": input_data["tone"],
        "response_json": input_data["response_json"]
    })

    # Step 2: Review Quiz
    review = review_chain.invoke({
        "subject": input_data["subject"],
        "quiz": quiz.content if hasattr(quiz, "content") else quiz
    })

    return {
        "quiz": quiz.content if hasattr(quiz, "content") else quiz,
        "review": review.content if hasattr(review, "content") else review
    }
