from neo4j import GraphDatabase
from dotenv import load_dotenv
import os

load_dotenv()

URI = os.getenv("NEO4J_URI")
USER = os.getenv("NEO4J_USERNAME")
PASSWORD = os.getenv("NEO4J_PASSWORD")

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

ALIASES = {
    "coconut": "തെങ്ങ്",
    "rice": "അരി",
    "paddy": "അരി",
    "chilli": "മുളക്",
    "chili": "മുളക്",
    "pepper": "കുരുമുളക്",
    "black pepper": "കുരുമുളക്",
    "cocoa": "കൊക്കോ",
    "banana": "വാഴ",
    "ginger": "ഇഞ്ചി",
    "turmeric": "മഞ്ഞൾ",
    "papaya": "പപ്പായ",
    "mango": "മാവ്",

    "കാന്താരിയെ": "കാന്താരി",
    "കാന്താരിക്ക്": "കാന്താരി",
    "കാന്താരിയുടെ": "കാന്താരി",

    "കൊക്കോയെ": "കൊക്കോ",
    "കൊക്കോയ്ക്ക്": "കൊക്കോ",
    "കൊക്കോയുടെ": "കൊക്കോ",

    "മുളകിനെ": "മുളക്",
    "മുളകിന്": "മുളക്",
    "മുളകിന്റെ": "മുളക്",

    "പയറിനെ": "പയർ",
    "പയറിന്": "പയർ",
    "പയറിന്റെ": "പയർ",

    "വാഴയെ": "വാഴ",
    "വാഴയ്ക്ക്": "വാഴ",
    "വാഴയുടെ": "വാഴ",

    "ഇഞ്ചിയെ": "ഇഞ്ചി",
    "ഇഞ്ചിക്ക്": "ഇഞ്ചി",
    "ഇഞ്ചിയുടെ": "ഇഞ്ചി",

    "നെല്ല്": "അരി",
    "നെല്ലിനെ": "അരി",
    "നെല്ലിന്": "അരി",
}


def get_all_crops():
    query = """
    MATCH (n:Entity)
    WHERE n.label = 'CROP'
    RETURN DISTINCT n.name AS name
    """

    with driver.session() as session:
        rows = session.run(query).data()

    return [row["name"] for row in rows]


def get_crop_from_question(question):
    q = question.strip().lower()

    for alias, crop in ALIASES.items():
        if alias.lower() in q:
            return crop

    crops = get_all_crops()

    for crop in crops:
        if crop in question:
            return crop

    return None


def get_question_type(question):
    q = question.lower()

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
    crop = get_crop_from_question(question)

    if not crop:
        return "ചോദ്യത്തിലുള്ള വിളയുടെ പേര് ഗ്രാഫിൽ കണ്ടെത്താനായില്ല."

    label, heading = get_question_type(question)

    if label:
        query = """
        MATCH (a:Entity)-[r:RELATION]->(b:Entity)
        WHERE b.name = $crop
        AND a.label = $label
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


if __name__ == "__main__":
    while True:
        question = input("Ask a question (type exit): ")

        if question.lower() == "exit":
            break

        print("\nAnswer:")
        print(ask_graph(question))
        print("-" * 50)