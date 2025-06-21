import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

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


def load_api_key():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        print("Error: GEMINI_API_KEY is not set in environment variables.")
        sys.exit(1)
    return api_key


def parse_arguments():
    if len(sys.argv) < 2:
        print("Usage: python3 main.py <prompt>")
        sys.exit(1)
    return " ".join(sys.argv[1:])


def generate_response(client, prompt):
    try:
        messages = [types.Content(role="user", parts=[types.Part(text=prompt)])]
        config = types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
        response = client.models.generate_content(
            model="gemini-2.0-flash-001", contents=messages, config=config
        )
        return response
    except Exception as e:
        print(f"Error generating response: {e}")
        sys.exit(1)


def main():
    api_key = load_api_key()
    prompt = parse_arguments()

    client = genai.Client(api_key=api_key)
    response = generate_response(client, prompt)

    text = getattr(response, "text", None)
    function_calls = getattr(response, "function_calls", None)

    if function_calls:
        for function_call_part in function_calls:
            print(
                f"Calling function: {function_call_part.name}({function_call_part.args})"
            )
    elif text:
        print("\n--- Response ---")
        print(text)
    else:
        print("[No response text received]")


if __name__ == "__main__":
    main()
