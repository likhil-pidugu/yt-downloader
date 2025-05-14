import os
import shutil
import argparse
from pathlib import Path
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from tqdm import tqdm
import warnings
from time import sleep


warnings.filterwarnings("ignore")

TEMP_DIR = Path(".yt_downloader")

class DownloadProgressBar:
    def __init__(self):
        self.pbar = None
        self.last_downloaded = 0
        self.current_desc = ""

    def __call__(self, d):
        if d['status'] == 'downloading':
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            downloaded = d.get('downloaded_bytes', 0)
            desc = d.get('_filename', 'Downloading')
            
            # Detect change and reset bar
            if not self.pbar or desc != self.current_desc:
                if self.pbar:
                    self.pbar.close()
                self.pbar = tqdm(
                    total=total_bytes,
                    unit='B',
                    unit_scale=True,
                    unit_divisor=1024,
                    desc=f"Downloading: {Path(desc).suffix.replace('.', '').upper()}",
                    bar_format="{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}]",
                    dynamic_ncols=True,
                    ascii=False,
                    ncols=80,
                    leave=False
                )
                self.last_downloaded = 0
                self.current_desc = desc

            increment = downloaded - self.last_downloaded
            if increment > 0:
                self.pbar.update(increment)
            self.last_downloaded = downloaded

        elif d['status'] == 'finished':
            if self.pbar:
                self.pbar.close()
                self.pbar = None


class PostProcessProgressBar:
    def __call__(self, d):
        if d['status'] == 'started':
            with tqdm(
                total=1,
                desc="Converting",
                bar_format="{l_bar}{bar}| {percentage:3.0f}% [{elapsed}]",
                ncols=80,
                leave=False
            ) as pbar:
                sleep(0.5)  # simulate some time
                pbar.update(1)


def download_video(url: str, output_format: str, output_path: str = "downloads", resolution: str = None, title: str = None):
    TEMP_DIR.mkdir(exist_ok=True)
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    temp_outtmpl = str(TEMP_DIR / '%(title)s.%(ext)s')

    # Shared instances to prevent duplicate bars
    download_hook = DownloadProgressBar()
    postprocess_hook = PostProcessProgressBar()

    ydl_opts = {
        'outtmpl': temp_outtmpl,
        'noplaylist': True,
        'quiet': True,
        'no_warnings': True,
        'progress_hooks': [download_hook],
        'restrictfilenames': True,
        'postprocessor_hooks': [postprocess_hook],
        'logger': None,
    }

    if output_format.lower() == 'mp3':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'prefer_ffmpeg': True
        })
    elif output_format.lower() == 'mp4':
        format_str = f"bestvideo[height={resolution}]+bestaudio/best" if resolution else "bestvideo+bestaudio/best"
        ydl_opts.update({
            'format': format_str,
            'merge_output_format': 'mp4',
            'prefer_ffmpeg': True,
            'postprocessor_args': [
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k'
            ]
        })
    else:
        raise ValueError("Output format must be 'mp3' or 'mp4'")

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Move final file
        for file in TEMP_DIR.iterdir():
            if file.is_file():
                final_name = f"{title}.{file.suffix.lstrip('.')}" if title else file.name
                final_path = output_path / final_name
                shutil.move(str(file), str(final_path))
                print(f"\n✅ Saved to: {final_path.resolve()}")

    except DownloadError as e:
        print(f"❌ Error: {e}")
    finally:
        shutil.rmtree(TEMP_DIR, ignore_errors=True)


def main():
    parser = argparse.ArgumentParser(description="YouTube Downloader")
    parser.add_argument('url', help='YouTube video URL')
    parser.add_argument('format', choices=['mp3', 'mp4'], help='Download format')
    parser.add_argument('--output', default='downloads', help='Output directory')
    parser.add_argument('--resolution', help='Video resolution (e.g., 720, 1080, 1440)')
    parser.add_argument('--title', help='Custom title for output file (no extension)')
    args = parser.parse_args()

    download_video(
        url=args.url,
        output_format=args.format,
        output_path=args.output,
        resolution=args.resolution,
        title=args.title
    )


if __name__ == '__main__':
    main()

