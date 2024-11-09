from contextlib import suppress

def get_agent(agent_info):
    agent_name, business_name = None, None         
    with suppress(KeyError):
        agent_name = agent_info["propertyInfo"]["agentInfo"]["displayName"]
        business_name = agent_info["propertyInfo"]["agentInfo"]["businessName"]
        phone_no = agent_info["propertyInfo"]["agentInfo"]["phoneNumber"]
        
    zillow_days, contacts, subsidized = "", "", ""

    if not agent_name and not business_name:
        agent = "Name undisclosed"
    elif not agent_name:
        agent = business_name
    elif not business_name:
        agent = agent_name
    else:
        agent = f"{agent_name} - {business_name}"
        
    if phone_no:
        agent = f"{agent}, {phone_no}"
    
    verified = agent_info["propertyInfo"]["verified"]
    if verified:
        agent = f"{agent} (Verified Source)"
    
    return agent