import regex as re
import json
from typing import List
import openai
from pathlib import Path
from structs import ApiResultFiltSubtitles, Subtitle


KEY = (Path(__file__).parent / "api.txt").read_text().strip()

ROOT = Path(__file__).parent

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "filter_subtitles",
            "description": "Handle filtered subtitles by topic.",
            "parameters": {
                "type": "object",
                "properties": {
                    "subtitles": {
                        "type": "array",
                        "description": "A list of subtitle items, each item structured as {'begin': 'time', 'end': 'time', 'text': 'subtitle text'}.",
                        "items": {
                            "type": "object",
                            "properties": {
                                "begin": {
                                    "type": "string",
                                    "description": "The time at which the subtitle begins",
                                },
                                "end": {
                                    "type": "string",
                                    "description": "The time at which the subtitle ends",
                                },
                                "text": {
                                    "type": "string",
                                    "description": "The text of the subtitle",
                                },
                                "rating": {
                                    "type": "number",
                                    "description": "The relevance of the subtitle to the topic (0-1)",
                                },
                            },
                            "required": ["begin", "end", "text", "rating"],
                        },
                    },
                    "topic": {
                        "type": "string",
                        "description": "The topic to filter subtitles by relevance.",
                    },
                    # "best_timestamps": {
                    #     "type": "array",
                    #     "description": "A list of timestamps in which the subtitles are very strongly related to the topic",
                    #     "items": {
                    #         "type": "string",
                    #         "description": "A timestamp in the format '00:00:00'",
                    #     },
                    # },
                },
                "required": ["subtitles", "topic"],
            },
        },
    }
]


def force_tool(tool: dict):
    return {"type": "function", "function": {"name": tool["function"]["name"]}}


def filter_subtitles(subtitles: List[Subtitle], topic: str):
    api = openai.OpenAI(api_key=KEY)
    response = api.beta.chat.completions.parse(
        model="gpt-4o-2024-08-06",
        # tools=TOOLS,
        # tool_choice=force_tool(TOOLS[0]),
        messages=[
            {
                "role": "system",
                "content": """
                      Select items from the data["subtitles"]
                      list of items given by the user that are relevant to the topic specified
                      in the "topic" key of the data. Call a function using the filtered list of items in the same JSON format
                """,
            },
            {
                "role": "user",
                "content": json.dumps({"subtitles": subtitles, "topic": topic}),
            },
        ],
        response_format=ApiResultFiltSubtitles,
    )
    res = (
        response.choices[0].message.parsed
        if not response.choices[0].message.refusal
        else None
    )
    return res
    # # tool_calls = response.choices[0].message.tool_calls
    # # if not tool_calls:
    # #     return None
    # (ROOT / "tool_calls.json").write_text(res)
    # # clean_res_str = clean_json_string(tool_calls[0].function.arguments)
    # # full_res = json.loads(clean_res_str)
    # # subtitles_filt = full_res.get("subtitles", [])
    # # return {"result": full_res, "removed": len(subtitles) - len(subtitles_filt)}


def clean_json_string(dirty_json: str) -> str:
    """
    Extract first list with subtitles key from json string response from OpenAI

    Needed as sometimes gibberish is added at the end
    """
    try:
        json.loads(dirty_json)
        return dirty_json
    except json.JSONDecodeError:
        single_line = re.sub(r"\s+", " ", dirty_json)
        valid_str = re.search('subtitles":(.*?)]', single_line)
        if valid_str:
            end = valid_str.end()
            return valid_str.string[:end] + "}"
        return None
