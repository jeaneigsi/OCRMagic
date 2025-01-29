import torch
import psutil
import os
import json
import numpy as np
from PIL import Image
from together import Together
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("TOGETHER_API_KEY")

def clear_model(model):
    del model
    torch.cuda.empty_cache()

def overall_memory_usage():
    process = psutil.Process()
    memory_info = process.memory_info()
    memory_used = memory_info.rss / (1024 ** 2)  # Convert to MB
    print(f"Overall CPU memory used by the process: {memory_used:.2f} MB")
    return memory_used

def process(prediction):
    output = []
    for ocr_result in prediction:
        for text_line in ocr_result.text_lines:
            output.append(text_line.text)
    return output

def reduce_image_size(img: Image.Image, reduction_factor: float = 0.7) -> Image.Image:
    new_width = int(img.width * reduction_factor)
    new_height = int(img.height * reduction_factor)
    return img.resize((new_width, new_height))

def pil_to_np(img: Image.Image) -> np.ndarray:
    return np.array(img)


# Initialize the Together client
client = Together(api_key=api_key)

def improve_text(input_text):
    """
    Enhances the input text by making it more readable and adding extra information or commentary.

    Args:
        input_text (str): The text to improve.

    Returns:
        str: Enhanced text with better readability and added commentary.
    """
    system_prompt = "Make text readable and clear without additional informations and commentaries."

    response = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct-Turbo-Free",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": input_text}
        ],
    )
    
    return response.choices[0].message.content