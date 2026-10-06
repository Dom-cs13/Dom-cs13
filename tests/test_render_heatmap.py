from scripts.render_heatmap_svg import build_grid, render_svg

def test_build_grid():
    days = [
        {"date": "2025-01-01", "count": 0, "level": 0},
        {"date": "2025-01-02", "count": 5, "level": 2},
    ]
    grid = build_grid(days)
    assert len(grid) >= 1
    # Check that day is placed in grid
    found = any(cell and cell[0] == "2025-01-02" for col in grid for cell in col)
    assert found

def test_render_svg():
    data = {
        "days": [{"date": "2025-01-01", "count": 2, "level": 1}],
        "current_streak": {"length": 1, "start": "2025-01-01", "end": "2025-01-01"},
        "longest_streak": {"length": 1, "start": "2025-01-01", "end": "2025-01-01"},
        "total_contributions": 2,
        "best_day": {"date": "2025-01-01", "count": 2},
        "range": {"start": "2025-01-01", "end": "2025-01-01"},
    }
    svg = render_svg(data)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "contributions in the last year" in svg
