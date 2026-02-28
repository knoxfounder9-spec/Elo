from PIL import Image, ImageDraw, ImageFont
from database import fetch
import os


def generate_image():

    # 🔥 FIXED TABLE NAME
    rows = fetch(
        "SELECT user_id, elo, wins, losses FROM users ORDER BY elo DESC LIMIT 10"
    )

    img = Image.new("RGB", (800, 600), "black")
    draw = ImageDraw.Draw(img)

    # Optional: better font
    try:
        font = ImageFont.truetype("arial.ttf", 30)
    except:
        font = ImageFont.load_default()

    y = 80
    rank = 1

    if not rows:
        draw.text((250, 250), "No Players Yet", fill="white", font=font)
    else:
        for user_id, elo, wins, losses in rows:
            text = f"#{rank} | {elo} Elo | W:{wins} L:{losses}"
            draw.text((100, y), text, fill="white", font=font)

            y += 50
            rank += 1

    path = "leaderboard.png"
    img.save(path)

    return path
