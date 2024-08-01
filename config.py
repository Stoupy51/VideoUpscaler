
# Imports
import os

# Constants
ROOT: str = os.path.dirname(os.path.abspath(__file__)).replace("\\", "/")
INPUT_FOLDER: str = f"{ROOT}/input"
OUTPUT_FOLDER: str = f"{ROOT}/output"
IMAGES_FOLDER: str = f"{ROOT}/images"

# Configuration
CONVERT_TO_JPG: bool = True				# If True, the frames will be converted to jpg format.
JPG_QUALITY: int = 95					# Range: 0-100
VIDEO_ENCODER: str = "libx265"			# libx265, libx264, libvpx-vp9, libaom-av1, libaom-av1, libaom-av1
VIDEO_FINAL_BITRATE: int = 180000		# 180 Mbps
EXPRESS_MODE: bool = True				# If True, all the unprocessed frames will be copied to a new folder and fed to the program.
										# Resulting in a faster process but no real progress tracking.

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

