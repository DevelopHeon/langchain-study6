from typing import Set

from click import prompt

from backend.core import run_llm
import streamlit as st
from streamlit_chat import message

# Add sidebar with user information
with st.sidebar:
    st.title("User Profile")
    
    # Check if user is authenticated
    if st.experimental_user.email:
        # Add profile section
        with st.container():
            st.image("https://www.gravatar.com/avatar/00000000000000000000000000000000?d=mp", width=100)
            st.markdown(f"### 👤 {st.experimental_user.email.split('@')[0]}")
            st.markdown(f"📧 {st.experimental_user.email}")
    else:
        st.warning("Please login to view your profile information")
    
    # Add a divider
    st.divider()

# Main content
st.title("🦜️ LangChain Documentation Helper")
st.markdown("### Ask anything about LangChain documentation")

prompt = st.text_input("", 
                      placeholder="Enter your prompt here..",
                      label_visibility="collapsed")

if (
    "chat_answers_history" not in st.session_state
    and "user_prompt_history" not in st.session_state
    and "chat_history" not in st.session_state
):
    st.session_state["chat_answers_history"] = []
    st.session_state["user_prompt_history"] = []
    st.session_state["chat_history"] = []

def create_sources_string(source_urls: Set[str]) -> str:
    if not source_urls:
        return ""
    sources_list = list(source_urls)
    sources_list.sort()
    sources_string = "sources:\n"
    for i, source in enumerate(sources_list):
        sources_string += f"{i+1}. {source}\n"
    return sources_string

if prompt:
    with st.spinner("Generating response..."):
        generated_response = run_llm(
            query=prompt, chat_history=st.session_state["chat_history"]
        )
        sources = set([doc.metadata["source"] for doc in generated_response["source_documents"]])
        
        formatted_response = f"{generated_response['result']} \n\n {create_sources_string(sources)}"

        st.session_state["user_prompt_history"].append(prompt)
        st.session_state["chat_answers_history"].append(formatted_response)
        st.session_state["chat_history"].append(("human", prompt))
        st.session_state["chat_history"].append(("ai", generated_response["result"]))

if st.session_state["chat_answers_history"]:
    for generated_response, user_query in zip(
        st.session_state["chat_answers_history"],
        st.session_state["user_prompt_history"],
    ):
        message(user_query, is_user=True)
        message(generated_response)

