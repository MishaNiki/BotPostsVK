from model import chat

class TestStorage:
    """
        Memory storage
        stores information about each chat
    """
    def __init__(self):
        self.chats = dict() # stores objects of type chat, key: chat id

    def get_chat(self, id):
        """
            Get object chat by id
        """

        # implicit chat object initialization
        if self.chats.get(id) is None :
            self.chats[id] = chat.Chat()
        return self.chats[id]