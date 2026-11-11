from __future__ import annotations

import csv
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Tuple


BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"


@dataclass
class UserPreferences:
    destination: str | None = None
    budget_tier: str | None = None  # budget, mid, luxury
    trip_days: int | None = None
    style: str | None = None  # adventure, cultural, relaxation
    amenities: List[str] = field(default_factory=list)


class TravelPlannerAI:
    def __init__(self, hotels_path: Path, itinerary_path: Path) -> None:
        self.hotels = self._load_hotels(hotels_path)
        self.itineraries = self._load_itineraries(itinerary_path)
        self.supported_destinations = sorted({hotel["destination"] for hotel in self.hotels})
        self.allowed_amenities = {
            "wifi",
            "breakfast",
            "pool",
            "gym",
            "spa",
            "airport_shuttle",
            "family_friendly",
            "work_friendly",
        }

    @staticmethod
    def _load_hotels(path: Path) -> List[Dict[str, str]]:
        with path.open(newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    @staticmethod
    def _load_itineraries(path: Path) -> List[Dict[str, str]]:
        with path.open(newline="", encoding="utf-8") as file:
            return list(csv.DictReader(file))

    def parse_preferences(self, message: str, prefs: UserPreferences) -> UserPreferences:
        text = message.lower()

        for destination in self.supported_destinations:
            if destination.lower() in text:
                prefs.destination = destination
                break

        budget_keywords = {
            "budget": ["cheap", "budget", "low cost", "affordable"],
            "mid": ["mid", "moderate", "value"],
            "luxury": ["luxury", "premium", "high end", "5 star"],
        }
        for budget_tier, keywords in budget_keywords.items():
            if any(keyword in text for keyword in keywords):
                prefs.budget_tier = budget_tier
                break

        for style in ["adventure", "cultural", "relaxation"]:
            if style in text:
                prefs.style = style
                break

        for token in text.replace(",", " ").split():
            cleaned = token.strip(" .!?")
            if cleaned in self.allowed_amenities and cleaned not in prefs.amenities:
                prefs.amenities.append(cleaned)

        for token in text.replace("-", " ").split():
            if token.isdigit():
                days = int(token)
                if 1 <= days <= 14:
                    prefs.trip_days = days
                    break

        return prefs

    @staticmethod
    def _hotel_budget_tier(price_per_night: int) -> str:
        if price_per_night < 120:
            return "budget"
        if price_per_night <= 220:
            return "mid"
        return "luxury"

    def _score_hotel(self, hotel: Dict[str, str], prefs: UserPreferences) -> float:
        score = 0.0
        if prefs.destination and hotel["destination"] == prefs.destination:
            score += 4

        price = int(hotel["price_per_night"])
        hotel_tier = self._hotel_budget_tier(price)
        if prefs.budget_tier and prefs.budget_tier == hotel_tier:
            score += 3
        elif prefs.budget_tier:
            score += 0.5

        if prefs.style and prefs.style == hotel["style"]:
            score += 2

        hotel_amenities = {item.strip() for item in hotel["amenities"].split("|")}
        score += len(set(prefs.amenities).intersection(hotel_amenities)) * 1.5

        score += float(hotel["rating"]) / 2
        return score

    def recommend_hotels(self, prefs: UserPreferences, top_n: int = 3) -> List[Tuple[Dict[str, str], float]]:
        scored = [(hotel, self._score_hotel(hotel, prefs)) for hotel in self.hotels]
        scored.sort(key=lambda item: item[1], reverse=True)
        return scored[:top_n]

    def generate_itinerary(self, destination: str, days: int, style: str | None) -> List[str]:
        filtered = [row for row in self.itineraries if row["destination"] == destination]
        filtered.sort(key=lambda row: int(row["day"]))

        plans: List[str] = []
        for row in filtered[:days]:
            day_text = f"Day {row['day']}: {row['plan']}"
            if style and style not in row["plan"].lower():
                day_text += f" (Style tip: add more {style} activities)"
            plans.append(day_text)

        if not plans:
            plans = [f"Day {index}: Free exploration in {destination}" for index in range(1, days + 1)]

        return plans

    @staticmethod
    def missing_fields(prefs: UserPreferences) -> List[str]:
        required = {
            "destination": prefs.destination,
            "budget_tier": prefs.budget_tier,
            "trip_days": prefs.trip_days,
        }
        return [field for field, value in required.items() if value is None]


def chat() -> None:
    planner = TravelPlannerAI(DATA_DIR / "hotels.csv", DATA_DIR / "itineraries.csv")
    prefs = UserPreferences()

    print("Travel Planner AI)")
    print("Tell me your plan. Example: 'I need a budget trip to Paris for 3 days with wifi and breakfast.'")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("Bot: Thanks! Have a great trip.")
            return

        prefs = planner.parse_preferences(user_input, prefs)
        missing = planner.missing_fields(prefs)

        if missing:
            questions = {
                "destination": f"Which destination do you prefer? Available: {', '.join(planner.supported_destinations)}",
                "budget_tier": "What budget tier do you want? (budget / mid / luxury)",
                "trip_days": "How many days is your trip? (1-14)",
            }
            print("Bot:", " ".join(questions[item] for item in missing))
            continue

        hotels = planner.recommend_hotels(prefs, top_n=3)
        itinerary = planner.generate_itinerary(
            destination=prefs.destination or "",
            days=prefs.trip_days or 3,
            style=prefs.style,
        )

        print("\nBot: Here are your top hotel recommendations:")
        for rank, (hotel, score) in enumerate(hotels, start=1):
            print(
                f"{rank}. {hotel['name']} ({hotel['destination']}) | ₹{hotel['price_per_night']}/night | "
                f"Rating {hotel['rating']} | Match Score {score:.1f}"
            )
            print(f"   Amenities: {hotel['amenities']}")
            print(f"   Why: {hotel['description']}")

        print("\nBot: Suggested itinerary:")
        for item in itinerary:
            print("-", item)

        print("\nBot: You can refine with more preferences or type 'exit'.")


if __name__ == "__main__":
    chat()
