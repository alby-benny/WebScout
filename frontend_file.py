import streamlit as st
import webscrapper
from process_text import summarization

# Initialize session state
if "has_user_input" not in st.session_state:
    st.session_state.has_user_input = False
if "messages" not in st.session_state:
    st.session_state.messages = []
if "related_topics" not in st.session_state:
    st.session_state.related_topics = {}


# Function to fetch and display URL content
def fetch_url_content(url):
    info_sub = webscrapper.Main_info(url)
    st.session_state.messages.append({"role": "assistant", "content": info_sub[0]})
    with st.chat_message("assistant"):
        st.markdown(info_sub[0])
    if len(info_sub) > 1 and info_sub[1]:
        st.session_state.has_user_input = True
        st.session_state.related_topics = info_sub[1]
    else:
        st.session_state.has_user_input = False


# Function to handle the assistant's response to user queries
def add_assistant_response(Ques):
    info = webscrapper.get_info(Ques)
    summarized_response = summarization(Ques, info[0])  # Use user query and content
    st.session_state.messages.append({"role": "assistant", "content": summarized_response})
    with st.chat_message("assistant"):
        st.markdown(summarized_response)
    if len(info) > 1 and info[1]:
        st.session_state.has_user_input = True
        st.session_state.related_topics = info[1]
    else:
        st.session_state.has_user_input = False


# Function to handle button click and summarize content
def button_state(key, content):
    # Summarize the content associated with the button clicked
    summarized_response = summarization(key, content)  # key is the button label, content is the content
    st.session_state.messages.append({"role": "assistant", "content": summarized_response})
    with st.chat_message("assistant"):
        st.markdown(summarized_response)


# Main app
st.title("Chatbot")

# Display chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Get user input
if prompt := st.chat_input("What is up?"):
    # Clear previous assistant responses if needed
    #st.session_state.messages = []

    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Add assistant's response and related buttons
    add_assistant_response(prompt)

# Handle related topics as buttons
if st.session_state.has_user_input:
    st.write("Related topics to view:")
    for key, url in st.session_state.related_topics.items():
        if st.button(label=key, key=key):
            # Call the button state function with the key and the related content (fetched from webscrapper)
            content = webscrapper.Main_info(url)[0]
            button_state(key, content)
