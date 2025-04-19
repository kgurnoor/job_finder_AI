import streamlit as st
from modules import dialog_manager, llm_handler, scraper, utils
import time

def main():
    st.title("Asha AI Bot")

    # Initialize session state
    if "session_id" not in st.session_state:
        st.session_id = dialog_manager.create_session()
        st.session_state.messages = []

    # Display previous messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Get user input
    user_query = st.chat_input("Ask me anything about JobsForHer...")
    if user_query:
        st.session_state.messages.append({"role": "user", "content": user_query})
        with st.chat_message("user"):
            st.markdown(user_query)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            bot_response = get_bot_response(user_query, st.session_state.session_id)

            # Basic formatting for Streamlit
            formatted_response = bot_response.replace("- Title:", "<br>**Title:**").replace("- Company:", "<br>**Company:**").replace("- Location:", "<br>**Location:**").replace("- Link:", "<br>[Link](").replace(")", ")<br><br>")
            full_response = formatted_response

            placeholder.markdown(full_response, unsafe_allow_html=True)  # Allow HTML for bolding and links
            time.sleep(0.02)
            #placeholder.markdown(full_response)
            st.session_state.messages.append({"role": "assistant", "content": full_response})

def get_bot_response(user_query, session_id):
    """Handles the overall bot response generation process."""

    # 1. Get Context and Generate Prompt
    context = dialog_manager.get_context(session_id)
    prompt = llm_handler.craft_gemini_prompt(user_query, context, prompt_type="generate_response_without_context")

    # 2. Check if scraping is needed and Scrape
    if llm_handler.is_scraping_required(prompt):
        scraped_data = scraper.scrape_relevant_data(user_query)
        if scraped_data:
            #  Prompt for a job list format
            prompt = llm_handler.craft_gemini_prompt(user_query, scraped_data, prompt_type="generate_list_format")

    # 3. Get response from LLM
    gemini_response = llm_handler.get_gemini_response(prompt)

    # 4. Handle Bias and Finalize
    final_response = llm_handler.handle_bias(user_query, gemini_response)
    dialog_manager.update_context(session_id, user_query, final_response)
    return final_response

if __name__ == "__main__":
    main()