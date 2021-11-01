from RASAComponents.ScrumAssistant.tour.topic.topics import Topic
from RASAComponents.ScrumAssistant.tour.conversation.abstract_flow import ConversationFlow
from RASAComponents.ScrumAssistant.tour.visitor.visitor import Visitor
from random import randint


class AskVisitor(Visitor):

    def __init__(self) -> None:
        super().__init__()

    def visit_sequential(self, it: ConversationFlow) -> str:
        return self.search_question(it)

    def visit_global(self, it: ConversationFlow) -> str:
        respond = "utter_sin_question"
        it.restart()
        question = 0
        keys = list(it.all_topics.keys())
        while (
                respond == "utter_sin_question"
                and Topic(keys[question], []) in it.to_explain_stack
        ):
            question = randint(0, len(it.all_topics) - 1)
            respond = it.all_topics[keys[question]].get_question()
        it.jump_to_topic(Topic(keys[question], []))
        return respond

    def visit_neutral(self, it: ConversationFlow) -> str:
        return self.search_question(it)

    def search_question(self, it: ConversationFlow) -> str:
        respond = "utter_sin_question"
        it.restart()
        keys = list(it.all_topics.keys())
        while respond == "utter_sin_question":
            question = randint(0, len(it.all_topics) - 1)
            respond = it.all_topics[keys[question]].get_question()
        it.jump_to_topic(Topic(keys[question], []))
        return respond
