import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file


load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Error: GEMINI_API_KEY not set in environment.")
    sys.exit(1)

client = genai.Client(api_key=api_key)

if len(sys.argv) <= 1:
    print("Usage: python main.py <prompt> [--verbose]")
    sys.exit(1)

user_prompt = sys.argv[1]

# Create function declaration schema for get_files_info
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)

# Create available functions tool
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)

# Updated system prompt with function usage instructions
system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

response = client.models.generate_content(
    model='gemini-2.0-flash-001',
    contents=messages,
    config=types.GenerateContentConfig(
        tools=[available_functions],
        system_instruction=system_prompt
    ),
)

# Check if the LLM made function calls
if response.candidates[0].content.parts:
    for part in response.candidates[0].content.parts:
        if hasattr(part, 'function_call') and part.function_call:
            function_call_part = part.function_call
            print(f"Calling function: {function_call_part.name}({function_call_part.args})")
        elif hasattr(part, 'text') and part.text:
            print(part.text)

if len(sys.argv) == 3 and sys.argv[2] == "--verbose":
    print("User prompt:", user_prompt)
    print("Prompt tokens:", response.usage_metadata.prompt_token_count)
    print("Response tokens:", response.usage_metadata.candidates_token_count)
