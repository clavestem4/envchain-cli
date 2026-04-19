"""Workflow: ordered sequence of chains to load in order."""
from typing import List, Dict
from envchain.chain import get_chain, get_chain_names, add_chain

WORKFLOW_KEY = "__workflow__"


class WorkflowError(Exception):
    pass


def _get_workflows(get_fn=get_chain, names_fn=get_chain_names) -> Dict:
    names = names_fn()
    if WORKFLOW_KEY not in names:
        return {}
    chain = get_fn(WORKFLOW_KEY)
    import json
    result = {}
    for k, v in chain.items():
        try:
            result[k] = json.loads(v)
        except Exception:
            result[k] = []
    return result


def set_workflow(name: str, chain_names: List[str], get_fn=get_chain,
                names_fn=get_chain_names, add_fn=add_chain):
    import json
    all_names = names_fn()
    for c in chain_names:
        if c not in all_names:
            raise WorkflowError(f"Chain '{c}' does not exist.")
    workflows = _get_workflows(get_fn, names_fn)
    workflows[name] = chain_names
    _save_workflows(workflows, add_fn)


def get_workflow(name: str, get_fn=get_chain, names_fn=get_chain_names) -> List[str]:
    workflows = _get_workflows(get_fn, names_fn)
    if name not in workflows:
        raise WorkflowError(f"Workflow '{name}' not found.")
    return workflows[name]


def remove_workflow(name: str, get_fn=get_chain, names_fn=get_chain_names, add_fn=add_chain):
    workflows = _get_workflows(get_fn, names_fn)
    if name not in workflows:
        raise WorkflowError(f"Workflow '{name}' not found.")
    del workflows[name]
    _save_workflows(workflows, add_fn)


def list_workflows(get_fn=get_chain, names_fn=get_chain_names) -> Dict:
    return _get_workflows(get_fn, names_fn)


def _save_workflows(workflows: Dict, add_fn=add_chain):
    import json
    serialized = {k: json.dumps(v) for k, v in workflows.items()}
    add_fn(WORKFLOW_KEY, serialized, overwrite=True)
