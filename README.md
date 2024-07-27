
## Dependencies
- https://github.com/nihui/waifu2x-ncnn-vulkan
- FFmpeg (installed and added to PATH)
- Python 3.10+

# VideoUpscaler
Simple Python program to upscale a video using 'waifu2x-ncnn-vulkan'

## How to use
1. Install the dependencies (waifu2x-ncnn-vulkan for windows is already included in the 'waifu2x-ncnn-vulkan' folder)
2. Put your video in the 'input' folder
3. Run the program with the scale you want to apply to the video: `python process.py 2` (2x scale): available scales are 2, 4, 8, 16, 32
4. The upscaled video will be in the 'output' folder

## Pausing the program
You can close the program whenever you want, you'll just need to run the `python process.py` script to continue the process from where it left off.

