from tour.chain.criterion import (
    AndCriterion,
    NotCriterion,
    EqualPenultimateEvent,
    EqualAction,
    EqualIntent,
    EqualEntity,
    OrCriterion
)
from tour.chain.node import (
    DefaultNode,
    Node,
    NodeActionListen,
    NodeNext,
    NodeGet,
    NodeRepeat,
    NodeExample,
    NodeAsk,
    NodeResponse
)


def chain_builder(last_node: DefaultNode) -> Node:
    """

    EqualAction("action_listen") checks if the last thing rasa did was listen to
    user input.


    Parameters
    ----------
    last_node

    Returns
    -------

    """
    # Allows apprentice to talk to us.
    chain = NodeActionListen(
        last_node,
        AndCriterion(
            NotCriterion(EqualPenultimateEvent("utter_cross_examine")),
            NotCriterion(EqualAction("action_listen"))
        )
    )
    # Advances to the next explanation.
    chain = NodeNext(
        chain,
        AndCriterion(
            AndCriterion(
                NotCriterion(EqualPenultimateEvent("utter_cross_examine")),
                EqualAction("action_listen")
            ),
            EqualIntent("affirm")
        )
    )
    # Explains a specific topic.
    chain = NodeGet(
        chain,
        AndCriterion(
            AndCriterion(
                NotCriterion(EqualPenultimateEvent("utter_cross_examine")),
                EqualAction("action_listen")
            ),
            AndCriterion(
                EqualIntent("explain_me_topic"), NotCriterion(EqualEntity(None))
            )
        )
    )
    # Re explains a topic.
    chain = NodeGet(
        chain,
        AndCriterion(
            AndCriterion(
                NotCriterion(EqualPenultimateEvent("utter_cross_examine")),
                EqualAction("action_listen")
            ),
            AndCriterion(
                EqualIntent("no_entiendo"), NotCriterion(EqualEntity(None))
            )
        )
    )
    chain = NodeRepeat(
        chain,
        OrCriterion(
            EqualAction("utter_ask_bad"),
            AndCriterion(
                AndCriterion(
                    NotCriterion(EqualPenultimateEvent("utter_cross_examine")),
                    EqualAction("action_listen")
                ),
                AndCriterion(EqualIntent("no_entiendo"), EqualEntity(None))
            )
        )
    )
    chain = NodeExample(
        chain,
        AndCriterion(
            AndCriterion(
                NotCriterion(EqualPenultimateEvent("utter_cross_examine")),
                EqualAction("action_listen")
            ),
            EqualIntent("need_example")
        )
    )
    chain = NodeGet(
        chain,
        AndCriterion(
            AndCriterion(
                EqualPenultimateEvent("utter_cross_examine"),
                EqualPenultimateEvent("utter_cross_examine_example")
            ),
            EqualIntent("need_example")
        ), example=True
    )
    chain = NodeGet(
        chain,
        AndCriterion(
            AndCriterion(
                EqualPenultimateEvent("utter_cross_examine"),
                EqualPenultimateEvent("utter_cross_examine_example")
            ),
            NotCriterion(EqualIntent("need_example"))
        ), example=False)
    chain = NodeGet(
        chain,
        AndCriterion(
            AndCriterion(
                EqualPenultimateEvent("utter_cross_examine"),
                EqualPenultimateEvent("utter_cross_examine_jump")
            ),
            EqualIntent("change_current_flow")
        ), jump=True
    )
    chain = NodeGet(
        chain,
        AndCriterion(
            AndCriterion(
                EqualPenultimateEvent("utter_cross_examine"),
                EqualPenultimateEvent("utter_cross_examine_jump")
            ),
            NotCriterion(EqualIntent("change_current_flow"))
        ), jump=False)
    return chain
