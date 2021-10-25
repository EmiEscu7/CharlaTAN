import sys
sys.path.pop(0)

import os
import importlib
import inspect
from typing import Text, Type, Optional, Any, List
from pathlib import Path
from rasa.shared.utils.io import read_yaml_file
from rasa.core import registry
from rasa.core.policies.ensemble import InvalidPolicyConfig
#D:/Universidad/CharlaTAN/RASAComponents/Policies.yml
POLICIES_OF_RASA_COMPONENTS  = "RASAComponents/Policies.yml"
p = Path(Path(__file__).parent.parent / POLICIES_OF_RASA_COMPONENTS)

print(p)
if (__name__ == "__main__"):
    a = read_yaml_file(p)
    policies = a['policies']
    print(f"Politicas definidas: {policies}")
    parsed_policies = {}
    for policy in policies:
        print(policy)
        policy_name = policy.pop('name')
        print("Policy name: " + policy_name)
        print(policy_name.split(".")[0])
        try:
            constr_func = registry.policy_from_module_path(policy_name)
            try:
                policy_object = constr_func(**policy)
            except TypeError as e:
                raise Exception(f"Could not initialize {policy_name}. {e}")
            parsed_policies[policy_name.split(".")[0]]=policy_object
        except (ImportError, AttributeError):
                    raise InvalidPolicyConfig(
                        f"Module for policy '{policy_name}' could not "
                        f"be loaded. Please make sure the "
                        f"name is a valid policy."
                    )
    print(f"Politicas parseadas: {parsed_policies}")
    parsed_policies["Customizer"].predict_action_probabilities()
