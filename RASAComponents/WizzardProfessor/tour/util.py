import json
from typing import Dict

from RASAComponents.WizzardProfessor.tour.conversation import abstract_flow, concrete_flow
from RASAComponents.WizzardProfessor.tour.learning_styles_detection import Dimension, DimensionLevel
from RASAComponents.WizzardProfessor.tour.topic import topics

def create_conversation_flows(path_flow: str
                              ) -> Dict[str, abstract_flow.ConversationFlow]:
    """Creates the iterators that can be used in the TourPolicy.

    Author: Bruno.

    Parameters
    ----------
    path_flow
        Path where the tour flow is defined.

    Returns
    -------
    Dict {k: v}, where k is an conversation name, and v is an conversation object.
    """
    with open(path_flow) as file:
        flow = [topics.parse_topic(raw_topic) for raw_topic in json.load(file)]
    return {
        "global": concrete_flow.GlobalConversationFlow(name="global",
                                                       flow=flow),
        "neutral": concrete_flow.NeutralConversationFlow(name="neutral",
                                                         flow=flow),
        "seq": concrete_flow.SequentialConversationFlow(name="seq",
                                                        flow=flow)
    }


def create_dimension(iterators: Dict[str, abstract_flow.ConversationFlow]
                     ) -> "Dimension":
    """Creates the dimension used by the LearningStyleDetector.

    Author: Bruno.

    Parameters
    ----------
    iterators
        Dict {k: v}, where k is an conversation name, and v is an conversation object.

    Returns
    -------
    Created dimension.
    """
    return Dimension(
        name="perception",
        threshold=3.,
        levels=[
            DimensionLevel("global", iterators["global"]),
            DimensionLevel("neutral", iterators["neutral"]),
            DimensionLevel("seq", iterators["seq"])
        ]
    )


def must_set_timer(intent_name: str, predicted_utter: str) -> bool:
    """Determines if a timer must be set after an explanation is given.

    If the received intent is in the set 'intents_with_no_timer', the timer
    must not be set. If the predicted utter is in 'utters_with_no_timer', the
    timer must not be set, making the assistant wait for user confirmation
    before continuing with next explanations.

    Author: Bruno.

    Parameters
    ----------
    intent_name
        Last detected intent.
    predicted_utter
        Last predicted utter.

    Returns
    -------
    True if timer must be set, False otherwise.
    """
    intents_with_no_timer = {
        "greet",
        "goodbye"
    }

    utters_with_no_timer = {
        "utter_start_tour",
        "utter_move_to_planning_room",
        "utter_move_to_development_room",
        "utter_move_to_meeting_room",
        "utter_daily_meeting",
        "utter_move_to_kanban",
        "utter_interact_with_kanban",
        "utter_move_to_office",
        "utter_finish_tour"
    }

    return (intent_name not in intents_with_no_timer
            and predicted_utter not in utters_with_no_timer)
