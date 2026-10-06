import os
from scripts.make_info_card import generate_info_card_svg

def test_generate_info_card_svg():
    info = {
        "user": "dom@github",
        "name": "Dominique Contreras",
        "role": "Aspiring Developer",
        "stack": "Python, JavaScript, HTML",
        "engines": "Unity, Unreal Engine",
    }
    svg = generate_info_card_svg(info)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Dominique Contreras" in svg
    assert "Python, JavaScript, HTML" in svg
    assert "Unity, Unreal Engine" in svg
