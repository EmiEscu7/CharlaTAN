from typing import List

from tour.conversation.abstract_flow import ConversationFlow
from tour.topic.topics import Topic
from tour.visitor.visitor import Visitor


class SequentialConversationFlow(ConversationFlow):
    """Implementation of ConversationFlow that traverses all topics, subtopics
    and examples that the flow contains.

    Author: Bruno.
    """

    def __init__(self, flow: List[Topic], name: str = ""):
        """Constructor.

        Author: Bruno.

        Parameters
        ----------
        flow
            Order of topics for the explanation.
        """
        super().__init__(flow, name)

    def next(self) -> str:
        """Determines next explanation to give. For this implementation, a
        topic is explained, then his examples, and lastly his subtopics.

        Author: Bruno.

        Returns
        -------
        Next explanation to give.
        """
        # Gets the next explanation to give, that wasn't explained previously.
        # If the next to explain is None, then remove the current explanation
        # and continue with the next in the flow.
        while (len(self._to_explain_stack) > 0
               and self._to_explain_stack[-1].is_explained):
            next_to_explain = self._to_explain_stack[-1].next()
            if next_to_explain is None:
                self._to_explain_stack.pop()
            else:
                self._to_explain_stack.append(next_to_explain)

        if len(self._to_explain_stack) == 0:
            return "utter_ask"

        return self._to_explain_stack[-1].get_explanation()

    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_sequential(self)


class GlobalConversationFlow(ConversationFlow):
    """Implementation of ConversationFlow that traverses only the topics
    specified in the flow, ignoring examples and subtopics.

    Author: Tomas.
    """

    def __init__(self, flow: List[Topic], name: str = ""):
        """Constructor.

        Author: Tomas.

        Parameters
        ----------
        flow
            Order of topics for the explanation.
        """
        super().__init__(flow, name)

    def next(self) -> str:
        """Iterates over the conversation flow not entering in the subtopics of
        the topic.

        Author: Tomas.

        Returns
        -------
        Utter associated to the next topic.
        """
        if self._to_explain_stack[-1].is_explained:
            self._to_explain_stack.pop()
        if len(self._to_explain_stack) == 0:
            return "utter_ask"

        return self._to_explain_stack[-1].get_explanation()

    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_global(self)


class NeutralConversationFlow(ConversationFlow):

    def __init__(self, flow: List[Topic], name: str = ""):
        """Constructor.

        Author: Adrian.

        Parameters
        ----------
        flow
            Order of topics for the explanation.
        """
        super().__init__(flow, name)

    def next(self) -> str:
        """Iterates over the conversation flow entering only in the first
        subtopic of the topic

        Author: Adrian.

        Returns
        -------
        Utter associated to the next topic.
        """
        while (len(self._to_explain_stack) > 0
               and self._to_explain_stack[-1].is_explained):
            if self._to_explain_stack[-1].get_amount_subtopics() < 1:
                next_to_explain = self._to_explain_stack[-1].next()
                if next_to_explain is None:
                    self._to_explain_stack.pop()
                else:
                    self._to_explain_stack.append(next_to_explain)
            else:
                self._to_explain_stack.pop()

        if len(self._to_explain_stack) == 0:
            return "utter_ask"

        return self._to_explain_stack[-1].get_explanation()

    def accept(self, visitor: Visitor) -> str:
        return visitor.visit_neutral(self)
