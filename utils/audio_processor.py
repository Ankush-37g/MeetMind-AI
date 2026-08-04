import yt_dlp
from pydub import AudioSegment
import os

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_youtube_audio(url: str) -> str:
    # Build the output filename template — yt-dlp will substitute
    # the video's title and extension into this pattern
    output_path = os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s")

    ydl_opts = {
        # Download the best available audio-only stream; fall back to
        # the best overall stream if no audio-only format exists
        "format": "bestaudio/best",

        # Where to save the file, using the template defined above
        "outtmpl": output_path,

        # Post-processing steps applied after download
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",       # extract audio using ffmpeg
                "preferredcodec": "wav",           # convert to WAV
                "preferredquality": "192",         # bitrate quality (kbps) before WAV conversion
            }
        ],

        # Suppress yt-dlp's verbose console output
        "quiet": True,
    }

    # Open a yt-dlp downloader instance with the options above
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # Download the video and extract metadata (title, ext, etc.)
        info = ydl.extract_info(url, download=True)

        # yt-dlp reports the original filename (e.g. .webm/.m4a) before
        # postprocessing renames it to .wav — build the correct final
        # filename manually since prepare_filename() doesn't know about
        # the postprocessor's output extension
        filename = ydl.prepare_filename(info).replace(".webm", ".wav").replace(".m4a", ".wav")

    return filename



def convert_to_wav(input_path: str) -> str:
    """Convert any audio/video file to WAV format using pydub."""
    
    # Build the output filename by replacing the original extension with "_converted.wav"
    # e.g. "meeting.mp3" -> "meeting_converted.wav"
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"
    
    # Load the input file (pydub uses ffmpeg internally, so it works with
    # almost any audio/video format: mp3, mp4, m4a, ogg, etc.)
    audio = AudioSegment.from_file(input_path)
    
    # Downmix to mono (1 channel) and resample to 16kHz —
    # this matches what Whisper expects and keeps file size/processing time down
    audio = audio.set_channels(1).set_frame_rate(16000)
    
    # Write out the processed audio as a WAV file
    audio.export(output_path, format="wav")
    
    # Return the path so the caller (e.g. the transcription step) can use it
    return output_path



def chunk_audio(wav_path : str, chunk_minutes : int=10) -> list:

    audio = AudioSegment.from_wav(wav_path)

    chunk_ms = chunk_minutes * 60 * 1000

    chunks = []

    for i,start in enumerate(range(0, len(audio), chunk_ms)):
        end = start + chunk_ms
        chunk = audio[start:end]
        chunk_path = f"{wav_path}_chunk_{i}.wav"
        chunk.export(chunk_path, format="wav")
        chunks.append(chunk_path)
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)

    print(f"Audio ready - {len(chunks)} chunks created.")
    return chunks

