
from typing import TypedDict,List, Dict, Any, Optional
from datetime import datetime

class AgentState(TypedDict, total = False):
    
    task : str
    plan : List[str]
    current_step : int 
    max_steps : int
    
    rag_results: List[Dict[str, Any]]
    code_output : str
    file_path : str
    final_answer : str
    
    memory : List[Dict[str,Any]]
    errors: List[str]
    start_time : str
    
    iteration: int                     
    tool_calls: List[str]