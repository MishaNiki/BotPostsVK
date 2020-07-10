from enum import Enum


class State(Enum):
    """
        List of object states
    """
    INACTIVE = 0 # user does not work
    GET_POSTS_STAGE_1 = 1 # user must set community uuid or id
    GET_POSTS_STAGE_2 = 2 # user must set the number of posts


class Chat:
    """
        Object chat
    """
    state = State.INACTIVE
    group_id = -1 # selected group
    groups = dict() # chat group dictionary, key: id group, value: name group

    def set_state(self, state):
        """ Update state chat """
        self.state = state

    def select_group_id(self, id):
        """ adding community id as selected by user """
        self.group_id = str(id)

    def set_group(self, name):
        self.groups[str(self.group_id)] = name
