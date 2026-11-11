# Travel Planner AI (BYOP using ShopAssist-style design)

## 1) Project Goal
Build an AI-driven chatbot that helps travelers plan trips by:
- collecting user requirements through conversation,
- recommending top hotels using a scoring model,
- generating a day-wise itinerary for the selected destination.

This follows the ShopAssist pattern: conversational information gathering + deterministic recommendation logic for reliability.

## 2) AI Approach / Model
This project uses a **hybrid AI approach**:
- **NLP-style preference extraction** from free-text input (destination, budget tier, trip length, amenities, travel style).
- **Rule-based scoring engine** to rank hotels transparently.

Why this choice:
- deterministic behavior for predictable outputs,
- easy debugging,
- good baseline before integrating LLM APIs.

## 3) Data Sources
For this demonstration, curated sample datasets are included:
- `data/hotels.csv` (hotel metadata: destination, price, style, rating, amenities, description)
- `data/itineraries.csv` (day-wise itinerary templates by destination)

In production, these can be replaced with public datasets (for example from Kaggle), OTA APIs, and review platforms.

## 4) Key Design Decisions
1. **Progressive requirement collection**  
   Chatbot asks follow-ups until required fields are captured (`destination`, `budget_tier`, `trip_days`).

2. **Explicit scoring features**  
   Final ranking score combines:
   - destination match,
   - budget-tier match,
   - style match,
   - amenity overlap,
   - rating bonus.

3. **Safe defaults without hidden behavior**  
   If itinerary templates are unavailable for a destination, fallback itinerary lines are explicitly generated.

## 5) Challenges Encountered
- Free-text input can be ambiguous (e.g., “not expensive but premium feel”).
- Amenities and style terms vary by user vocabulary.
- Balancing explainability vs. flexibility of natural language understanding.

## 6) How to Run
From this folder:

```bash
python app.py
```

Then chat with the assistant. Type `exit` to stop.

## 7) How to Test
```bash
python -m unittest -v
```

## 8) Future Improvements
- integrate LLM API for stronger intent extraction,
- add geospatial filtering and season-aware itinerary logic,
- include user feedback loop for personalized ranking.
