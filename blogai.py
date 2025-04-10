# Import necessary libraries
import streamlit as st  # For creating the web app interface
import os  # For accessing environment variables
import google.generativeai as genai  # Google's Gemini AI API
from dotenv import load_dotenv  # For loading environment variables from .env file

# Load environment variables from .env file (for local development)
# This is where you'd store sensitive information like API keys
load_dotenv()

# Try to use the API key from Streamlit secrets (for deployment on Streamlit Cloud)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    # If not found in Streamlit secrets, fall back to the environment variable (for local development)
    api_key = os.environ.get("GEMINI_API_KEY")

# Configure the Gemini API with the obtained API key
genai.configure(api_key=api_key)

# Define generation settings for the AI model
# These parameters control how the AI generates text
generation_config = {
    "temperature": 1,  # Controls randomness (0 = deterministic, 1 = more creative)
    "top_p": 0.95,  # Controls diversity of responses (nucleus sampling)
    "top_k": 40,  # Limits the next word selection to top K candidates
    "max_output_tokens": 8192,  # Maximum length of the response
    "response_mime_type": "text/plain",  # Format of the response
}

# Initialize the generative model from Gemini API
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",  # Specifies which Gemini model to use
    generation_config=generation_config,  # Applies our configuration
    system_instruction="""
    You are a professional writer and blogger with expertise in crafting engaging, well-structured blog posts.
    Generate a blog post based on the given topic, tone, and word count.
    The tone should align with the user's selection (e.g., professional, humorous, casual, or a mix).
    Ensure the blog follows a proper structure, including an introduction, body sections, and a conclusion.
    Keep the writing engaging, informative, and suitable for a general audience.
    """,  # This instruction tells the AI how to behave
)

# =============================================
# Streamlit User Interface Setup
# =============================================

# Create the header for the web app
st.header("Blog Post Generator AI 📝")
st.write("Enter a topic, choose a tone, and set the word count to generate a professional blog post.")

# Define available tones with descriptions
# This dictionary maps tone names to their descriptions
tone_options = {
    "Professional": "Formal, polished, and authoritative. Ideal for business and corporate topics.",
    "Informative & Educational": "Fact-driven and structured to explain concepts clearly.",
    "Conversational & Friendly": "Engaging and approachable, like talking to a friend.",
    "Witty & Humorous": "Lighthearted with humor, making content fun and digestible.",
    "Persuasive & Sales-Oriented": "Focused on convincing the reader, great for marketing and sales.",
    "Inspirational & Motivational": "Encouraging and uplifting, perfect for self-improvement and success stories.",
    "Narrative & Storytelling": "Uses anecdotes and storytelling for engagement.",
    "Analytical & Data-Driven": "Fact-based with statistics, suitable for business and finance topics.",
    "Casual & Fun": "Light, entertaining, and easy to read.",
    "Thought-Provoking & Philosophical": "Encourages deep thinking and reflection."
}

# Function to suggest a tone based on the topic
def suggest_tone(topic):
    """
    Analyzes the topic and suggests an appropriate writing tone.
    Looks for keywords in the topic to determine the best tone.
    """
    topic_lower = topic.lower()  # Convert to lowercase for case-insensitive comparison
    
    # Check for keywords and return matching tone
    if any(word in topic_lower for word in ["business", "finance", "corporate", "strategy"]):
        return "Professional"
    elif any(word in topic_lower for word in ["science", "education", "learning", "technology"]):
        return "Informative & Educational"
    elif any(word in topic_lower for word in ["personal", "lifestyle", "travel", "relationships"]):
        return "Conversational & Friendly"
    elif any(word in topic_lower for word in ["comedy", "fun", "entertainment", "jokes"]):
        return "Witty & Humorous"
    elif any(word in topic_lower for word in ["marketing", "sales", "advertising", "branding"]):
        return "Persuasive & Sales-Oriented"
    elif any(word in topic_lower for word in ["motivation", "success", "self-improvement", "inspiration"]):
        return "Inspirational & Motivational"
    elif any(word in topic_lower for word in ["history", "biography", "stories", "fiction"]):
        return "Narrative & Storytelling"
    elif any(word in topic_lower for word in ["data", "analysis", "research", "statistics"]):
        return "Analytical & Data-Driven"
    elif any(word in topic_lower for word in ["fun", "casual", "easy", "relaxed"]):
        return "Casual & Fun"
    elif any(word in topic_lower for word in ["philosophy", "deep", "thoughts", "ethics"]):
        return "Thought-Provoking & Philosophical"
    else:
        return "Professional"  # Default tone if no keywords match

# =============================================
# User Input Section
# =============================================

# Text input field for the blog topic
topic = st.text_input("Enter the topic for your blog post:")

# Suggest a tone based on the entered topic
if topic:
    # If topic is provided, suggest a tone
    suggested_tone = suggest_tone(topic)
    st.write(f"💡 **Suggested Tone:** {suggested_tone} - {tone_options[suggested_tone]}")
else:
    # Default tone if no topic is entered yet
    suggested_tone = "Professional"

# Dropdown for tone selection (defaults to the suggested tone)
selected_tone = st.selectbox(
    "Choose the tone for your blog:", 
    list(tone_options.keys()),  # All available tone options
    index=list(tone_options.keys()).index(suggested_tone)  # Default selection
)

# Display the selected tone's description
st.write(f"**Selected Tone:** {selected_tone} - {tone_options[selected_tone]}")

# Slider for selecting blog post length
length_option = st.slider(
    "Select the maximum word count:", 
    min_value=100,  # Minimum word count
    max_value=2000,  # Maximum word count
    value=500,  # Default value
    step=100  # Increment step
)

# =============================================
# Blog Post Generation Section
# =============================================

# Only generate if a topic is provided
if topic:
    # Show what we're about to generate
    st.write(f"Generating a **{selected_tone.lower()}** blog post about **{topic}** with up to {length_option} words...")

    def process_gemini_response(prompt, tone, length):
        """
        Generates a blog post using the Gemini API.
        
        Args:
            prompt: The blog topic
            tone: The writing style to use
            length: Maximum word count
            
        Returns:
            The generated blog post text
        """
        # Create a detailed prompt for the AI
        modified_prompt = (
            f"Write a {tone.lower()} blog post about '{prompt}' with a maximum of {length} words. "
            "Ensure a proper structure including an introduction, main sections, and a conclusion."
        )

        # Start a chat session with the model
        chat_session = model.start_chat()
        # Send our prompt and get the response
        response = chat_session.send_message(modified_prompt)
        return response.text

    # Generate the blog post using our function
    blog_post = process_gemini_response(topic, selected_tone, length_option)

    # Display the generated blog post
    st.write(blog_post)