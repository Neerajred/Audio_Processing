import google.generativeai as genai
from config import GEMINI_API_KEY, logger

def summarize_with_gemini(text):
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        print(text)
        prompt = f"""
        You are a professional call summarization assistant with expertise in analyzing and summarizing call recordings from real estate service platforms. Your task is to determine who initiated the call (agent or customer) and whether it is incoming or outgoing based on who spoke first and the context of the conversation.
        Please structure the summary as follows in 3-4 lines:
        Begin by clearly stating who initiated the call (agent or customer) and whether it was an incoming or outgoing call.
        Follow with a chronological summary of the discussion, including:
        The project or service being discussed
        The customer's preferences, questions, requirements, or concerns
        The agent’s responses, suggestions, and offerings
        Conclude with any resolutions, follow-up plans, or next steps agreed upon during the call.
        Guidelines for the summary:
        Use clear and professional language suitable for business communication.
        Do not include any personal names or identifiers
        Avoid assumptions — only assign roles (agent or customer) if clearly stated or inferred from context
        Keep the summary concise (ideally 4–6 sentences)
        Examples:
        Example 1:
        The call is initiated by an agent introducing a project.
        The customer is not interested in plots but prefers already constructed houses.
        The customer is looking for a smaller house (200–250 sq. yards) within a specific budget (200–250, presumably in lakhs).
        The agent will follow up after checking for suitable options.
        Example 2:
        The call is initiated by the customer inquiring about a project near Ibrahimpatnam.
        The project near Ibrahimpatnam is 18,000 sq. yards, with approximately 80% development completed and roads expected to be finished within two to three months.
        A 70% bank loan is available through SBI, ICICI, and Tata Capital.
        The project offers plots ranging from 183 to 600 sq. yards, with approximately 385 plots currently available (40% unsold).
        Transcript:\n\n{text}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Summarization failed: {e}")
        return "Summary not available due to error."

def suggest_actions_with_gemini(summary):
    if not summary.strip() or "Summary not available" in summary:
        return "Action suggestions not available"
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel("gemini-2.5-flash")
        prompt = f"""
        You are a knowledgeable marketing strategist with extensive experience in 
        suggesting actionable follow-up strategies based on client interactions and 
        marketing activities. Your expertise lies in analyzing summaries and providing 
        tailored recommendations to agents for their next steps.
        Your task is to provide a suggestion for the next follow-up action or marketing 
        activity based on the summary provided.
        The suggestion should be one line, structured clearly, outlining the recommended action, 
        rationale for the recommendation, and any potential outcomes. 
        Consider the context of the client's industry, target audience, and previous 
        interactions to ensure the suggestion is relevant and actionable. 
        Be cautious to avoid generic recommendations and ensure that your suggestions 
        are directly applicable to the provided summary
        Summary:\n\n{summary}
        """
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Action suggestion failed: {e}")
        return "Action suggestions not available"