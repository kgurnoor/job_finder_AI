import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=GOOGLE_API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

GEMINI_PROMPTS = {
    "initial_prompt": """
        You are Asha, an AI assistant for the JobsForHer (HerKey) platform.
        Your goal is to help women find jobs, events, and mentorship opportunities.
        Be positive, helpful, and encouraging.
        Do not include any personally identifiable information.
        ONLY use the information I provide. If the information is not available, say so.
    """,
    "bias_reframing": """
        If the user's query contains any gender bias, reframe the question in a neutral and positive way.
        For example, if the user asks "Are women suitable for leadership roles?", you should respond as if the user asked "Tell me about women in leadership."
    """,
    "scraping_required_check": """
        Determine if the user's query requires scraping information from the web. Respond with "yes" or "no".
        For example:
        User: Show me recent job postings.
        Response: yes
        User: What is the mission of JobsForHer?
        Response: no
    """,
    "generate_response_with_context": """
        Generate a comprehensive and informative answer, and ALWAYS use the scraped data I provide. Format the data nicely for the user.
        Scraped data: {scraped_data}
        User query: {user_query}
    """,
    "generate_response_without_context": """
        Generate a comprehensive and informative answer to the user's query.
        User query: {user_query}
    """,
    "generate_job_list": """
        You are Asha, an AI assistant for the JobsForHer (HerKey) platform.
        The user is looking for software engineering jobs in Pune.
        Present the results as a list. For each job, include:
        - Title: [Job Title]
        - Company: [Company Name]
        - Location: [Location]
        - Link: [Job Link]
        If any information is missing, indicate it as "N/A".
        Do not provide any introductory or concluding sentences.
        Do not give any descriptions or explanations.
        Only provide the list of jobs based on the scraped data.
        Scraped data: {scraped_data}
        User query: {user_query}
    """
}

def craft_gemini_prompt(user_query, context, prompt_type="generate_response_without_context"):
    """Crafts the prompt for the Gemini LLM, incorporating conversation history."""

    prompt = GEMINI_PROMPTS["initial_prompt"] + "\n" + GEMINI_PROMPTS["bias_reframing"] + "\n"

    if context:
        prompt += "Here is the conversation history:\n"
        for message in context:
            prompt += f"{message['role']}: {message['content']}\n"

    if prompt_type == "generate_job_list":
        prompt += GEMINI_PROMPTS["generate_job_list"].format(scraped_data=context, user_query=user_query) # changed context to scraped_data
    else:
        prompt += GEMINI_PROMPTS["generate_response_without_context"].format(user_query=user_query)
    return prompt

def get_gemini_response(prompt):
    """Sends the prompt to the Gemini LLM and returns the response."""

    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "I'm sorry, I encountered an error while processing your request."

def is_scraping_required(prompt):
    """Determines if web scraping is required based on the user query."""

    prompt_check = GEMINI_PROMPTS["scraping_required_check"] + "\n" + prompt
    response = model.generate_content(prompt_check)
    return "yes" in response.text.lower()

def update_prompt_with_scraped_data(prompt, scraped_data):
    """Updates the prompt with the scraped data before sending it to Gemini."""

    return GEMINI_PROMPTS["generate_response_with_context"].format(scraped_data=scraped_data, user_query=prompt)

def handle_bias(user_query, gemini_response):
    """Handles potential bias in the LLM's response."""

    biased_phrases = ["are women suitable", "women in leadership", "women's abilities"]
    for phrase in biased_phrases:
        if phrase in user_query.lower():
            return "Women are highly capable and successful in all fields."
    return gemini_response