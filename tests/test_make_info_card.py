import os
from scripts.make_info_card import generate_info_card_svg

def test_generate_info_card_svg():
    info = {
        "user": "dom@arch",
        "host": "Dominique Contreras",
        "os": "Arch Linux x86_64",
        "gamedev": "Unity · Godot (C#, GDScript)",
    }
    svg = generate_info_card_svg(info)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Dominique Contreras" in svg
    assert "Arch Linux x86_64" in svg
    assert "Unity · Godot (C#, GDScript)" in svg
