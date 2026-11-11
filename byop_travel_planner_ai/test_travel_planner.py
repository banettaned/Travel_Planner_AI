from pathlib import Path
import unittest

from app import TravelPlannerAI, UserPreferences


BASE_DIR = Path(__file__).resolve().parent


class TravelPlannerAITests(unittest.TestCase):
    def setUp(self) -> None:
        self.planner = TravelPlannerAI(BASE_DIR / "data" / "hotels.csv", BASE_DIR / "data" / "itineraries.csv")

    def test_parse_preferences_extracts_required_fields(self) -> None:
        prefs = UserPreferences()
        self.planner.parse_preferences("I need a budget trip to Paris for 3 days with wifi and breakfast", prefs)
        self.assertEqual(prefs.destination, "Paris")
        self.assertEqual(prefs.budget_tier, "budget")
        self.assertEqual(prefs.trip_days, 3)
        self.assertIn("wifi", prefs.amenities)

    def test_recommendations_prioritize_destination_and_budget(self) -> None:
        prefs = UserPreferences(destination="Tokyo", budget_tier="budget", trip_days=2, amenities=["wifi"])
        top = self.planner.recommend_hotels(prefs, top_n=1)
        self.assertEqual(top[0][0]["destination"], "Tokyo")
        self.assertEqual(top[0][0]["name"], "Tokyo Capsule Hub")


if __name__ == "__main__":
    unittest.main()
