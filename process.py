
# Imports
from config import *
from print import *
import sys
import time
import shutil
import subprocess
from PIL import Image

# Enable colors on Windows 10 terminal
os.system("color")

# Ask if we shutdown the computer after the process
SHUTDOWN: bool = False
info("Shutdown the computer after the process? (y/N)")
if input().lower() == "y":
	SHUTDOWN = True
	info("The computer will shutdown after the process.")

# For each video in the input folder,
for video in videos:

	# If the video has already been upscaled, skip it
	if video in upscaled_videos:
		warning(f"'{video}' has already been processed, remove it from the output folder to reprocess it.")
		continue

	# If the video is in the list of videos that have been partially processed, ask to restart or skip
	images_path: str = f"{IMAGES_FOLDER}/{video}"
	if video in progressed_videos:
		warning(f"'{video}' has already been partially processed, do you want to resume the process? (Y/n)")
		if input().lower() == "n":
			shutil.rmtree(images_path, ignore_errors = True)
	
	# Create the folder for the video's images
	os.makedirs(images_path, exist_ok = True)


	# Extract the video's frames if not already done
	extracted_path: str = f"{images_path}/extracted"
	os.makedirs(extracted_path, exist_ok = True)
	if not os.listdir(extracted_path):
		command: list[str] = ["ffmpeg", "-i", f"{INPUT_FOLDER}/{video}", f"{extracted_path}/%07d.png"]
		debug(f"Extracting frames from '{video}'...")
		subprocess.run(command, capture_output = True)

		# Convert the frames to jpg
		if CONVERT_TO_JPG:
			debug(f"Converting frames to jpg...")
			for frame in os.listdir(extracted_path):
				if frame.endswith(".png"):
					Image.open(f"{extracted_path}/{frame}").save(f"{extracted_path}/{frame.replace('.png', '.jpg')}", quality = JPG_QUALITY)
					os.remove(f"{extracted_path}/{frame}")
	

	# Convert all the frames to jpg if needed
	upscaled_path: str = f"{images_path}/upscaled"
	os.makedirs(upscaled_path, exist_ok = True)
	upscaled_frames: list[str] = os.listdir(upscaled_path)
	if CONVERT_TO_JPG:
		to_convert: list[str] = [frame for frame in upscaled_frames if frame.endswith(".png")]
		debug(f"Converting {len(to_convert)} frames to jpg...")

		# Loop through the frames to convert them to jpg and refresh the list of upscaled frames
		for i, frame in enumerate(to_convert):
			Image.open(f"{upscaled_path}/{frame}").save(f"{upscaled_path}/{frame.replace('.png', '.jpg')}", quality = JPG_QUALITY)
			os.remove(f"{upscaled_path}/{frame}")
			debug(f"Converted '{frame}' to jpg... ({i + 1}/{len(to_convert)})")
		upscaled_frames = os.listdir(upscaled_path)

	# Get all the frames in each folder
	frames: list[str] = os.listdir(extracted_path)
	not_upscaled_frames: list[str] = [frame for frame in frames if frame not in upscaled_frames]
	if not_upscaled_frames:

		# Try to get upscaling ratio if any
		upscaled_ratio: int = None
		if upscaled_frames:
			upscaled_size: tuple[int, int] = Image.open(f"{upscaled_path}/{upscaled_frames[0]}").size
			extracted_size: tuple[int, int] = Image.open(f"{extracted_path}/{frames[0]}").size
			upscaled_ratio = upscaled_size[0] // extracted_size[0]
			info(f"Detected upscaling ratio: {upscaled_ratio}")
		else:
			if len(sys.argv) > 1:
				upscaled_ratio = int(sys.argv[1])
			else:
				upscaled_ratio = int(input("Enter the upscaling ratio: "))


		# For each frame that hasn't been upscaled yet,
		if not EXPRESS_MODE:
			start_time: float = time.perf_counter()
			for i, frame in enumerate(not_upscaled_frames):
				
				# Upscale the frame
				command: list[str] = [
					WAIFU2X_EXECUTABLE,
					"-i", f"{extracted_path}/{frame}",
					"-o", f"{upscaled_path}/{frame}",
					"-n", str(NOISE_LEVEL),
					"-s", str(upscaled_ratio),
				]
				time_elapsed: float = time.perf_counter() - start_time
				average_time: float = time_elapsed / (i + 1)
				remaining_time: float = average_time * (len(not_upscaled_frames) - i)
				debug(f"Upscaling frame '{frame}'... ({i + 1}/{len(not_upscaled_frames)}),\tTime elapsed: {time_elapsed:.2f}s,\tAverage time: {average_time:.2f}s,\tRemaining time: {remaining_time:.2f}s")
				subprocess.run(command, capture_output = True)

				# Convert the frame to jpg
				if CONVERT_TO_JPG and frame.endswith(".png"):
					Image.open(f"{upscaled_path}/{frame}").save(f"{upscaled_path}/{frame.replace('.png', '.jpg')}", quality = JPG_QUALITY)
					os.remove(f"{upscaled_path}/{frame}")
		else:
			# Copy the unprocessed frames to a new folder
			express_path: str = f"{images_path}/express"
			shutil.rmtree(express_path, ignore_errors = True)
			os.makedirs(express_path, exist_ok = True)
			info(f"Copying unprocessed frames to express folder due to express mode...")
			for i, frame in enumerate(not_upscaled_frames):
				if i % 100 == 0:
					debug(f"Copying frame '{frame}'... ({i + 1}/{len(not_upscaled_frames)}),\tProgress: {i / len(not_upscaled_frames) * 100:.2f}%")
				shutil.copy(f"{extracted_path}/{frame}", express_path)
			info(f"Finished copying unprocessed frames to express folder.")
			
			# Upscale the frames
			command: list[str] = [
				WAIFU2X_EXECUTABLE,
				"-i", express_path,
				"-o", upscaled_path,
				"-n", str(NOISE_LEVEL),
				"-s", str(upscaled_ratio),
			]
			info(f"Upscaling frames with express mode...")
			subprocess.run(command)

			# Convert the frames to jpg
			if CONVERT_TO_JPG:
				debug(f"Converting frames to jpg...")
				to_convert: list[str] = os.listdir(upscaled_path)
				for i, frame in enumerate(to_convert):
					if frame.endswith(".png"):
						Image.open(f"{upscaled_path}/{frame}").save(f"{upscaled_path}/{frame.replace('.png', '.jpg')}", quality = JPG_QUALITY)
						os.remove(f"{upscaled_path}/{frame}")
						debug(f"Converted '{frame}' to jpg... ({i + 1}/{len(to_convert)}")
			
			# Remove the express folder
			shutil.rmtree(express_path, ignore_errors = True)

	# Convert the frames to a video
	input_video_for_sound: str = f"{INPUT_FOLDER}/{video}"
	command: list[str] = [
		"ffmpeg",
		"-r", "60",							# Set the framerate to 60
		"-i", f"{upscaled_path}/%07d." + ("jpg" if CONVERT_TO_JPG else "png"),	# Input frames
		"-i", input_video_for_sound,		# Input video for sound
		"-c:v", VIDEO_ENCODER,				# Encode the video
		"-b:v", f"{VIDEO_FINAL_BITRATE}k",	# Set the video bitrate
		"-c:a", "copy",						# Copy the audio without re-encoding
		"-map", "0:v:0",					# Map the first input (frames) as video
		"-map", "1:a:0",					# Map the second input (sound) as audio
		"-pix_fmt", "yuv420p",				# Set the pixel format to yuv420p
		"-preset", "slow",					# Set the encoding preset to slow (slower but better quality)
		"-y",
		f"{OUTPUT_FOLDER}/{video}",			# Output video
	]
	info(f"Converting frames to video...")
	subprocess.run(command, capture_output = False)

# Shutdown the computer if needed
if SHUTDOWN:
	info("Shutting down the computer...")
	if os.name == "nt":
		subprocess.run(["shutdown", "/s", "/t", "0", "/f"], capture_output = False)
	else:
		subprocess.run(["shutdown", "now"], capture_output = False)

