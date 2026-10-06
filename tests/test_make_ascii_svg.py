import os
from PIL import Image
from scripts.make_ascii_svg import image_to_ascii_grid, generate_ascii_svg

def test_image_to_ascii_grid(tmp_path):
    # Create a small 10x10 test image
    test_img_path = tmp_path / "test.png"
    img = Image.new("L", (20, 20), color=255)
    img.save(test_img_path)

    grid = image_to_ascii_grid(str(test_img_path), cols=10, rows=5)
    assert len(grid) == 5
    assert len(grid[0]) == 10
    # Since it's all white (255), it should be all spaces
    assert grid[0] == " " * 10

def test_generate_ascii_svg():
    rows = ["Hello", "World"]
    svg = generate_ascii_svg(rows, cols=5, rows_count=2, title="dom@github: ~$ ./portrait.sh", name="Dominique Contreras")
    assert "<svg" in svg
    assert "</svg>" in svg
    assert "Dominique Contreras" in svg
    assert "Hello" in svg
    assert "World" in svg
