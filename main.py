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

def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = dict(function_call_part.args)

    if verbose:
        print(f"Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_args['working_directory'] = './calculator'

    available_function_map = {
        'get_files_info': get_files_info,
        'get_file_content': get_file_content,
        'write_file': write_file,
        'run_python_file': run_python_file,
    }

    if function_name not in available_function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    try:
        function_to_call = available_function_map[function_name]
        function_result = function_to_call(**function_args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"result": function_result},
                )
            ],
        )
    except Exception as e:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Error calling function: {str(e)}"},
                )
            ],
        )

if len(sys.argv) <= 1:
    print("Usage: python main.py <prompt> [--verbose]")
    sys.exit(1)

user_prompt = sys.argv[1]
verbose = len(sys.argv) == 3 and sys.argv[2] == "--verbose"

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

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Reads and returns the content of a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns its output, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory.",
            ),
        },
        required=["file_path"],
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites content to a specified file, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            ),
        },
        required=["file_path", "content"],
    ),
)

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

messages = [
    types.Content(role="user", parts=[types.Part(text=user_prompt)]),
]

max_iterations = 20
for iteration in range(max_iterations):
    response = client.models.generate_content(
        model='gemini-2.0-flash-001',
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt
        ),
    )

    function_called = False
    for candidate in response.candidates:
        messages.append(candidate.content)

        for part in candidate.content.parts:
            if hasattr(part, 'function_call') and part.function_call:
                function_called = True
                function_call_part = part.function_call
                function_call_result = call_function(function_call_part, verbose)

                if not (hasattr(function_call_result, 'parts') and
                        len(function_call_result.parts) > 0 and
                        hasattr(function_call_result.parts[0], 'function_response')):
                    raise Exception("Function call result does not have expected structure")

                messages.append(function_call_result)

                if verbose:
                    print(f"-> {function_call_result.parts[0].function_response.response}")

    if not function_called:
        for candidate in response.candidates:
            for part in candidate.content.parts:
                if hasattr(part, 'text') and part.text:
                    print("Final response:")
                    print(part.text)
        break

    if verbose:
        print("User prompt:", user_prompt)
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
