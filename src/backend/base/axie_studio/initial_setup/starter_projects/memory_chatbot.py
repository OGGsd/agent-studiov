from axie_studio.components.helpers.memory import MemoryComponent
from axie_studio.components.input_output import ChatInput, ChatOutput
from axie_studio.components.openai.openai_chat_model import OpenAIModelComponent
from axie_studio.components.processing import PromptComponent
from axie_studio.components.processing.converter import TypeConverterComponent
from axie_studio.graph import Graph


def memory_chatbot_graph(template: str | None = None):
    if template is None:
        template = """{context}

    User: {user_message}
    AI: """
    memory_component = MemoryComponent()
    chat_input = ChatInput()
    type_converter = TypeConverterComponent()
    type_converter.set(input_data=memory_component.retrieve_messages_dataframe)
    prompt_component = PromptComponent()
    prompt_component.set(
        template=template,
        user_message=chat_input.message_response,
        context=type_converter.convert_to_message,
    )
    openai_component = OpenAIModelComponent()
    openai_component.set(input_value=prompt_component.build_prompt)

    chat_output = ChatOutput()
    chat_output.set(input_value=openai_component.text_response)

    return Graph(chat_input, chat_output)
