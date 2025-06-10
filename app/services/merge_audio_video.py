import subprocess
import sys
import os

def merge_audio_video(video_path, audio_path, output_path):
    if not os.path.exists(video_path):
        print(f"Error: Video file not found: {video_path}")
        return
    if not os.path.exists(audio_path):
        print(f"Error: Audio file not found: {audio_path}")
        return

    command = [
        "ffmpeg",
        "-i", video_path,
        "-i", audio_path,
        "-c:v", "copy",
        "-c:a", "aac",
        "-shortest",
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        #print(f"✅ Merged successfully! Output saved as: {output_path}")
        return output_path
    except subprocess.CalledProcessError as e:
        print("❌ FFmpeg error:", e)

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python merge.py <video_path> <audio_path> <output_path>")
    else:
        video_file = sys.argv[1]
        audio_file = sys.argv[2]
        output_file = sys.argv[3]
        merge_audio_video(video_file, audio_file, output_file)
