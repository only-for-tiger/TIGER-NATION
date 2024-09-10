from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image, ImageDraw, ImageFont
import os
import requests
from io import BytesIO
import pyqrcode  # Alternative QR code library
import logging

# Set up logging to capture debug information
logging.basicConfig(filename='debug.log', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Define user agent for the WebDriver
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36"

# Set Chrome options for WebDriver
options = Options()
options.add_argument(f'user-agent={user_agent}')
options.add_argument("--start-maximized")
options.add_argument('--ignore-certificate-errors')
options.add_argument("--disable-extensions")
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
options.add_argument('--headless')  # Run in headless mode for no GUI

# Path to chromedriver executable
driver_path = r"C:\Users\ravin\Downloads\chromedriver-win64\chromedriver-win64\chromedriver.exe"

# Initialize the WebDriver
service = Service(driver_path)
driver = webdriver.Chrome(service=service, options=options)

# Define file paths
temp_image_path = "temp_profile_image.png"
output_path = "final_output_image.png"

try:
    # Ask user for the profile URL
    profile_url = input("Please enter the profile URL: ")  # Corrected to full Twitter profile URL

    # Generate QR code for the profile URL using pyqrcode
    qr_code = pyqrcode.create(profile_url)
    qr_image_path = "qr_code.png"
    qr_code.png(qr_image_path, scale=6)  # Generates the QR code with a scale factor

    # Navigate to the profile page
    driver.get(profile_url)

    # Wait for the profile image to be present and download it
    WebDriverWait(driver, 20).until(EC.presence_of_element_located((By.CSS_SELECTOR, "img[src*='profile_images']")))
    image_element = driver.find_element(By.CSS_SELECTOR, "img[src*='profile_images']")
    additional_image_url = image_element.get_attribute("src")
    response = requests.get(additional_image_url)
    response.raise_for_status()
    additional_image = Image.open(BytesIO(response.content))
    additional_image.save(temp_image_path)

    # Load the main image
    image_path = r"C:\Users\ravin\Downloads\Copy of Red and Black Gradient Modern Professional Id Card\1.png"
    image = Image.open(image_path)
    draw = ImageDraw.Draw(image)

    # Define the main text and font
    main_text = profile_url.split('/')[-1]
    font_path = r"C:\Users\ravin\Downloads\marykate\MaryKate.ttf"
    font_size = 50
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        font = ImageFont.load_default()  # Fallback to default font if MaryKate font isn't available

    # Define the bold effect by drawing the text multiple times
    bold_offset = 1

    # Calculate text size and position
    text_bbox = draw.textbbox((0, 0), main_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    # Calculate the position for the text
    image_width, image_height = image.size
    x = int((image_width - text_width) / 2 + 70)  # Move text 70 pixels to the right
    y = int((image_height - text_height) / 2 - 70)  # Move text 70 pixels up

    # Define text color
    text_color = (255, 255, 0)  # Yellow

    # Draw the main text multiple times with offset to simulate bold effect
    for offset in range(-bold_offset, bold_offset + 1):
        draw.text((x + offset, y), main_text, font=font, fill=text_color)
        draw.text((x, y + offset), main_text, font=font, fill=text_color)

    # Add the final text to the image to ensure it's on top
    draw.text((x, y), main_text, font=font, fill=text_color)

    # Define the Arial font for the secondary text
    arial_font_path = "arial.ttf"
    arial_font_size = 35
    try:
        arial_font = ImageFont.truetype(arial_font_path, arial_font_size)
    except IOError:
        arial_font = ImageFont.load_default()  # Fallback to default font if Arial font isn't available

    # Process the main text to get the number sequence
    def text_to_numbers(text):
        numbers = [ord(char.upper()) - ord('A') + 1 for char in text if char.isalpha()]
        return numbers

    numbers = text_to_numbers(main_text)
    first_7_numbers = numbers[:7]  # Limit to 7 numbers
    numbers_str = ''.join(map(str, first_7_numbers))  # Remove spaces

    # Define the secondary text
    secondary_text = f"TIGER NO : {numbers_str}"

    # Calculate the size and position for the secondary text
    secondary_bbox = draw.textbbox((0, 0), secondary_text, font=arial_font)
    secondary_width = secondary_bbox[2] - secondary_bbox[0]
    secondary_height = secondary_bbox[3] - secondary_bbox[1]

    # Position the secondary text below the main text
    secondary_x = int((image_width - secondary_width) / 2 + 70)
    secondary_y = int(y + text_height + 40)  # Increase offset to move text further down

    # Define secondary text color
    secondary_text_color = (255, 255, 255)  # White

    # Add the secondary text to the image
    draw.text((secondary_x, secondary_y), secondary_text, font=arial_font, fill=secondary_text_color)

    # Load and resize the QR code image
    qr_code_image = Image.open(qr_image_path).resize((200, 200)).convert('RGBA')

    # Load and resize the additional profile image
    additional_image = Image.open(temp_image_path).resize((200, 200)).convert('RGBA')

    # Calculate positions for pasting images
    qr_code_x = int((image_width - qr_code_image.width) / 7.6 + 0)
    qr_code_y = int(y + text_height + 89.5)  # Place below the main text with a 50-pixel gap
    additional_image_x = int((image_width - additional_image.width) / 2 - additional_image.width - 88)
    additional_image_y = int((image_height - additional_image.height) / 2.6)  # Center vertically

    # Paste QR code and additional images onto the main image
    image.paste(qr_code_image, (qr_code_x, qr_code_y), qr_code_image)
    image.paste(additional_image, (additional_image_x, additional_image_y), additional_image)

    # Save the final image and open it
    image.save(output_path)
    print(f"Image saved with text, additional image, and QR code at {output_path}")
    os.startfile(output_path)

except Exception as e:
    logging.error(f"An error occurred: {e}")
    raise

finally:
    # Clean up resources
    driver.quit()
    if os.path.exists(temp_image_path):
        os.remove(temp_image_path)
    if os.path.exists(qr_image_path):
        os.remove(qr_image_path)
