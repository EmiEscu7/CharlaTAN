from RASAComponents.WizzardProfessor.tour.topic.topics import Topic
from typing import Dict, List
from RASAComponents.WizzardProfessor.tour.iterator.iterator import Iterator
from RASAComponents.WizzardProfessor.tour.visitor.visitor import Visitor


class SequentialIterator(Iterator):

    def __init__(self, flow: List[Topic]):
        super().__init__(flow)

    def next(self) -> str:
        while len(self._to_explain) > 0 and self._to_explain[-1].is_explained:
            next_to_explain = self._to_explain[-1].next()
            if next_to_explain is None:
                self._to_explain.pop()
            else:
                self._to_explain.append(next_to_explain)

        if len(self._to_explain) == 0:
            return "utter_ask"

        return self._to_explain[-1].get_explanation()

    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_sequential(self)


class GlobalIterator(Iterator):

    def __init__(self,flow: List[Topic]):
        super().__init__(flow)

    """
    Iterates over the conversation flow not entering in the subtopics of the topic

    Author: Tomas.

    Returns
    -------
        Utter associated to the next topic.
    """

    def next(self) -> str:
        if self._to_explain[-1].is_explained:
            self._to_explain.pop()
        if len(self._to_explain) == 0:
            return "utter_ask"

        return self._to_explain[-1].get_explanation()

    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_global(self)


class NeutralIterator(Iterator):

    def __init__(self, flow: List[Topic]):
        super().__init__(flow)

    """
    Iterates over the conversation flow entering only in the first subtopic of the topic

    Author: Adrian.

    Returns
    -------
        Utter associated to the next topic.
    """

    def next(self) -> str:
        while len(self._to_explain) > 0 and self._to_explain[-1].is_explained:
            if self._to_explain[-1].get_amount_subtopics() < 1:
                next_to_explain = self._to_explain[-1].next()
                if next_to_explain is None:
                    self._to_explain.pop()
                else:
                    self._to_explain.append(next_to_explain)
            else:
                self._to_explain.pop()

        if len(self._to_explain) == 0:
            return "utter_ask"

        return self._to_explain[-1].get_explanation()

    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_neutral(self)
