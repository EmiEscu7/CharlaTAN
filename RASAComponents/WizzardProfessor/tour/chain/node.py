import abc

from rasa.shared.core.trackers import DialogueStateTracker

from RASAComponents.WizzardProfessor.tour import util as tour_util
from RASAComponents.WizzardProfessor.tour.chain.criterion import Criterion
from RASAComponents.WizzardProfessor.tour.conversation.abstract_flow import ConversationFlow
from RASAComponents.WizzardProfessor.tour.visitor.ask_visitor import AskVisitor
from RASAComponents.WizzardProfessor.tour.visitor.example_visitor import ExampleVisitor
from RASAComponents.WizzardProfessor.tour.visitor.topic_visitor import TopicVisitor


class Node(metaclass=abc.ABCMeta):

    def __init__(self, criterion: Criterion) -> None:
        self._criterion = criterion

    @abc.abstractmethod
    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        raise NotImplementedError


class DefaultNode(Node):

    def __init__(self, criterion: Criterion) -> None:
        super().__init__(criterion)
        self._utters = {}

    @property
    def utters(self):
        return self._utters

    @utters.setter
    def utters(self, utters):
        self._utters = utters

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        last_intent_name = tracker.latest_message.intent["name"]
        if "utter_" + last_intent_name not in self._utters:
            return "utter_default"
        return "utter_" + last_intent_name


class NodeGet(Node):

    def __init__(
            self,
            node: Node,
            criterion: Criterion,
            jump: bool = None,
            example: bool = None
    ) -> None:
        self._node = node
        self._jump = jump
        self._example = example
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            if self._jump is not None:
                it.jump = self._jump
                return it.accept(
                    TopicVisitor(it.current_topic, self._example)
                )
            if self._example is not None:
                return it.accept(
                    TopicVisitor(it.current_topic, self._example)
                )
            return it.accept(
                TopicVisitor(
                    next(tracker.get_latest_entity_values("topic"), None),
                    self._example)
            )
        else:
            return self._node.next(it, tracker)


class NodeActionListen(Node):

    def __init__(self, next_node: Node, criterion: Criterion) -> None:
        super().__init__(criterion)
        self._node = next_node

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            return "action_listen"
        else:
            return self._node.next(it, tracker)


class NodeRepeat(Node):

    def __init__(self, node: Node, criterion: Criterion) -> None:
        self._node = node
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            return it.repeat()
        else:
            return self._node.next(it, tracker)


class NodeNext(Node):

    def __init__(self, node: Node, criterion: Criterion) -> None:
        self._node = node
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            next_utter = it.next()
            return next_utter
        else:
            return self._node.next(it, tracker)


class NodeAsk(Node):

    def __init__(self, node: Node, criterion: Criterion) -> None:
        self._node = node
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            return it.accept(AskVisitor())
        else:
            return self._node.next(it, tracker)


class NodeExample(Node):

    def __init__(self, node: Node, criterion: Criterion) -> None:
        self._node = node
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            entity = next(tracker.get_latest_entity_values("topic"), None)
            topic = None if entity is None else entity.replace(" ", "_")
            return it.accept(
                ExampleVisitor(topic)
            )
        else:
            return self._node.next(it, tracker)


class NodeResponse(Node):

    def __init__(self, node: Node, criterion: Criterion) -> None:
        self._node = node
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            intent_name = tracker.latest_message.intent["name"]
            if intent_name == it.to_explain_stack[-1].get_question():
                return "utter_ask_good"
            else:
                return "utter_ask_bad"
        else:
            return self._node.next(it, tracker)


class NodeReset(Node):

    def __init__(self, node: Node, criterion: Criterion) -> None:
        self._node = node
        super().__init__(criterion)

    def next(self, it: ConversationFlow, tracker: DialogueStateTracker) -> str:
        if self._criterion.check(tracker):
            it.restart()
            return it.next()
        else:
            return self._node.next(it, tracker)
