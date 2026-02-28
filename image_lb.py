from PIL import Image, ImageDraw, ImageFont
from database import fetch

def generate_image():

    img = Image.new("RGB", (800, 600), "black")
    draw = ImageDraw.Draw(img)

    rows = fetch("SELECT user_id, elo FROM players ORDER BY elo DESC LIMIT 10")

    y = 50
    rank = 1

    for user_id, elo in rows:
        text = f"#{rank} | {user_id} | {elo} Elo"
        draw.text((50, y), text, fill="white")
        y += 50
        rank += 1

    path = "leaderboard.png"
    img.save(path)

    return path
