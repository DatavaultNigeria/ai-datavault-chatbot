import streamlit as st 
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
import os

from openai import OpenAI
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")


client = OpenAI(
    api_key=api_key,
    base_url="https://api.groq.com/openai/v1"
    ) 


def ask_groq_to_generate_code(user_query, df):
    sample = df.head(3).to_dict(orient="records")
    
    prompt = f"""
        You are a senior data analyst using Python (pandas + matplotlib). A user uploaded a dataset with these columns: {', '.join(df.columns)}.
        Here is a preview of the data: {sample}

        The user asked: '{user_query}'

        Write a complete Python code (using pandas and Streamlit) that:
        - Answers the question
        - Displays relevant tables or charts
        - Includes clear text insights using st.markdown()
        Do NOT include explanations or markdown fencing. Just return the code.
        """
    
    response = client.chat.completions.create(
        model="llama3-70b-8192",
        messages=[
            {"role": "system", "content": "You are a helpful data analyst who explains insights clearly."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content.strip()

st.set_page_config(page_title="AI Data Chatbot", layout="centered")
st.title("📈 AI Data Chatbot")

# Upload Excel file
uploaded_file = st.file_uploader("Upload your Excel or CSV", type=["csv", "xlsx"])

if uploaded_file:
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    st.markdown("### ✅ Preview of Your Data:")
    st.dataframe(df)

    # Prompt input
    query = st.text_input("Ask any question about the data (e.g. 'data summary')")

    if st.button("Get Insights"):
        with st.spinner("Thinking..."):
            try:
                # Get response from Groq
                raw_code = ask_groq_to_generate_code(query, df)

                # Clean code: remove markdown code fences like ```python
                import re
                def clean_code(code):
                    return re.sub(r"```(?:python)?\n?|```", "", code).strip()

                cleaned_code = clean_code(raw_code)

                # Check if user asked for code
                if any(keyword in query.lower() for keyword in ["show the code", "generate code", "code only"]):
                    st.markdown("### 🧠 Generated Python Code")
                    st.code(cleaned_code, language="python")

                # Execute code: display insights, charts, tables
                exec_namespace = {"df": df, "st": st, "pd": pd, "plt": plt}
                exec(cleaned_code, {}, exec_namespace)

            except Exception as e:
                st.error(f"Alert:\n\n{e} \n\n Kindly enter your prompt again and click 'Get Insights'")
