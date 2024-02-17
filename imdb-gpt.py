import streamlit as st
from openai_assistant import ask_question

# Initialize session state for conversation history if it doesn't exist
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# Streamlit app title
st.title("IMDB Questions Assistant")

model = "gpt-4"
verbose = False

# Function to handle the question submission
def handle_question():
    question = st.session_state.question_input
    if question:
        response = ask_question(question, model=model, verbose=verbose)
        # Insert the question and answer at the beginning of the conversation
        st.session_state.conversation.insert(0, ("Answer", response))
        st.session_state.conversation.insert(0, ("Question", question))

# Display conversation history
def display_conversation():
    for message_type, message in st.session_state.conversation:
        if message_type == "Question":
            st.text_area(f"Q:", value=message, height=20, key=message)
        else:
            st.text_area(f"A:", value=message, height=150, key=message)

# Reset the input box after the form is submitted
if 'submit' not in st.session_state:
    st.session_state.submit = False

if st.session_state.submit:
    question = st.text_input("What would you like to know?", key="question_input", value="")
    st.session_state.submit = False
else:
    question = st.text_input("What would you like to know?", key="question_input")

# Button to submit the question
if st.button("Ask"):
    st.session_state.submit = True
    handle_question()

# Call to display the conversation history
display_conversation()
