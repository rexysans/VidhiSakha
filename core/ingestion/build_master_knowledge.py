import pandas as pd
import json
import re


def parse_range(range_str):
    if pd.isna(range_str) or range_str == "-":
        return None, None
    parts = re.findall(r"[0-9]+[A-Z]*", str(range_str))
    if len(parts) == 1:
        return parts[0], parts[0]
    elif len(parts) >= 2:
        return parts[0], parts[-1]
    return None, None


def ingest_data():
    # 1. Load Data
    index_df = pd.read_csv("dataset/Index.csv", encoding="latin1").dropna(
        subset=["Parts of the Indian Constitution"]
    )
    const_df = pd.read_csv("dataset/Constitution Of India.csv")

    # 2. Process Parts
    parts_list = []
    for i, row in index_df.iterrows():
        start, end = parse_range(row["Articles in Indian Constitution"])
        parts_list.append(
            {
                "part_uid": i,
                "part_id": row["Parts of the Indian Constitution"],  # display id
                "part_name": row["Subject Mentioned in the Part"],
                "article_range": {"start": start, "end": end},
            }
        )

    # 3. Process Articles & Map to Parts
    articles_list = []
    for i, row in const_df.iterrows():
        text = str(row["Articles"])
        # Regex to find the Article ID at the start of the text (e.g., "1.", "51A.", "243ZG.")
        match = re.match(r"^([0-9]+[A-Z]*)\.", text)
        if match:
            article_id = match.group(1)
            # Find which part this article belongs to based on the range
            # (Note: Simplification for v1; real logic uses list index matching)
            parent_part_uid = None
            for p in parts_list:

                # Basic check: if ID is between start and end digits
                if p["article_range"]["start"] and article_id:
                    # Logic to check if article_id fits in part p
                    # This is where your 'Reasoning Engine' eventually takes over
                    try:
                        current_id = int(re.sub("[^0-9]", "", article_id))
                        start_id = int(
                            re.sub("[^0-9]", "", p["article_range"]["start"])
                        )
                        end_id = int(re.sub("[^0-9]", "", p["article_range"]["end"]))
                        if start_id <= current_id <= end_id:
                            parent_part_uid = p["part_uid"]
                            break

                    except:
                        continue

            articles_list.append(
                {
                    "article_uid": i,
                    "article_id": article_id,  # legal id
                    "full_text": text.strip(),
                    "title": text.split("\n")[0],
                    "part_uid": parent_part_uid,  # system relation
                }
            )

    # 4. Save to Structured JSON (The "Knowledge Layer" Source)
    output = {"parts": parts_list, "articles": articles_list}
    with open("dataset/vidhisakha_kb_v1.json", "w") as f:
        json.dump(output, f, indent=4)

    print("Ingestion Complete: vidhisakha_kb_v1.json created.")

    unmapped = sum(1 for a in articles_list if a["part_uid"] is None)
    print("Unmapped articles:", unmapped)


if __name__ == "__main__":
    ingest_data()
