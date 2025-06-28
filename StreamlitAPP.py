import os
import json
import traceback
import pandas as pd
from dotenv import load_dotenv
import streamlit as st

os.environ.pop("SSL_CERT_FILE", None)

from src.mcqgenerator.utils import read_file, get_table_data
from langchain_community.callbacks.manager import get_openai_callback
from src.mcqgenerator.MCQGenerator import generate_evaluate_chain
from src.mcqgenerator.logger import logging

# Load JSON Response Template
json_path = os.path.join(os.getcwd(), "Response.json")
with open(json_path, "r") as file:
    RESPONSE_JSON = json.load(file)

st.title("MCQ Generator Application with LangChain")

# Form UI
with st.form("user_inputs"):
    uploaded_file = st.file_uploader("Upload a PDF or Text File")
    mcq_count = st.number_input("Number of MCQs", min_value=1, max_value=3)
    subject = st.text_input("Insert Subject", max_chars=20)
    tone = st.text_input("Complexity level of questions", max_chars=20, placeholder="Simple")
    button = st.form_submit_button("Create MCQs")

    if button and uploaded_file and mcq_count and subject and tone:
        with st.spinner("Loading..."):
            try:
                text = read_file(uploaded_file)

                with get_openai_callback() as cb:
                    response = generate_evaluate_chain({
                        "text": text,
                        "number": mcq_count,
                        "subject": subject,
                        "tone": tone,
                        "response_json": json.dumps(RESPONSE_JSON)
                    })

            except Exception as e:
                traceback.print_exception(type(e), e, e.__traceback__)
                st.error("An error occurred during MCQ generation.")
            else:
                # Show token and cost info
                print(f"Total Tokens Used: {cb.total_tokens}")
                print(f"Prompt Tokens: {cb.prompt_tokens}")
                print(f"Completion Tokens: {cb.completion_tokens}")
                print(f"Total Cost: ${cb.total_cost}")


                # Show full raw response for inspection
                print("🧾 Full response from chain:", response)

                if isinstance(response, dict):
                    # quiz = response.get("quiz")
                    # if quiz:
                    #     table_data = get_table_data(quiz)

                    #     # DEBUGGING: log table_data info
                    #     print("Type of table_data:", type(table_data))
                    #     print("Content of table_data:", table_data)
                    quiz = response.get("quiz")

# 🔍 Debug quiz before processing
                    print("🧠 Raw quiz:", quiz)
                    print("🧠 Type of quiz:", type(quiz))

                    if quiz:
                        table_data = get_table_data(quiz)

                        print("📊 Output of get_table_data:", table_data)
                        print("📊 Type of table_data:", type(table_data))

                        # Convert if table_data is a JSON string
                        if isinstance(table_data, str):
                            try:
                                table_data = json.loads(table_data)
                            except json.JSONDecodeError:
                                st.error("Table data is not valid JSON.")
                                table_data = None

                        if isinstance(table_data, (list, dict)):
                            try:
                                df = pd.DataFrame(table_data)
                                df.index = df.index + 1
                                st.table(df)

                                # Show the review
                                st.text_area("Review", value=response.get("review", ""))
                            except Exception as e:
                                st.error(f"DataFrame conversion failed: {e}")
                        else:
                            st.error("Table data is not in the correct format (list or dict).")
                    else:
                        st.warning("No quiz data was found in the response.")
                else:
                    st.write("Unexpected response format:")
                    st.write(response)
