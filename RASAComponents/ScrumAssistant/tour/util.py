import json
from typing import Dict

from RASAComponents.ScrumAssistant.tour.event_handling import EventPublisher
from RASAComponents.ScrumAssistant.tour.conversation import abstract_flow, concrete_flow
from RASAComponents.ScrumAssistant.tour.learning_styles_detection import Dimension, DimensionLevel
from RASAComponents.ScrumAssistant.tour.topic import topics


def move_to_location(response):
    locations = {
        "utter_start_tour": "tour_scrum_assistant_p1",
        "utter_move_to_planning_room": "tour_scrum_assistant_p2",
        "utter_move_to_development_room": "tour_scrum_assistant_p5",
        "utter_move_to_meeting_room": "tour_scrum_assistant_p6",
        "utter_move_to_kanban": "tour_scrum_assistant_p4",
        "utter_move_to_office": "tour_scrum_assistant_p3",
        "utter_finish_tour": "finish_tour"
    }

    publisher = EventPublisher(exchange_name="log_eventos", host="localhost")
    if locations.get(response) is not None:
        publisher.publish("movement_now",
                          {"location": locations.get(response),
                           "recipient": "Scrum Assistant"})


def move_task(response):
    state = {
        "utter_task_in_progress": "IN PROGRESS",
        "utter_task_done": "DONE"
    }

    publisher = EventPublisher(exchange_name="log_eventos", host="localhost")
    if state.get(response) is not None:
        publisher.publish("task",
                          {"recipient": "Scrum Assistant",
                           "action": "change_state",
                           "new_state": state.get(response),
                           "id_artefacto": "40"})


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
        # Movement commands.
        "utter_start_tour",
        "utter_move_to_planning_room",
        "utter_move_to_development_room",
        "utter_move_to_meeting_room",
        "utter_move_to_kanban",
        "utter_move_to_office",
        "utter_finish_tour",
        # Allow user integration with virtual world.
        "utter_daily_meeting",
        "utter_interact_with_kanban",
        # Require user input.
        "utter_ask",
        "utter_cross_examine_jump_global",
        "utter_cross_examine_jump_sequential",
        "utter_cross_examine_example",
        "utter_cross_examine_topic_scrum",
        "utter_cross_examine_topic_product_backlog",
        "utter_cross_examine_topic_product_owner",
        "utter_cross_examine_topic_epic",
        "utter_cross_examine_topic_scrum_master",
        # Others.
        "utter_default",
        "utter_sin_ejemplos",
        "utter_no_examples",
        "utter_sin_question"
    }

    return (intent_name not in intents_with_no_timer
            and predicted_utter not in utters_with_no_timer)
