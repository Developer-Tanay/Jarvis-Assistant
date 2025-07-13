"""
ImageGeneration.py - AI Image Genera    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 512,
            "height": 512
        }
    } Hugging Face Stable Diffusion
Generates images from text prompts using Stable Diffusion XL model
"""

import requests
import json
import base64
import os
from PIL import Image
from io import BytesIO
from dotenv import dotenv_values
from datetime import datetime

# Load environment variables
env_vars = dotenv_values(".env")
HUGGINGFACE_API_KEY = env_vars.get("HUGGINGFACE_API_KEY")

if not HUGGINGFACE_API_KEY:
    raise ValueError("HUGGINGFACE_API_KEY not found in .env file")

# Stable Diffusion API endpoint - using a free model
API_URL = "https://api-inference.huggingface.co/models/runwayml/stable-diffusion-v1-5"
headers = {"Authorization": f"Bearer {HUGGINGFACE_API_KEY}"}

# Ensure directories exist
os.makedirs("Data", exist_ok=True)
os.makedirs("Data/Generated_Images", exist_ok=True)


def query_image_api(prompt, negative_prompt="blurry, low quality, distorted"):
    """
    Query Hugging Face API for image generation

    Args:
        prompt (str): The text prompt for image generation
        negative_prompt (str): What to avoid in the generated image

    Returns:
        bytes: The generated image data
    """
    payload = {
        "inputs": prompt,
        "parameters": {
            "negative_prompt": negative_prompt,
            "num_inference_steps": 20,
            "guidance_scale": 7.5,
            "width": 1024,
            "height": 1024,
        },
    }

    try:
        response = requests.post(API_URL, headers=headers, json=payload, timeout=60)
        response.raise_for_status()
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"Error generating image: {e}")
        return None


def save_generated_image(image_data, prompt):
    """
    Save the generated image to the Data/Generated_Images directory

    Args:
        image_data (bytes): The image data
        prompt (str): The original prompt (for filename)

    Returns:
        str: Path to the saved image file
    """
    try:
        # Create a safe filename from prompt
        safe_prompt = "".join(
            c for c in prompt if c.isalnum() or c in (" ", "-", "_")
        ).rstrip()
        safe_prompt = safe_prompt[:50]  # Limit length

        # Generate timestamp for unique filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"generated_{timestamp}_{safe_prompt}.png"
        filepath = os.path.join("Data", "Generated_Images", filename)

        # Save the image
        image = Image.open(BytesIO(image_data))
        image.save(filepath, "PNG")

        print(f"Image saved successfully: {filepath}")
        return filepath

    except Exception as e:
        print(f"Error saving image: {e}")
        return None


def open_image(filepath):
    """
    Open the generated image with the default system image viewer

    Args:
        filepath (str): Path to the image file
    """
    try:
        if os.path.exists(filepath):
            os.startfile(filepath)  # Windows
        else:
            print(f"Image file not found: {filepath}")
    except Exception as e:
        print(f"Error opening image: {e}")


def generate_image(prompt):
    """
    Main function to generate an image from text prompt

    Args:
        prompt (str): The text description for image generation

    Returns:
        str: Success message with image path or error message
    """
    try:
        print(f"Generating image for prompt: '{prompt}'")

        # Generate the image
        image_data = query_image_api(prompt)

        if image_data is None:
            return "Failed to generate image. Please check your internet connection and API key."

        # Save the image
        filepath = save_generated_image(image_data, prompt)

        if filepath is None:
            return "Image generated but failed to save."

        # Open the image
        open_image(filepath)

        return f"Image generated successfully! Saved as: {os.path.basename(filepath)}"

    except Exception as e:
        error_msg = f"Error in image generation: {str(e)}"
        print(error_msg)
        return error_msg


def process_image_generation_request():
    """
    Process image generation request from the data file
    This function is called when Main.py spawns this as a subprocess
    """
    try:
        # Check if the request file exists
        request_file = os.path.join("Frontend", "Files", "ImageGeneratoion.data")

        if not os.path.exists(request_file):
            print("No image generation request found.")
            return

        # Read the request
        with open(request_file, "r", encoding="utf-8") as f:
            request_data = f.read().strip()

        if not request_data:
            print("Empty image generation request.")
            return

        # Parse the request (format: "prompt, True")
        if ", True" in request_data:
            prompt = request_data.replace(", True", "").strip()

            # Clean up the prompt (remove "generate image" prefix if present)
            prompt = prompt.replace("generate image", "").strip()

            if prompt:
                result = generate_image(prompt)
                print(result)
            else:
                print("Empty prompt after cleanup.")
        else:
            print("Invalid request format.")

        # Clean up the request file
        with open(request_file, "w", encoding="utf-8") as f:
            f.write("")

    except Exception as e:
        print(f"Error processing image generation request: {e}")


# Enhanced prompts for better results
def enhance_prompt(basic_prompt):
    """
    Enhance a basic prompt with quality modifiers for better image generation

    Args:
        basic_prompt (str): Basic prompt from user

    Returns:
        str: Enhanced prompt with quality modifiers
    """
    quality_modifiers = [
        "high quality",
        "detailed",
        "professional",
        "masterpiece",
        "8k resolution",
        "photorealistic",
    ]

    # Add quality modifiers if not already present
    enhanced = basic_prompt
    for modifier in quality_modifiers[:3]:  # Add first 3 modifiers
        if modifier not in enhanced.lower():
            enhanced += f", {modifier}"

    return enhanced


if __name__ == "__main__":
    # This runs when the file is executed as a subprocess
    process_image_generation_request()
