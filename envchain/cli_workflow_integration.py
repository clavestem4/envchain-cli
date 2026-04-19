"""Integration helpers: run/merge all chains in a workflow."""
from typing import Dict, List
from envchain.workflow import get_workflow, WorkflowError
from envchain.chain import get_chain


def load_workflow_vars(workflow_name: str, strategy: str = "last-wins") -> Dict[str, str]:
    """Load and merge env vars from all chains in a workflow.

    strategy:
      - 'last-wins': later chains overwrite earlier ones
      - 'first-wins': earlier chains take precedence
    """
    chain_names = get_workflow(workflow_name)
    merged: Dict[str, str] = {}
    for name in chain_names:
        chain = get_chain(name)
        for k, v in chain.items():
            if strategy == "first-wins" and k in merged:
                continue
            merged[k] = v
    return merged


def workflow_var_sources(workflow_name: str) -> List[Dict]:
    """Return each variable with its source chain for a workflow."""
    chain_names = get_workflow(workflow_name)
    seen = {}
    for name in chain_names:
        chain = get_chain(name)
        for k, v in chain.items():
            seen[k] = {"chain": name, "key": k, "value": v}
    return list(seen.values())


def workflow_conflicts(workflow_name: str) -> Dict[str, List[str]]:
    """Return keys that appear in more than one chain in the workflow."""
    chain_names = get_workflow(workflow_name)
    key_sources: Dict[str, List[str]] = {}
    for name in chain_names:
        chain = get_chain(name)
        for k in chain:
            key_sources.setdefault(k, []).append(name)
    return {k: v for k, v in key_sources.items() if len(v) > 1}
