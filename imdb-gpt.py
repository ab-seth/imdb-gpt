import streamlit as st
from openai_assistant import ask_question

# Initialize session state for conversation history if it doesn't exist
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = []

# Streamlit app title
st.title("IMDB Questions Assistant")


model = "gpt-4"
verbose = False

# Input field for the question
question = st.text_input("What would you like to know?", key="question_input")

# Function to handle the question submission
def handle_question():
    question = st.session_state.question_input
    if question:  
        response = ask_question(question, model=model, verbose=verbose)
        
        st.session_state.conversation.append(("Question", question))
        st.session_state.conversation.append(("Answer", response))
        
        # st.session_state.question_input = ""



# Function to create custom styled text areas
def custom_text_area(label, value, height, key):
    # Unique CSS class for each text area 
    css_class = f"textarea-{key}"
    
    # Custom CSS to style the text area background
    custom_css = f"""
        <style>
            .{css_class} {{
                background-color: #f0f2f6;
                border-radius: 5px;
                padding: 10px;
            }}
        </style>
    """
    
    # Display custom CSS
    st.markdown(custom_css, unsafe_allow_html=True)
    
    # Display text area with the custom CSS class
    with st.container():
        st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
        st.text_area(label=label, value=value, height=height, key=key)
        st.markdown('</div>', unsafe_allow_html=True)


# Button to submit the question
if st.button("Ask"):
    handle_question()
    
# Display conversation history
for idx, (message_type, message) in enumerate(reversed(st.session_state.conversation)):
    if message_type == "Question":
        custom_text_area(label=f"Q: {idx+1}", value=message, height=75, key=f"q_{idx}")
    else:  
        custom_text_area(label=f"A: {idx+1}", value=message, height=100, key=f"a_{idx}")