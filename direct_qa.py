from neo4j import GraphDatabase
import os
import streamlit as st

URI = st.secrets.get("NEO4J_URI", os.getenv("NEO4J_URI"))
USER = st.secrets.get("NEO4J_USERNAME", os.getenv("NEO4J_USERNAME"))
PASSWORD = st.secrets.get("NEO4J_PASSWORD", os.getenv("NEO4J_PASSWORD"))

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

ALIASES = {
    "chilli": "മുളക്", "chili": "മുളക്",
    "ginger": "ഇഞ്ചി", "banana": "വാഴ",
    "cocoa": "കൊക്കോ", "coconut": "തെങ്ങ്",
    "കാന്താരി": "കാന്താരി", "കാന്താരിയെ": "കാന്താരി", "കാന്താരിക്ക്": "കാന്താരി",
    "മുളക്": "മുളക്", "മുളകിനെ": "മുളക്", "മുളകിന്റെ": "മുളക്",
    "പയർ": "പയർ", "പയറിനെ": "പയർ", "പയറിന്": "പയർ",
    "ഇഞ്ചി": "ഇഞ്ചി", "ഇഞ്ചിക്ക്": "ഇഞ്ചി", "ഇഞ്ചിയുടെ": "ഇഞ്ചി",
    "വാഴ": "വാഴ", "വാഴയുടെ": "വാഴ",
    "കൊക്കോ": "കൊക്കോ", "കൊക്കോയുടെ": "കൊക്കോ",
}

def get_crop_from_question(question):
    q = question.strip().lower()
    for alias, crop in ALIASES.items():
        if alias.lower() in q:
            return crop
    return None

def get_question_type(question):
    q = question.lower()
    if "കീട" in q or "pest" in q:
        return "PEST", "കീടങ്ങൾ"
    if "രോഗ" in q or "disease" in q:
        return "DISEASE", "രോഗങ്ങൾ"
    if "വളം" in q or "വളങ്ങൾ" in q or "fertilizer" in q:
        return "FERTILIZER", "വളങ്ങൾ"
    if "പരിഹാരം" in q or "ചികിത്സ" in q or "treatment" in q:
        return "TREATMENT", "ചികിത്സകൾ"
    return None, "ബന്ധപ്പെട്ട വിവരങ്ങൾ"

def ask_graph(question):
    crop = get_crop_from_question(question)

    if not crop:
        return "ചോദ്യത്തിലുള്ള വിളയുടെ പേര് ഗ്രാഫിൽ കണ്ടെത്താനായില്ല."

    label, heading = get_question_type(question)

    if label:
        query = """
        MATCH (a:Entity)-[r:RELATION]->(b:Entity)
        WHERE b.name = $crop AND a.label = $label
        RETURN DISTINCT a.name AS name
        ORDER BY name
        """
        params = {"crop": crop, "label": label}
    else:
        query = """
        MATCH (a:Entity)-[r:RELATION]->(b:Entity)
        WHERE b.name = $crop
        RETURN DISTINCT a.name AS name, a.label AS label
        ORDER BY label, name
        """
        params = {"crop": crop}

    with driver.session() as session:
        rows = session.run(query, **params).data()

    if not rows:
        return f"{crop} എന്ന വിളയ്ക്ക് {heading} സംബന്ധിച്ച വിവരം ഗ്രാഫിൽ ലഭ്യമല്ല."

    answer = f"{crop} - {heading}:\n"
    for row in rows:
        if "label" in row:
            answer += f"- {row['name']} ({row['label']})\n"
        else:
            answer += f"- {row['name']}\n"
    return answer.strip()
