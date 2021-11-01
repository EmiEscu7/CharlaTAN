from tour.conversation.abstract_flow import ConversationFlow
from tour.visitor.visitor import Visitor

AMT_EXAMPLE_NEUTRAL = 2


class ExampleVisitor(Visitor):

    def __init__(self, topic: str = None) -> None:
        self._topic = topic

    def visit_sequential(self, it: ConversationFlow) -> str:
        example = self.search(it)
        if example is None:
            return it.all_topics[self._topic].get_example()
        return example

    def visit_global(self, it: ConversationFlow) -> str:
        example = self.search(it)
        if example is None:
            example = it.all_topics[self._topic].get_example()
            it.all_topics[self._topic].set_current_example(0)
        return example

    def visit_neutral(self, it: ConversationFlow) -> str:
        example = self.search(it)
        if example is None:
            example = it.all_topics[self._topic].get_example()
            if it.all_topics[self._topic].get_current_example() > AMT_EXAMPLE_NEUTRAL:
                it.all_topics[self._topic].set_current_example(0)
        return example

    def search(self, it: ConversationFlow) -> str:
        if self._topic is None:
            return it.to_explain_stack[-1].get_example()
        else:
            if self._topic not in it.all_topics:
                return "action_topic_not_recognized"
            else:
                return None
