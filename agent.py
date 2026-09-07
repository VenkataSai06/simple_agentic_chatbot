import json
from groq import Groq
from dotenv import load_dotenv
import os

from tools import (
    safe_calculate,
    get_current_time,
    save_note,
    get_notes
)


load_dotenv()


api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    raise RuntimeError(
        "Missing GROQ_API_KEY environment variable. "
        "Create a .env file with GROQ_API_KEY=your_key"
    )


client = Groq(
    api_key=api_key
)


# ==========================
# TOOL DEFINITIONS
# ==========================

tools = [

    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": (
                "Perform mathematical calculations. "
                "Use this whenever the user asks for arithmetic."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": (
                            "Mathematical expression, "
                            "for example: 25 * 40"
                        )
                    }
                },
                "required": ["expression"]
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": (
                "Get the current local date, time, and day."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "save_note",
            "description": (
                "Save a note or important information "
                "when the user asks you to remember something."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "note": {
                        "type": "string",
                        "description": (
                            "The information that should be saved."
                        )
                    }
                },
                "required": ["note"]
            }
        }
    },


    {
        "type": "function",
        "function": {
            "name": "get_notes",
            "description": (
                "Retrieve all previously saved notes "
                "when the user asks what information "
                "has been saved or remembered."
            ),
            "parameters": {
                "type": "object",
                "properties": {}
            }
        }
    }

]


# ==========================
# EXECUTE TOOL
# ==========================

def execute_tool(function_name, arguments):

    if function_name == "calculate":

        return safe_calculate(
            arguments["expression"]
        )


    elif function_name == "get_current_time":

        return get_current_time()


    elif function_name == "save_note":

        return save_note(
            arguments["note"]
        )


    elif function_name == "get_notes":

        return get_notes()


    return {
        "error": "Unknown tool"
    }


# ==========================
# AGENT FUNCTION
# ==========================

def run_agent(user_message, chat_history=None):

    if chat_history is None:
        chat_history = []


    messages = [

        {
            "role": "system",
            "content": """
You are a helpful AI assistant.

You have access to tools.

Use tools when necessary.

IMPORTANT RULES:

1. Use the calculator tool for mathematical calculations.
2. Use the time tool when the user asks for the current time or date.
3. Use save_note when the user asks you to remember or save information.
4. Use get_notes when the user asks what you remember or what notes are saved.
5. Do not pretend that you used a tool when you did not.
6. After receiving a tool result, explain the answer naturally.
"""
        }

    ]


    # Add previous chat history
    messages.extend(chat_history)


    # Add current user message
    messages.append(
        {
            "role": "user",
            "content": user_message
        }
    )


    # ==========================
    # FIRST LLM CALL
    # ==========================

    response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=messages,

        tools=tools,

        tool_choice="auto"

    )


    response_message = response.choices[0].message


    # ==========================
    # IF NO TOOL IS REQUIRED
    # ==========================

    if not response_message.tool_calls:

        return {
            "response": response_message.content,
            "tool_used": None
        }


    # ==========================
    # ADD AGENT RESPONSE
    # ==========================

    messages.append(
        response_message
    )


    used_tools = []


    # ==========================
    # EXECUTE TOOLS
    # ==========================

    for tool_call in response_message.tool_calls:

        function_name = tool_call.function.name

        arguments = json.loads(
            tool_call.function.arguments
        )


        result = execute_tool(
            function_name,
            arguments
        )


        used_tools.append(
            function_name
        )


        # Add tool result
        messages.append(
            {
                "role": "tool",

                "tool_call_id": tool_call.id,

                "name": function_name,

                "content": json.dumps(result)
            }
        )


    # ==========================
    # SECOND LLM CALL
    # ==========================

    final_response = client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=messages

    )


    return {
        "response": final_response.choices[0].message.content,

        "tool_used": used_tools
    }