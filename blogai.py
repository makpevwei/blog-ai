import streamlit as st
import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Try to use the API key from Streamlit secrets (for deployment on Streamlit Cloud)
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    # If not found, fall back to the environment variable (for local development)
    api_key = os.environ.get("GEMINI_API_KEY")

# Configure the Gemini API with the chosen API key
genai.configure(api_key=api_key)

# Define generation settings for the AI model
generation_config = {
    "temperature": 1,  
    "top_p": 0.95,  
    "top_k": 40,  
    "max_output_tokens": 8192,  
    "response_mime_type": "text/plain",  
}

# Initialize the generative model from Gemini API
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash-8b",
    generation_config=generation_config,
    system_instruction="""
    You are a professional writer and blogger with expertise in crafting engaging, well-structured blog posts.
    Generate a blog post based on the given topic, tone, and word count.
    The tone should align with the user's selection (e.g., professional, humorous, casual, or a mix).
    Ensure the blog follows a proper structure, including an introduction, body sections, and a conclusion.
    Keep the writing engaging, informative, and suitable for a general audience.
    """,
)

# Streamlit UI
st.header("Blog Post Generator AI 📝")
st.write("Enter a topic, choose a tone, and set the word count to generate a professional blog post.")

# Define available tones with descriptions
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
    topic_lower = topic.lower()
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

# Text input for topic
topic = st.text_input("Enter the topic for your blog post:")

# Suggest a tone based on the entered topic
if topic:
    suggested_tone = suggest_tone(topic)
    st.write(f"💡 **Suggested Tone:** {suggested_tone} - {tone_options[suggested_tone]}")
else:
    suggested_tone = "Professional"  # Default tone if no topic is entered

# Dropdown for tone selection (defaulting to the suggested tone)
selected_tone = st.selectbox("Choose the tone for your blog:", list(tone_options.keys()), index=list(tone_options.keys()).index(suggested_tone))

# Display the selected tone's description
st.write(f"**Selected Tone:** {selected_tone} - {tone_options[selected_tone]}")

# Slider for blog post length
length_option = st.slider(
    "Select the maximum word count:", min_value=100, max_value=2000, value=500, step=100
)

# Generate blog post if topic is provided
if topic:
    st.write(f"Generating a **{selected_tone.lower()}** blog post about **{topic}** with up to {length_option} words...")

    def process_gemini_response(prompt, tone, length):
        """
        Generates a blog post using the Gemini API with the given topic, tone, and word count.
        """
        modified_prompt = (
            f"Write a {tone.lower()} blog post about '{prompt}' with a maximum of {length} words. "
            "Ensure a proper structure including an introduction, main sections, and a conclusion."
        )

        chat_session = model.start_chat()
        response = chat_session.send_message(modified_prompt)
        return response.text

    # Generate the blog post
    blog_post = process_gemini_response(topic, selected_tone, length_option)

    # Display the generated blog post
    st.write(blog_post)
