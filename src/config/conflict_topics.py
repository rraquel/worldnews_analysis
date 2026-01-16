"""
Predefined global conflict topics for analysis.
These topics represent major areas of geopolitical concern that could affect world order.
"""

from typing import List, Dict

# Global conflict topics with search terms and descriptions
GLOBAL_CONFLICT_TOPICS: List[Dict[str, any]] = [
    {
        "id": "china_taiwan",
        "name": "China-Taiwan Tensions",
        "description": "Cross-strait relations, military exercises, and territorial disputes",
        "keywords": ["Taiwan", "China", "strait", "TSMC", "semiconductors", "reunification", "independence"],
        "risk_level": "high",
        "category": "territorial_dispute"
    },
    {
        "id": "ukraine_russia",
        "name": "Russia-Ukraine War",
        "description": "Ongoing conflict, NATO involvement, and European security",
        "keywords": ["Ukraine", "Russia", "NATO", "Crimea", "Donbas", "Zelensky", "Putin"],
        "risk_level": "critical",
        "category": "active_conflict"
    },
    {
        "id": "middle_east_israel_palestine",
        "name": "Israel-Palestine Conflict",
        "description": "Gaza, West Bank, and regional stability",
        "keywords": ["Israel", "Palestine", "Gaza", "Hamas", "West Bank", "Netanyahu", "settlements"],
        "risk_level": "critical",
        "category": "active_conflict"
    },
    {
        "id": "iran_nuclear",
        "name": "Iran Nuclear Program",
        "description": "Nuclear development, sanctions, and regional power dynamics",
        "keywords": ["Iran", "nuclear", "uranium", "JCPOA", "sanctions", "enrichment", "IAEA"],
        "risk_level": "high",
        "category": "proliferation"
    },
    {
        "id": "north_korea",
        "name": "North Korea Nuclear Threat",
        "description": "Missile tests, nuclear weapons, and Korean Peninsula stability",
        "keywords": ["North Korea", "DPRK", "Kim Jong", "missile", "nuclear test", "sanctions"],
        "risk_level": "high",
        "category": "proliferation"
    },
    {
        "id": "south_china_sea",
        "name": "South China Sea Disputes",
        "description": "Territorial claims, maritime routes, and regional tensions",
        "keywords": ["South China Sea", "Spratly", "Paracel", "Philippines", "Vietnam", "maritime", "UNCLOS"],
        "risk_level": "medium",
        "category": "territorial_dispute"
    },
    {
        "id": "india_pakistan_kashmir",
        "name": "India-Pakistan Kashmir Dispute",
        "description": "Kashmir conflict, border tensions, and nuclear-armed rivals",
        "keywords": ["Kashmir", "India", "Pakistan", "Line of Control", "Modi", "Imran Khan"],
        "risk_level": "high",
        "category": "territorial_dispute"
    },
    {
        "id": "yemen_civil_war",
        "name": "Yemen Civil War",
        "description": "Saudi-Iran proxy war, humanitarian crisis, and regional instability",
        "keywords": ["Yemen", "Houthi", "Saudi Arabia", "Iran", "humanitarian", "Aden"],
        "risk_level": "high",
        "category": "active_conflict"
    },
    {
        "id": "syria_conflict",
        "name": "Syrian Civil War",
        "description": "Multi-party conflict, refugee crisis, and regional proxy battles",
        "keywords": ["Syria", "Assad", "rebels", "ISIS", "Kurds", "Turkey", "refugee"],
        "risk_level": "medium",
        "category": "active_conflict"
    },
    {
        "id": "ethiopia_tigray",
        "name": "Ethiopia-Tigray Conflict",
        "description": "Civil war, humanitarian crisis, and Horn of Africa stability",
        "keywords": ["Ethiopia", "Tigray", "TPLF", "Eritrea", "humanitarian", "Addis Ababa"],
        "risk_level": "medium",
        "category": "active_conflict"
    },
    {
        "id": "sahel_terrorism",
        "name": "Sahel Region Terrorism",
        "description": "Islamic extremism, coups, and regional instability",
        "keywords": ["Sahel", "Mali", "Burkina Faso", "Niger", "jihadist", "terrorism", "France"],
        "risk_level": "medium",
        "category": "terrorism"
    },
    {
        "id": "arctic_competition",
        "name": "Arctic Resource Competition",
        "description": "Climate change, resource extraction, and territorial claims",
        "keywords": ["Arctic", "Russia", "Canada", "Greenland", "resources", "Northwest Passage"],
        "risk_level": "medium",
        "category": "territorial_dispute"
    },
    {
        "id": "us_china_tech_war",
        "name": "US-China Technology Competition",
        "description": "Semiconductors, AI, 5G, and technological decoupling",
        "keywords": ["US China", "technology", "semiconductors", "Huawei", "5G", "AI", "export controls"],
        "risk_level": "high",
        "category": "economic_conflict"
    },
    {
        "id": "venezuela_crisis",
        "name": "Venezuela Political Crisis",
        "description": "Economic collapse, migration, and regional stability",
        "keywords": ["Venezuela", "Maduro", "opposition", "sanctions", "migration", "oil"],
        "risk_level": "medium",
        "category": "political_instability"
    },
    {
        "id": "myanmar_coup",
        "name": "Myanmar Military Coup",
        "description": "Democratic backsliding, civil resistance, and ethnic conflicts",
        "keywords": ["Myanmar", "Burma", "coup", "military junta", "Aung San", "Rohingya"],
        "risk_level": "medium",
        "category": "political_instability"
    },
    {
        "id": "balkans_tensions",
        "name": "Western Balkans Tensions",
        "description": "Serbia-Kosovo relations, ethnic tensions, and EU integration",
        "keywords": ["Kosovo", "Serbia", "Bosnia", "Balkans", "ethnic", "EU accession"],
        "risk_level": "low",
        "category": "territorial_dispute"
    },
    {
        "id": "cyber_warfare",
        "name": "Cyber Warfare and Espionage",
        "description": "State-sponsored hacking, critical infrastructure, and information warfare",
        "keywords": ["cyber attack", "hacking", "ransomware", "espionage", "critical infrastructure"],
        "risk_level": "high",
        "category": "hybrid_warfare"
    },
    {
        "id": "space_militarization",
        "name": "Space Militarization",
        "description": "Anti-satellite weapons, space force, and orbital competition",
        "keywords": ["space", "satellite", "anti-satellite", "space force", "orbital", "Starlink"],
        "risk_level": "medium",
        "category": "emerging_domain"
    },
    {
        "id": "climate_security",
        "name": "Climate Change and Security",
        "description": "Resource scarcity, migration, and climate-driven conflicts",
        "keywords": ["climate change", "water scarcity", "climate migration", "food security", "drought"],
        "risk_level": "medium",
        "category": "emerging_threat"
    },
    {
        "id": "ai_autonomous_weapons",
        "name": "AI and Autonomous Weapons",
        "description": "Lethal autonomous weapons, AI regulation, and ethical concerns",
        "keywords": ["autonomous weapons", "AI warfare", "killer robots", "military AI", "drone swarms"],
        "risk_level": "medium",
        "category": "emerging_domain"
    }
]

