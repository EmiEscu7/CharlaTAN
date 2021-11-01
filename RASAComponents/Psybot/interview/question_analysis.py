from typing import Callable, Dict

from interview.elements import Interview


def queue_question(interview: Interview, **args):
    if "question_id" not in args:
        raise KeyError("Missing 'question_id' argument in function "
                       "'queue_question'")

    interview.queue_question(interview.get_question(args["question_id"]))


def update_dimension(interview: Interview, **args):
    if "dimension" not in args:
        raise KeyError("Missing 'dimension' argument in function "
                       "'update_dimension'")
    if "value" not in args:
        raise KeyError("Missing 'value' argument in function "
                       "'update_dimension'")

    interview.update_profile(args["dimension"], args["value"])


def get_all_functions() -> Dict[str, Callable]:
    return {
        queue_question.__name__: queue_question,
        update_dimension.__name__: update_dimension
    }
