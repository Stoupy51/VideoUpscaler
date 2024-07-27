
# Imports
import os

# Constants
ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
INPUT_FOLDER: str = f"{ROOT}/input"
OUTPUT_FOLDER: str = f"{ROOT}/output"
IMAGES_FOLDER: str = f"{ROOT}/images"
CONVERT_TO_JPG: bool = True
JPG_QUALITY: int = 95	# Range: 0-100
VIDEO_FINAL_BITRATE: int = 240000	# 240 Mbps

# Waifu2x constants
WAIFU2X_FOLDER: str = f"{ROOT}/waifu2x-ncnn-vulkan"
NOISE_LEVEL: int = 3
WAIFU2X_EXECUTABLE: str = f"{WAIFU2X_FOLDER}/waifu2x-ncnn-vulkan.exe"

# Create folders if they don't exist
for folder in [INPUT_FOLDER, OUTPUT_FOLDER, IMAGES_FOLDER]:
	if not os.path.exists(folder):
		os.makedirs(folder)


# Variables
videos: list[str] = [file for file in os.listdir(INPUT_FOLDER) if not file.endswith(".md")]
progressed_videos: list[str] = [file for file in videos if os.path.exists(f"{IMAGES_FOLDER}/{file}/extracted")]
upscaled_videos: list[str] = [file for file in os.listdir(OUTPUT_FOLDER) if not file.endswith(".md")]

