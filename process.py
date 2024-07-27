
# Imports
from config import *
import sys
import time
import shutil
import subprocess
from PIL import Image


# For each video in the input folder,
for video in videos:

	# If the video has already been upscaled, skip it
	if video in upscaled_videos:
		print(f"'{video}' has already been processed, remove it from the output folder to reprocess it.")
		continue

	# If the video is in the list of videos that have been partially processed, ask to restart or skip
	images_path: str = f"{IMAGES_FOLDER}/{video}"
	if video in progressed_videos:
		print(f"'{video}' has already been partially processed, do you want to resume the process? (Y/n)")
		if input().lower() == "n":
			shutil.rmtree(images_path, ignore_errors = True)
	
	# Create the folder for the video's images
	os.makedirs(images_path, exist_ok = True)


	# Extract the video's frames if not already done
	extracted_path: str = f"{images_path}/extracted"
	os.makedirs(extracted_path, exist_ok = True)
	if not os.listdir(extracted_path):
		command: list[str] = ["ffmpeg", "-i", f"{INPUT_FOLDER}/{video}", f"{extracted_path}/%07d.png"]
		print(f"Extracting frames from '{video}'...")
		subprocess.run(command, capture_output = True)

		# Convert the frames to jpg
		if CONVERT_TO_JPG:
			print(f"Converting frames to jpg...")
			for frame in os.listdir(extracted_path):
				if frame.endswith(".png"):
					Image.open(f"{extracted_path}/{frame}").save(f"{extracted_path}/{frame.replace('.png', '.jpg')}", quality = JPG_QUALITY)
			for frame in os.listdir(extracted_path):
				if frame.endswith(".png"):
					os.remove(f"{extracted_path}/{frame}")
	

	# Get all the frames in each folder
	upscaled_path: str = f"{images_path}/upscaled"
	os.makedirs(upscaled_path, exist_ok = True)
	frames: list[str] = os.listdir(extracted_path)
	upscaled_frames: list[str] = os.listdir(upscaled_path)
	not_upscaled_frames: list[str] = [frame for frame in frames if frame not in upscaled_frames]


	# Try to get upscaling ratio if any
	upscaled_ratio: int = None
	if upscaled_frames:
		upscaled_size: tuple[int, int] = Image.open(f"{upscaled_path}/{upscaled_frames[0]}").size
		extracted_size: tuple[int, int] = Image.open(f"{extracted_path}/{frames[0]}").size
		upscaled_ratio = upscaled_size[0] // extracted_size[0]
		print(f"Detected upscaling ratio: {upscaled_ratio}")
	else:
		if len(sys.argv) > 1:
			upscaled_ratio = int(sys.argv[1])
		else:
			upscaled_ratio = int(input("Enter the upscaling ratio: "))


	# For each frame that hasn't been upscaled yet,
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
		print(f"Upscaling frame '{frame}'... ({i + 1}/{len(not_upscaled_frames)}),\tTime elapsed: {time_elapsed:.2f}s,\tAverage time: {average_time:.2f}s,\tRemaining time: {remaining_time:.2f}s")
		subprocess.run(command, capture_output = True)

		# Convert the frame to jpg
		if CONVERT_TO_JPG and frame.endswith(".png"):
			Image.open(f"{upscaled_path}/{frame}").save(f"{upscaled_path}/{frame.replace('.png', '.jpg')}", quality = JPG_QUALITY)
			os.remove(f"{upscaled_path}/{frame}")
	
	# Convert the frames to a video
	command: list[str] = [
		"ffmpeg",
		"-r", "60",
		"-i", f"{upscaled_path}/%07d." + ("jpg" if CONVERT_TO_JPG else "png"),
		"-c:v", "libx264",
		"-b:v", f"{VIDEO_FINAL_BITRATE}k",
		"-pix_fmt", "yuv420p",
		"-y",
		f"{OUTPUT_FOLDER}/{video}",
	]
	print(f"Converting frames to video...")
	subprocess.run(command, capture_output = False)

