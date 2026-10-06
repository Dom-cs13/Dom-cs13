import datetime
from scripts.fetch_contributions import (
    parse_contributions_html,
    compute_current_streak,
    compute_longest_streak,
    build_data,
)

SAMPLE_HTML = """
<table>
  <tbody>
    <tr>
      <td class="ContributionCalendar-day" data-date="2025-01-01" id="c-1" data-level="1"></td>
      <tool-tip for="c-1">2 contributions on January 1st.</tool-tip>
      <td class="ContributionCalendar-day" data-date="2025-01-02" id="c-2" data-level="2"></td>
      <tool-tip for="c-2">5 contributions on January 2nd.</tool-tip>
      <td class="ContributionCalendar-day" data-date="2025-01-03" id="c-3" data-level="0"></td>
      <tool-tip for="c-3">No contributions on January 3rd.</tool-tip>
    </tr>
  </tbody>
</table>
"""

def test_parse_contributions_html():
    days = parse_contributions_html(SAMPLE_HTML)
    assert len(days) == 3
    assert days[0] == {"date": "2025-01-01", "count": 2, "level": 1}
    assert days[1] == {"date": "2025-01-02", "count": 5, "level": 2}
    assert days[2] == {"date": "2025-01-03", "count": 0, "level": 0}

def test_compute_current_streak():
    days = [
        {"date": "2025-01-01", "count": 1, "level": 1},
        {"date": "2025-01-02", "count": 2, "level": 1},
        {"date": "2025-01-03", "count": 0, "level": 0}, # today with 0 count shouldn't break prior streak if it's last
    ]
    streak, start, end = compute_current_streak(days)
    assert streak == 2
    assert start == "2025-01-01"
    assert end == "2025-01-02"

def test_compute_longest_streak():
    days = [
        {"date": "2025-01-01", "count": 1, "level": 1},
        {"date": "2025-01-02", "count": 2, "level": 1},
        {"date": "2025-01-03", "count": 0, "level": 0},
        {"date": "2025-01-04", "count": 1, "level": 1},
    ]
    longest, start, end = compute_longest_streak(days)
    assert longest == 2
    assert start == "2025-01-01"
    assert end == "2025-01-02"

def test_build_data():
    days = [
        {"date": "2025-01-01", "count": 2, "level": 1},
        {"date": "2025-01-02", "count": 5, "level": 2},
    ]
    data = build_data(days, username="Dom-cs13")
    assert data["username"] == "Dom-cs13"
    assert data["total_contributions"] == 7
    assert data["active_days"] == 2
    assert data["best_day"]["date"] == "2025-01-02"
    assert data["best_day"]["count"] == 5
