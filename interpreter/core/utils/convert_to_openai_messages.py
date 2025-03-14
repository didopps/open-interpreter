import json


def convert_to_openai_messages(messages, function_calling=True):
    """
    Converts LMC messages into OpenAI messages
    """
    new_messages = []

    for message in messages:
        if "recipient" in message:
            if message["recipient"] != "assistant":
                continue

        new_message = {}

        if message["type"] == "message":
            new_message["role"] = message[
                "role"
            ]  # This should never be `computer`, right?
            new_message["content"] = message["content"]

        elif message["type"] == "code":
            new_message["role"] = "assistant"
            if function_calling:
                new_message["function_call"] = {
                    "name": "execute",
                    "arguments": json.dumps(
                        {"language": message["format"], "code": message["content"]}
                    ),
                    # parsed_arguments isn't actually an OpenAI thing, it's an OI thing.
                    # but it's soo useful!
                    "parsed_arguments": {
                        "language": message["format"],
                        "code": message["content"],
                    },
                }
            else:
                new_message[
                    "content"
                ] = f"""```{message["format"]}\n{message["content"]}\n```"""

        elif message["type"] == "console" and message["format"] == "output":
            if function_calling:
                new_message["role"] = "function"
                new_message["name"] = "execute"
                new_message["content"] = message["content"]

            else:
                if message["content"] == "No output":
                    content = "The code above was executed on my machine. It produced no output. Was that expected?"
                else:
                    content = (
                        "Code output: "
                        + message["output"]
                        + "\n\nWhat does this output mean / what's next (if anything, or are we done)?"
                    )

                new_messages.append(
                    {
                        "role": "user",
                        "content": content,
                    }
                )

        elif message["type"] == "image":
            new_message = {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": message["content"], "detail": "high"},
                    }
                ],
            }

        else:
            raise Exception(f"Unable to convert this message type: {message}")

        new_messages.append(new_message)

    """
    # Combine adjacent user messages
    combined_messages = []
    i = 0
    while i < len(new_messages):
        message = new_messages[i]
        if message["role"] == "user":
            combined_content = []
            while i < len(new_messages) and new_messages[i]["role"] == "user":
                if isinstance(new_messages[i]["content"], str):
                    combined_content.append({
                        "type": "text",
                        "text": new_messages[i]["content"]
                    })
                elif isinstance(new_messages[i]["content"], list):
                    combined_content.extend(new_messages[i]["content"])
                i += 1
            message["content"] = combined_content
        combined_messages.append(message)
        i += 1
    new_messages = combined_messages

    if not function_calling:
        # Combine adjacent assistant messages, as "function calls" will just be normal messages with content: markdown code blocks
        combined_messages = []
        i = 0
        while i < len(new_messages):
            message = new_messages[i]
            if message["role"] == "assistant":
                combined_content = ""
                while i < len(new_messages) and new_messages[i]["role"] == "assistant":
                    combined_content += new_messages[i]["content"] + "\n\n"
                    i += 1
                message["content"] = combined_content.strip()
            combined_messages.append(message)
            i += 1
        new_messages = combined_messages
    """

    return new_messages
