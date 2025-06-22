import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a function call plan, you can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""

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
    description="Reads the contents of a specified file in the working directory and returns it as a string. If the file exceeds 10,000 characters, the output is truncated to prevent large responses.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file whose contents should be read, relative to the working directory. Must point to a regular file.",
            )
        },
    ),
)

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file located within the working directory and returns its output, including stdout, stderr, and exit code if applicable.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory. Must point to a '.py' file.",
            )
        },
    ),
)

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes or overwrites the content of a file within the working directory. Creates the file and any necessary parent directories if they don't exist.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to write to, relative to the working directory. If the file or its directories do not exist, they will be created.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write into the file.",
            ),
        },
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

function_map = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}

WORKING_DIRECTORY = "./calculator"


def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    arguments = dict(function_call_part.args)

    if verbose:
        print(f"Calling function: {function_name}({arguments})")
    else:
        print(f" - Calling function: {function_name}")

    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    arguments["working_directory"] = WORKING_DIRECTORY

    try:
        function_result = function_map[function_name](**arguments)
    except Exception as e:
        function_result = f"Error: Exception when executing function: {e}"

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set.")
        sys.exit(1)
    return api_key


def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <prompt> [--verbose]")
        sys.exit(1)

    verbose = False
    args = sys.argv[1:]
    if "--verbose" in args:
        verbose = True
        args.remove("--verbose")

    prompt = " ".join(args)
    return prompt, verbose


def generate_response(client, prompt):
    messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
    config = types.GenerateContentConfig(
        tools=[available_functions], system_instruction=system_prompt
    )
    response = client.models.generate_content(
        model="gemini-2.0-flash-001", contents=messages, config=config
    )
    return response


def main():
    api_key = load_api_key()
    prompt, verbose = parse_arguments()
    client = genai.Client(api_key=api_key)

    response = generate_response(client, prompt)

    function_calls = getattr(response, "function_calls", None)
    if function_calls:
        for function_call_part in function_calls:
            function_call_result = call_function(function_call_part, verbose)

            parts = getattr(function_call_result, "parts", None)
            first_part = parts[0] if parts else None
            function_response = getattr(first_part, "function_response", None)
            response_result = getattr(function_response, "response", None)

            if not response_result:
                print("Error: Invalid function response")
                sys.exit(1)

            if verbose:
                print(f"-> {response_result}")
    else:
        text = getattr(response, "text", None)
        if text:
            print(text)
        else:
            print("[No response text received]")


if __name__ == "__main__":
    main()
