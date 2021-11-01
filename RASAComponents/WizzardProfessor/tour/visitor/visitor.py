import abc
from ..conversation.abstract_flow import ConversationFlow


class Visitor(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def visit_sequential(self, it: ConversationFlow) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_global(self, it: ConversationFlow) -> str:
        raise NotImplementedError

    @abc.abstractmethod
    def visit_neutral(self, it: ConversationFlow) -> str:
        raise NotImplementedError
