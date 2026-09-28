import streamlit as st

from backend.agent import agent


@st.cache_resource
def get_agent():
    return agent


st.title("AI Research Command Centre")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("What information do you need?"):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Researching the web..."):
            result = get_agent().invoke({"messages": [("user", prompt)]})
            messages = result.get("messages", [])
            response = messages[-1].content if messages else str(result)
            st.markdown(response)
            st.session_state.messages.append({"role": "assistant", "content": response})