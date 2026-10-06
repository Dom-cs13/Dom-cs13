import os
from scripts.make_info_card import generate_info_card_svg

def test_generate_info_card_svg():
    info = {
        "user": "dom@arch",
        "host": "Dominique Contreras",
        "os": "Arch Linux · CachyOS",
        "gamedev": "Unity · Godot (C#, GDScript)",
    }
    svg = generate_info_card_svg(info)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Dominique Contreras" in svg
    assert "Arch Linux · CachyOS" in svg
    assert "Unity · Godot (C#, GDScript)" in svg
