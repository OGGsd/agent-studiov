from axie_studio.services.chat.service import ChatService
from axie_studio.services.factory import ServiceFactory


class ChatServiceFactory(ServiceFactory):
    def __init__(self) -> None:
        super().__init__(ChatService)

    def create(self):
        # Here you would have logic to create and configure a ChatService
        return ChatService()
