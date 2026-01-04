import asyncio
import os
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.connectors.ai.function_choice_behavior import FunctionChoiceBehavior
from semantic_kernel.connectors.ai.chat_completion_client_base import ChatCompletionClientBase
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.functions.kernel_arguments import KernelArguments
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import (
    OpenAIChatPromptExecutionSettings,
)

from plugins.insurance_position_plugin import insurance_position_plugin
from plugins.conditions_plugin import conditions_plugin

load_dotenv()

async def main():
    kernel = Kernel()

    chat_completion = OpenAIChatCompletion(
        ai_model_id=os.getenv("OPENAI_MODEL", "gpt-4"),
        api_key=os.getenv("OPENAI_API_KEY"),
    )
    kernel.add_service(chat_completion)
    kernel.add_plugin(conditions_plugin(), plugin_name="conditions_analyzer")
    kernel.add_plugin(insurance_position_plugin(), plugin_name="insurance_position_handler")

    execution_settings = OpenAIChatPromptExecutionSettings()
    execution_settings.function_choice_behavior = FunctionChoiceBehavior.Auto()

    history = ChatHistory()

    userInput = None
    while True:
        userInput = input("User > ")

        if userInput == "exit":
            break

        history.add_user_message(userInput)

        result = await chat_completion.get_chat_message_content(
            chat_history=history,
            settings=execution_settings,
            kernel=kernel,
        )

        print("Assistant > " + str(result))

        history.add_message(result)
        
if __name__ == "__main__":
    asyncio.run(main())