# Analysis depth configurations
ANALYSIS_DEPTH_CONFIG = {
    "quick": {
        "name": "Quick Overview",
        "description": "Basic clustering and sentiment analysis",
        "days_back": 3,
        "max_articles": 50,
        "similarity_threshold": 0.7,
        "min_cluster_size": 2,
        "include_topic_modeling": False,
        "include_predictions": False,
        "include_cross_analysis": False
    },
    "standard": {
        "name": "Standard Analysis",
        "description": "Full rhetoric analysis and predictions",
        "days_back": 7,
        "max_articles": 150,
        "similarity_threshold": 0.6,
        "min_cluster_size": 2,
        "include_topic_modeling": True,
        "include_predictions": True,
        "include_cross_analysis": True
    },
    "deep": {
        "name": "Deep Analysis",
        "description": "Comprehensive analysis with historical comparison",
        "days_back": 14,
        "max_articles": 300,
        "similarity_threshold": 0.5,
        "min_cluster_size": 2,
        "include_topic_modeling": True,
        "include_predictions": True,
        "include_cross_analysis": True,
        "include_historical_comparison": True
    }
}

# Risk level colors for visualization
RISK_COLORS = {
    "critical": "#d32f2f",  # Red
    "high": "#f57c00",      # Orange
    "medium": "#fbc02d",    # Yellow
    "low": "#388e3c"        # Green
}

# Category icons/descriptions
CONFLICT_CATEGORIES = {
    "active_conflict": {"icon": "⚔️", "description": "Ongoing armed conflict"},
    "territorial_dispute": {"icon": "🗺️", "description": "Border or territorial disagreement"},
    "proliferation": {"icon": "☢️", "description": "Nuclear/WMD concerns"},
    "terrorism": {"icon": "💣", "description": "Terrorist activity"},
    "economic_conflict": {"icon": "💰", "description": "Economic/trade tensions"},
    "political_instability": {"icon": "🏛️", "description": "Political crisis"},
    "hybrid_warfare": {"icon": "💻", "description": "Cyber and information warfare"},
    "emerging_domain": {"icon": "🚀", "description": "New conflict domains"},
    "emerging_threat": {"icon": "🌍", "description": "Long-term security threats"}
}

def get_topics_by_risk_level(risk_level: str) -> List[Dict]:
    """Get all topics matching a specific risk level."""
    return [topic for topic in GLOBAL_CONFLICT_TOPICS if topic["risk_level"] == risk_level]

def get_topics_by_category(category: str) -> List[Dict]:
    """Get all topics matching a specific category."""
    return [topic for topic in GLOBAL_CONFLICT_TOPICS if topic["category"] == category]

def get_topic_by_id(topic_id: str) -> Dict:
    """Get a specific topic by its ID."""
    for topic in GLOBAL_CONFLICT_TOPICS:
        if topic["id"] == topic_id:
            return topic
    return None

def get_all_keywords() -> List[str]:
    """Get all unique keywords across all topics."""
    keywords = set()
    for topic in GLOBAL_CONFLICT_TOPICS:
        keywords.update(topic["keywords"])
    return sorted(list(keywords))
