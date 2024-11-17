def get_agent(agent_info):
    # Extract values using .get() to avoid KeyError
    agent_info = agent_info.get("propertyInfo", {}).get("agentInfo", {})
    
    agent_name = agent_info.get("displayName")
    business_name = agent_info.get("businessName")
    phone_no = agent_info.get("phoneNumber")
    verified = agent_info.get("verified", False)
    
    # Determine the agent string based on available information
    if agent_name and business_name:
        agent = f"{agent_name} - {business_name}"
    elif agent_name:
        agent = agent_name
    elif business_name:
        agent = business_name
    else:
        agent = "Name undisclosed"
    
    # Add phone number if available
    if phone_no:
        agent = f"{agent}, {phone_no}"
    
    # Add verified status if applicable
    if verified:
        agent = f"{agent} (Verified Source)"
    
    return agent
