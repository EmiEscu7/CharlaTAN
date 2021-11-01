from RASAComponents.WizzardProfessor.tour.topic.topics import Topic
from RASAComponents.WizzardProfessor.tour.iterator.iterator import Iterator
from RASAComponents.WizzardProfessor.tour.visitor.visitor import Visitor
from random import randint


class Ask(Visitor):

    def __init__(self) -> None:
        super().__init__()

    def visit_sequential(self, it: Iterator) -> str:
        return self.search_question(it)

    def visit_global(self, it: Iterator) -> str:
        respond = "utter_sin_question"
        it.restart()
        question = 0
        keys = list(it.get_intents_to_topic().keys())
        while respond == "utter_sin_question" and Topic(keys[question],[]) in it.get_to_explain():
            question = randint(0, len(it.get_intents_to_topic()) - 1)
            respond = it.get_intents_to_topic()[keys[question]].get_question()
        it.jump_to_topic(Topic(keys[question],[]))
        return respond

    def visit_neutral(self, it: Iterator) -> str:
        return self.search_question(it)

    def search_question(self, it: Iterator) -> str:
        respond = "utter_sin_question"
        it.restart()
        keys = list(it.get_intents_to_topic().keys())
        while respond == "utter_sin_question":
            question = randint(0, len(it.get_intents_to_topic()) - 1)
            respond = it.get_intents_to_topic()[keys[question]].get_question()
        it.jump_to_topic(Topic(keys[question],[]))
        return respond