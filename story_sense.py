from dotenv import load_dotenv
import streamlit as st
import os
import replicate
import google.generativeai as ggi

# Load environment variables from .env file
load_dotenv()

# Fetch the API keys from environment variables
ggi_api_key = os.getenv("GEMINI_API_KEY")
replicate_api_token = os.getenv("REPLICATE_API_TOKEN")

# Configure Gemini API
ggi.configure(api_key=ggi_api_key)

# Initialize the Gemini GenerativeModel
gemini_model = ggi.GenerativeModel("gemini-pro")
chat = gemini_model.start_chat()

# Initialize Replicate client with API token
replicate_client = replicate.Client(api_token=replicate_api_token)

# Streamlit app
st.title("Story Generator with Gemini and Replicate")
st.write("Enter your story prompt or topic and generate images for each panel of the story.")

# User input for story prompt
story_prompt = st.text_area("Enter the story prompt or topic:")

if st.button("Generate story"):
    if story_prompt:
        try:
            if chat:
                with st.spinner('Generating story...'):
                    story = chat.send_message(story_prompt, stream=True)
                    for panel_index, panel_prompt in enumerate(story):
                        if hasattr(panel_prompt, 'text') and panel_prompt.text:
                            input_params = {
                                "width": 512,
                                "height": 512,
                                "prompt": panel_prompt.text,
                                "refine": "expert_ensemble_refiner",
                                "apply_watermark": False,
                                "num_inference_steps": 25
                            }
                            output = replicate_client.run(
                                "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
                                input=input_params
                            )
                            if output:
                                image_url = output[0]
                                st.subheader(f"Panel {panel_index + 1}:")
                                st.write(panel_prompt.text)
                                st.image(image_url, caption=f"Generated image for panel {panel_index + 1}")
                            else:
                                st.error(f"Failed to generate image for panel {panel_index + 1}.")
                        else:
                            st.warning(f"Panel {panel_index + 1} has no text.")
            else:
                st.warning("Failed to initialize Gemini model. Please check the error message above.")
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
    else:
        st.warning("Please enter a story prompt to generate the story.")
else:
    st.info("Click the 'Generate Strory' button to create your story panels.")

st.write("Note: The story generation process might take a few moments.")
