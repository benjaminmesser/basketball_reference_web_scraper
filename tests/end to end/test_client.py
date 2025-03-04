import datetime
import filecmp
import os
import time
from unittest import TestCase

from basketball_reference_web_scraper.client import player_box_scores, season_schedule, players_advanced_season_totals, \
    play_by_play, players_season_totals
from basketball_reference_web_scraper.data import Location, Outcome
from basketball_reference_web_scraper.data import OutputWriteOption, OutputType, Team, PeriodType


class BaseEndToEndTest(TestCase):

    def setUp(self):
        # To avoid getting rate-limited
        time.sleep(20)

    def tearDown(self):
        # To avoid getting rate-limited
        time.sleep(20)


class TestPlayerBoxScores(BaseEndToEndTest):

    def setUp(self):
        super().setUp()

        self.box_scores = player_box_scores(day=11, month=3, year=2024)

    def test_first_entry(self):
        self.assertIsNotNone(self.box_scores)
        self.assertNotEqual(0, len(self.box_scores))
        self.assertEqual(124, len(self.box_scores))
        self.assertDictEqual({
            "name": "Nikola Jokić",
            "slug": "jokicni01",
            "team": Team.DENVER_NUGGETS,
            "opponent": Team.TORONTO_RAPTORS,
            "location": Location.HOME,
            "outcome": Outcome.WIN,
            "seconds_played": 2286,
            "made_field_goals": 14,
            "attempted_field_goals": 26,
            "made_three_point_field_goals": 1,
            "attempted_three_point_field_goals": 3,
            "made_free_throws": 6,
            "attempted_free_throws": 6,
            "offensive_rebounds": 6,
            "defensive_rebounds": 11,
            "assists": 12,
            "steals": 6,
            "blocks": 2,
            "turnovers": 2,
            "personal_fouls": 3,
            "plus_minus": 13.0,
            "game_score": 42.5,
        },
            self.box_scores[0])


class TestCsvPlayerBoxScores(BaseEndToEndTest):

    def test_csv_output(self):
        output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/playerboxscores/2024/03/11.csv",
        )
        player_box_scores(
            day=11,
            month=3,
            year=2024,
            output_type=OutputType.CSV,
            output_file_path=output_file_path,
            output_write_option=OutputWriteOption.WRITE,
        )

        self.assertTrue(
            filecmp.cmp(
                output_file_path,
                os.path.join(
                    os.path.dirname(__file__),
                    "./output/expected/playerboxscores/2024/03/11.csv",
                )))


class TestJsonPlayerBoxScores(BaseEndToEndTest):

    def test_json_output(self):
        output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/playerboxscores/2024/03/11.json",
        )
        player_box_scores(
            day=11,
            month=3,
            year=2024,
            output_type=OutputType.JSON,
            output_file_path=output_file_path,
            output_write_option=OutputWriteOption.WRITE,
        )

        self.assertTrue(
            filecmp.cmp(
                output_file_path,
                os.path.join(
                    os.path.dirname(__file__),
                    "./output/expected/playerboxscores/2024/03/11.json",
                )))


class TestSeasonSchedule(BaseEndToEndTest):
    def test_2001_season_schedule(self):
        schedule = season_schedule(season_end_year=2001)
        self.assertIsNotNone(schedule)

    def test_current_year_season_schedule(self):
        schedule = season_schedule(season_end_year=datetime.datetime.now().year)
        self.assertIsNotNone(schedule)


class TestPlayerAdvancedSeasonTotals(BaseEndToEndTest):
    def test_totals(self):
        player_season_totals = players_advanced_season_totals(season_end_year=2019)
        self.assertIsNotNone(player_season_totals)
        self.assertTrue(len(player_season_totals) > 0)


class TestPlayByPlay(BaseEndToEndTest):
    def test_BOS_2018_10_16_play_by_play(self):
        plays = play_by_play(
            home_team=Team.BOSTON_CELTICS,
            day=16,
            month=10,
            year=2018,
        )
        self.assertIsNotNone(plays)

    def test_BOS_2018_10_16_play_by_play_csv_to_file(self):
        output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/2018_10_16_BOS_pbp.csv",
        )
        play_by_play(
            home_team=Team.BOSTON_CELTICS,
            day=16,
            month=10,
            year=2018,
            output_type=OutputType.CSV,
            output_file_path=output_file_path,
            output_write_option=OutputWriteOption.WRITE,
        )

        self.assertTrue(
            filecmp.cmp(
                output_file_path,
                os.path.join(
                    os.path.dirname(__file__),
                    "./output/expected/2018_10_16_BOS_pbp.csv",
                )))

    def test_overtime_play_by_play(self):
        plays = play_by_play(
            home_team=Team.PORTLAND_TRAIL_BLAZERS,
            day=22,
            month=10,
            year=2018,
        )
        last_play = plays[-1]
        self.assertIsNotNone(last_play)
        self.assertEqual(1, last_play["period"])
        self.assertEqual(PeriodType.OVERTIME, last_play["period_type"])

    def test_overtime_play_by_play_to_json_file(self):
        output_file_path = os.path.join(
            os.path.dirname(__file__),
            "./output/generated/2018_10_22_POR_pbp.json",
        )
        play_by_play(
            home_team=Team.PORTLAND_TRAIL_BLAZERS,
            day=22,
            month=10,
            year=2018,
            output_type=OutputType.JSON,
            output_file_path=output_file_path,
            output_write_option=OutputWriteOption.WRITE,
        )

        self.assertTrue(
            filecmp.cmp(output_file_path,
                        os.path.join(
                            os.path.dirname(__file__),
                            "./output/expected/2018_10_22_POR_pbp.json",
                        )))


class TestPlayersSeasonTotals(TestCase):

    def test_2018(self):
        totals = players_season_totals(season_end_year=2018)

        for total in totals:
            # TODO: @jaebradley turn this into a dataclass with validation
            self.assertIsNot("", total["name"])
            self.assertIsNot("League Average", total["name"])
            self.assertTrue(total["slug"])
            self.assertTrue(total["name"])
            self.assertTrue(total["positions"])
            self.assertGreater(total["age"], 0)
            self.assertGreaterEqual(total["games_played"], 0)
            self.assertGreaterEqual(total["games_started"], 0)
            self.assertGreaterEqual(total["minutes_played"], 0)
            self.assertGreaterEqual(total["made_field_goals"], 0)
            self.assertGreaterEqual(total["attempted_field_goals"], total["made_field_goals"])
            self.assertGreaterEqual(total["made_three_point_field_goals"], 0)
            self.assertGreaterEqual(total["attempted_three_point_field_goals"], total["made_three_point_field_goals"])
            self.assertGreaterEqual(total["made_free_throws"], 0)
            self.assertGreaterEqual(total["attempted_free_throws"], total["made_free_throws"])
            self.assertGreaterEqual(total["offensive_rebounds"], 0)
            self.assertGreaterEqual(total["defensive_rebounds"], 0)
            self.assertGreaterEqual(total["assists"], 0)
            self.assertGreaterEqual(total["steals"], 0)
            self.assertGreaterEqual(total["blocks"], 0)
            self.assertGreaterEqual(total["turnovers"], 0)
            self.assertGreaterEqual(total["personal_fouls"], 0)
            self.assertGreaterEqual(total["points"], 0)
