from tour.conversation.abstract_flow import ConversationFlow
from tour.topic.topics import Topic
from tour.visitor.visitor import Visitor


class TopicVisitor(Visitor):

    def __init__(self, topic: str, example: bool = None) -> None:
        self._topic = topic.replace(" ", "_")
        self._example = example

    def visit_sequential(self, it: ConversationFlow) -> str:
        if it.is_older_topic(Topic(self._topic, [])):
            if it.jump is None:
                it.current_topic = self._topic
                return "utter_cross_examine_jump_sequential"
            else:
                return self.get_topic(it)
        else:
            return self.get_topic(it)

    def visit_global(self, it: ConversationFlow) -> str:
        if (
                not it.is_older_topic(Topic(self._topic, []))
                and not it.to_explain_stack[-1].get_id() == self._topic
        ):
            if it.jump is None:
                it.current_topic = self._topic
                return "utter_cross_examine_jump_global"
            else:
                return self.get_topic(it, it.jump)
        else:
            return self.get_topic(it)

    def visit_neutral(self, it: ConversationFlow) -> str:
        return self.get_topic(it)

    def get_topic(self, it: ConversationFlow, jump: bool = False) -> str:
        if it.is_older_topic(Topic(self._topic, [])):
            if self._example is None:
                it.current_topic = self._topic
                return "utter_cross_examine_example"
        if self._topic not in it.all_topics:
            return "action_topic_not_recognized"
        if jump:
            it.jump_to_topic(Topic(self._topic, []))
        if self._example:
            return it.all_topics[self._topic].get_example()
        return it.all_topics[self._topic].get_explanation()
