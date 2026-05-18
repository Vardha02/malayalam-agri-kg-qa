from neo4j import GraphDatabase
import os
import streamlit as st


def get_secret(name):
    """Read from Streamlit secrets first, then environment variables."""
    try:
        if name in st.secrets:
            return st.secrets[name]
    except Exception:
        pass
    return os.getenv(name)


URI = get_secret("NEO4J_URI")
USER = get_secret("NEO4J_USERNAME")
PASSWORD = get_secret("NEO4J_PASSWORD")

if not URI or not USER or not PASSWORD:
    raise ValueError(
        "Neo4j credentials missing. Add NEO4J_URI, NEO4J_USERNAME, and NEO4J_PASSWORD in Streamlit Secrets."
    )

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


ALIASES = {
    # Malayalam crops and case forms
    "കാന്താരി": "കാന്താരി",
    "കാന്താരിയെ": "കാന്താരി",
    "കാന്താരിക്ക്": "കാന്താരി",
    "കാന്താരിയുടെ": "കാന്താരി",

    "മുളക്": "മുളക്",
    "മുളകിനെ": "മുളക്",
    "മുളകിന്": "മുളക്",
    "മുളകിന്റെ": "മുളക്",

    "പയർ": "പയർ",
    "പയറിനെ": "പയർ",
    "പയറിന്": "പയർ",
    "പയറിന്റെ": "പയർ",

    "ഇഞ്ചി": "ഇഞ്ചി",
    "ഇഞ്ചിയെ": "ഇഞ്ചി",
    "ഇഞ്ചിക്ക്": "ഇഞ്ചി",
    "ഇഞ്ചിയുടെ": "ഇഞ്ചി",

    "വാഴ": "വാഴ",
    "വാഴയെ": "വാഴ",
    "വാഴയ്ക്ക്": "വാഴ",
    "വാഴയുടെ": "വാഴ",

    "കൊക്കോ": "കൊക്കോ",
    "കൊക്കോയെ": "കൊക്കോ",
    "കൊക്കോയ്ക്ക്": "കൊക്കോ",
    "കൊക്കോയുടെ": "കൊക്കോ",

    "തെങ്ങ്": "തെങ്ങ്",
    "തെങ്ങിനെ": "തെങ്ങ്",
    "തെങ്ങിന്": "തെങ്ങ്",
    "തെങ്ങിന്റെ": "തെങ്ങ്",

    "ചക്ക": "ചക്ക",
    "ചക്കയ്ക്ക്": "ചക്ക",
    "കപ്പ": "കപ്പ",
    "ചീര": "ചീര",
    "വഴുതന": "വഴുതന",
    "പപ്പായ": "പപ്പായ",
    "അമര": "അമര",
    "ചേന": "ചേന",
    "ചോളം": "ചോളം",
    "അരി": "അരി",

    # English aliases
    "chilli": "മുളക്",
    "chili": "മുളക്",
    "ginger": "ഇഞ്ചി",
    "banana": "വാഴ",
    "cocoa": "കൊക്കോ",
    "coconut": "തെങ്ങ്",
    "beans": "പയർ",
    "bean": "പയർ",
}


def normalize_text(text):
    return str(text).strip().lower()


def get_all_crops():
    query = """
    MATCH (n:Entity)
    WHERE n.label = 'CROP'
    RETURN DISTINCT n.name AS name
    """
    with driver.session() as session:
        rows = session.run(query).data()
    return [row["name"] for row in rows if row.get("name")]


def get_crop(question):
    q = normalize_text(question)

    for alias, crop in ALIASES.items():
        if normalize_text(alias) in q:
            return crop

    # fallback: search crop names directly from graph
    for crop in get_all_crops():
        if crop in question:
            return crop

    return None


def get_question_type(question):
    q = normalize_text(question)

    if "കീട" in q or "pest" in q or "pests" in q:
        return "PEST", "കീടങ്ങൾ"

    if "രോഗ" in q or "disease" in q or "diseases" in q:
        return "DISEASE", "രോഗങ്ങൾ"

    if "വളം" in q or "വളങ്ങൾ" in q or "fertilizer" in q or "fertilizers" in q:
        return "FERTILIZER", "വളങ്ങൾ"

    if "പരിഹാരം" in q or "ചികിത്സ" in q or "treatment" in q:
        return "TREATMENT", "ചികിത്സകൾ"

    return None, "ബന്ധപ്പെട്ട വിവരങ്ങൾ"


def ask_graph(question):
    crop = get_crop(question)

    if not crop:
        return "ചോദ്യത്തിലുള്ള വിളയുടെ പേര് ഗ്രാഫിൽ കണ്ടെത്താനായില്ല."

    label, heading = get_question_type(question)

    if label:
        query = """
        MATCH (a:Entity)-[:RELATION]->(b:Entity)
        WHERE b.name = $crop AND a.label = $label
        RETURN DISTINCT a.name AS name
        ORDER BY name
        """
        params = {"crop": crop, "label": label}
    else:
        query = """
        MATCH (a:Entity)-[:RELATION]->(b:Entity)
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
        if "label" in row and row.get("label"):
            answer += f"- {row['name']} ({row['label']})\n"
        else:
            answer += f"- {row['name']}\n"

    return answer.strip()
