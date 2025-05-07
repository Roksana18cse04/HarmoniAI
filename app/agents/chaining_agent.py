from app.agents.classifier_agent import classify_prompt_agent
from app.agents.tools_selector_agent import fetch_models_by_category_id

def run_multi_agent_chain(user_prompt):
    
    result = classify_prompt_agent(user_prompt)
    cat_id = result.get("category_id")

    tools = fetch_models_by_category_id(cat_id)
    return {
        "intent": result.get("intent"),
        "category_id": cat_id,
        "suggested_models": tools
    }
