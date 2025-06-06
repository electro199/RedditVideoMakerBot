from utils import settings
from utils.console import print_step
from video_creation.final_video import get_text_height


from PIL import Image, ImageDraw, ImageFont


import os
import textwrap


def create_fancy_thumbnail(image, text, text_color, padding, wrap=35):
    """
    It will take the 1px from the middle of the template and will be resized (stretched) vertically to accommodate the extra height needed for the title.
    """
    print_step(f"Creating fancy thumbnail for: {text}")
    font_title_size = 47
    font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), font_title_size)
    image_width, image_height = image.size

    # Calculate text height to determine new image height
    draw = ImageDraw.Draw(image)
    text_height = get_text_height(draw, text, font, wrap)
    lines = textwrap.wrap(text, width=wrap)
    # This are -50 to reduce the empty space at the bottom of the image,
    # change it as per your requirement if needed otherwise leave it.
    new_image_height = image_height + text_height + padding * (len(lines) - 1) - 50

    # Separate the image into top, middle (1px), and bottom parts
    top_part_height = image_height // 2
    middle_part_height = 1  # 1px height middle section
    bottom_part_height = image_height - top_part_height - middle_part_height

    top_part = image.crop((0, 0, image_width, top_part_height))
    middle_part = image.crop((0, top_part_height, image_width, top_part_height + middle_part_height))
    bottom_part = image.crop((0, top_part_height + middle_part_height, image_width, image_height))

    # Stretch the middle part
    new_middle_height = new_image_height - top_part_height - bottom_part_height
    middle_part = middle_part.resize((image_width, new_middle_height))

    # Create new image with the calculated height
    new_image = Image.new("RGBA", (image_width, new_image_height))

    # Paste the top, stretched middle, and bottom parts into the new image
    new_image.paste(top_part, (0, 0))
    new_image.paste(middle_part, (0, top_part_height))
    new_image.paste(bottom_part, (0, top_part_height + new_middle_height))

    # Draw the title text on the new image
    draw = ImageDraw.Draw(new_image)
    y = top_part_height + padding
    for line in lines:
        draw.text((120, y), line, font=font, fill=text_color, align="left")
        y += get_text_height(draw, line, font, wrap) + padding

    # Draw the username "PlotPulse" at the specific position
    username_font = ImageFont.truetype(os.path.join("fonts", "Roboto-Bold.ttf"), 30)
    draw.text(
        (205, 825),
        settings.config["settings"]["channel_name"],
        font=username_font,
        fill=text_color,
        align="left",
    )

    return new_image