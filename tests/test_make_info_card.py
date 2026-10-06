import os
from scripts.make_info_card import generate_info_card_svg

def test_generate_info_card_svg():
    info = {
        "user": "dom@github",
        "name": "Dominique Contreras",
        "role": "Systems and Software Engineer",
        "languages": "C# · Kotlin · C/C++ · Python",
        "backend": ".NET Core · YARP",
    }
    svg = generate_info_card_svg(info)
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Dominique Contreras" in svg
    assert "Systems and Software Engineer" in svg
    assert ".NET Core · YARP" in svg
