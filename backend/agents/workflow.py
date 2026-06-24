from langgraph.graph import StateGraph, START, END
from .state import PRReviewState
from .navigator import navigator_node
from .critic import critic_node
from .senior import senior_node
from .judge import judge_node

def create_workflow():
    """
    Compiles the multi-agent LangGraph state machine.
    Execution order: Navigator -> Critic -> Senior -> Judge
    """
    workflow = StateGraph(PRReviewState)
    
    workflow.add_node("navigator", navigator_node)
    workflow.add_node("critic", critic_node)
    workflow.add_node("senior", senior_node)
    workflow.add_node("judge", judge_node)
    
    workflow.add_edge(START, "navigator")
    # To keep it extremely fast, the navigator can run in parallel with the critic in a more complex setup.
    # But for now, we'll keep it strictly sequential as per the Build Plan.
    workflow.add_edge("navigator", "critic")
    workflow.add_edge("critic", "senior")
    workflow.add_edge("senior", "judge")
    workflow.add_edge("judge", END)
    
    return workflow.compile()
