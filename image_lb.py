from PIL import Image, ImageDraw, ImageFont
from database import fetch
import os


def generate_image():

    rows = fetch(
        "SELECT user_id, elo, wins, losses FROM users ORDER BY elo DESC LIMIT 10"
    )

    img_path = "assets/leaderboard_bg.png"

    # Load background safely
    if os.path.exists(img_path):
        img = Image.open(img_path).convert("RGB")
    else:
        # Fallback if image missing
        img = Image.new("RGB", (1200, 800), "#0f0f0f")

    draw = ImageDraw.Draw(img)

    # 🔥 Auto detect image size
    width, height = img.size

    # ✅ Better font scaling based on image size
    try:
        font_title = ImageFont.truetype("arial.ttf", int(height * 0.07))
        font_text = ImageFont.truetype("arial.ttf", int(height * 0.045))
    except:
        font_title = ImageFont.load_default()
        font_text = ImageFont.load_default()

    # ================= TITLE ================= #

    title_text = "<a:emoji_3:1477325503961501969># ⛩️🩸**BLOOD BATTLES**🩸⛩️<a:emoji_3:1477325503961501969>"

    title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
    title_width = title_bbox[2] - title_bbox[0]

    draw.text(
        ((width - title_width) // 2, height * 0.05),
        title_text,
        font=font_title,
        fill="white"
    )

    # ================= PLAYER LIST ================= #

    y = height * 0.20
    rank = 1

    if not rows:
        draw.text(
            (width * 0.3, y),
            "No Players Yet",
            font=font_text,
            fill="white"
        )
    else:
        for user_id, elo, wins, losses in rows:

            text = (
                f"#{rank}  "
                f"ELO: {elo}  "
                f"W:{wins}  "
                f"L:{losses}"
            )

            draw.text(
                (width * 0.15, y),
                text,
                font=font_text,
                fill="white"
            )

            y += height * 0.08
            rank += 1

    output_path = "leaderboard_output.png"
    img.save(output_path)

    return output_path
