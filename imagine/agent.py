from transformers import pipeline

nlp = pipeline("zero-shot-classification", model="facebook/bart-large-mnli")

def parse_command(user_input):
    labels = ["find my photo", "find similar images", "find photos of me", "find dancing people", "find smiling people"]
    result = nlp(user_input, candidate_labels=labels)
    action = result['labels'][0]

    entities = []
    if "dancing" in action:
        entities.append("dancing")
    elif "smiling" in action:
        entities.append("smiling")
    elif "find my photo" in action or "similar" in action:
        entities.append("find_my_photo")

    return {
        "actions": ["find"],
        "entities": entities
    }
