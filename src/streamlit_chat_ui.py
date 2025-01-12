import openai
import streamlit as st
from streamlit_chat import message
from src.buyergpt import BuyerGPT


# Init BuyerGPT
buyergpt = BuyerGPT()

# Setting page title and header
st.set_page_config(page_title="ShopperGPT", page_icon=":robot_face:")
st.header("ShopperGPT Web Demo :robot_face:")

# Initialise session state variables
if 'generated' not in st.session_state:
    st.session_state['generated'] = []
if 'past' not in st.session_state:
    st.session_state['past'] = []
if 'messages' not in st.session_state:
    st.session_state['messages'] = [
        {"role": "system", "content": "Who are you?"}
    ]
if "buyergpt" not in st.session_state:
    st.session_state["buyergpt"] = buyergpt

# generate a response
def generate_response(human_input, model_type):
    st.session_state['messages'].append({"role": "user", "content": human_input})
    response = buyergpt.run(human_input=human_input, model_type=model_type)
    st.session_state['messages'].append({"role": "assistant", "content": response })
    return response


# container for chat history
response_container = st.container()
# container for text box
container = st.container()

with container:
    with st.form(key='my_form', clear_on_submit=True):
        user_input = st.text_area("You:", key='input', height=100)
        submit_button = st.form_submit_button(label='Send')
        model_type = st.radio("Select Model: ", ('Fast', 'Deep'))

    if submit_button and user_input and model_type:
        output = generate_response(user_input, model_type=model_type)
        st.session_state['past'].append(user_input)
        st.session_state['generated'].append(output)

if st.session_state['generated']:
    with response_container:
        for i in range(len(st.session_state['generated'])):
            message(st.session_state["past"][i], is_user=True, key=str(i) + '_user')
            message(st.session_state["generated"][i], key=str(i))