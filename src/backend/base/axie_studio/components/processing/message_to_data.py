from loguru import logger

from axie_studio.custom.custom_component.component import Component
from axie_studio.io import MessageInput, Output
from axie_studio.schema.data import Data
from axie_studio.schema.message import Message


class MessageToDataComponent(Component):
    display_name = "Message to Data"
    description = "Convert a Message object to a Data object"
    icon = "message-square-share"
    beta = True
    name = "MessagetoData"
    legacy = True

    inputs = [
        MessageInput(
            name="message",
            display_name="Message",
            info="The Message object to convert to a Data object",
        ),
    ]

    outputs = [
        Output(display_name="Data", name="data", method="convert_message_to_data"),
    ]

    def convert_message_to_data(self) -> Data:
        if isinstance(self.message, Message):
            # Convert Message to Data
            return Data(data=self.message.data)

        msg = "Error converting Message to Data: Input must be a Message object"
        logger.opt(exception=True).debug(msg)
        self.status = msg
        return Data(data={"error": msg})
