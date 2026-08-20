import streamlit as st

st.set_page_config(
    page_title="NLP Chatbot",
    page_icon="🤖"
)

st.title("🤖 NLP Chatbot")

st.write("Ask questions and get answers using Natural Language Processing.")

if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Ask a question...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    st.session_state.messages.append({
        "role": "user",
        "content": user_input
    })

    response = "This is a temporary response."

    with st.chat_message("assistant"):
        st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response
    })