# Data Model – VidhiSakhā (v1)

## Entity: Part
Represents a structural division of the Indian Constitution.

Fields:
- part_id (string)  
  Example: "Part III"

- part_name (string)  
  Example: "Fundamental Rights"

- subject (string)  
  Example: "Fundamental Rights"

- article_start (int)  
  Example: 12

- article_end (int)  
  Example: 35

Source: Index.csv

---

## Entity: Article
Represents a single Article of the Indian Constitution.

Fields:
- article_id (string)  
  Example: 21

- article_title (string, optional)

- article_text (string)

- part_id (string, foreign key → Part.part_id)

Source: Constitution Of India.csv

---

## Relationship

Part HAS_MANY Articles  
Article BELONGS_TO Part
