import subprocess
import math

input_file = "5.mp4"
clip_length = 180

ffprobe = r"C:\Codes\ffmpeg\bin\ffprobe.exe"
ffmpeg  = r"C:\Codes\ffmpeg\bin\ffmpeg.exe"

result = subprocess.run(
    [
        ffprobe,
        "-v","error",
        "-show_entries","format=duration",
        "-of","default=noprint_wrappers=1:nokey=1",
        input_file
    ],
    stdout=subprocess.PIPE,
    stderr=subprocess.STDOUT,
    text=True
)

duration = float(result.stdout.strip())
num_clips = math.ceil(duration / clip_length)

print(f"total length: {duration:.2f} sec")
print(f"will be clipped to {num_clips} segments")

for i in range(num_clips):
    start = i * clip_length
    output = f"5_{i+1:03d}.mp4"

    subprocess.run([
        ffmpeg,
        "-ss", str(start),
        "-i", input_file,
        "-t", str(clip_length),
        "-c","copy",
        output
    ])

print("finish clipping")