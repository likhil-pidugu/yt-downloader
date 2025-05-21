import argparse, shutil, subprocess
from pathlib import Path
from yt_dlp import YoutubeDL
from yt_dlp.utils import DownloadError
from rich.progress import Progress, BarColumn, TextColumn
import re

def safe_filename(name: str) -> str:
    return re.sub(r'[<>:"/\\\\|?*]', '_', name)

TEMP_DIR = Path(".yt_downloader")

class QuietLogger:
    def debug(self, msg): pass
    def warning(self, msg): pass
    def error(self, msg): print(f"[Error] {msg}")

def progress_hook(progress_bar, task_id):
    def hook(d):
        if d['status'] == 'downloading':
            t, dled, s = d.get('total_bytes') or d.get('total_bytes_estimate', 0), d.get('downloaded_bytes', 0), d.get('speed', 0) or 0
            if t and dled and 'fragment_index' not in d:
                progress_bar.update(task_id, completed=dled, total=t, downloaded_mb=dled/1048576, total_mb=t/1048576, speed_kbps=s/1024)
        elif d['status'] == 'finished':
            t, dled = d.get('total_bytes', 0), d.get('downloaded_bytes', 0)
            progress_bar.update(task_id, completed=dled, total=t, downloaded_mb=dled/1048576, total_mb=t/1048576, speed_kbps=0)
    return hook

def download_youtube_media(url, output_format="mp4", output_path=str(Path.home()/"Downloads"), resolution="720", quality="192", title=None, playlist=False):
    TEMP_DIR.mkdir(exist_ok=True)
    Path(output_path).mkdir(parents=True, exist_ok=True)
    temp_out = str(TEMP_DIR / '%(title)s.%(ext)s')
    final_name = title if title else '%(title)s'
    final_out = str(Path(output_path) / (final_name + ".%(ext)s"))

    with Progress(
        TextColumn("Downloading :"), TextColumn("{task.percentage:>3.0f}%|"),
        BarColumn(), TextColumn("{task.percentage:>3.0f}%"),
        TextColumn("[{task.fields[downloaded_mb]:.1f}mb/{task.fields[total_mb]:.1f}mb]"),
        TextColumn("{task.fields[speed_kbps]:.0f}kb/s"),
    ) as progress:
        task = progress.add_task("", start=False, downloaded_mb=0.0, total_mb=0.0, speed_kbps=0)

        ydl_opts = {
            'outtmpl': temp_out, 'noplaylist': not playlist, 'quiet': True,
            'no_warnings': True, 'progress_hooks': [progress_hook(progress, task)],
            'restrictfilenames': True, 'logger': QuietLogger(), 'overwrites': True
        }

        if output_format == 'mp4':
            ydl_opts.update({
                'format': f"bestvideo[height<={resolution}]+bestaudio/best[ext=mp4]",
            })
        elif output_format == 'mp3':
            q = quality if quality in ['128', '192', '320'] else '192'
            ydl_opts.update({
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': q
                }],
                'prefer_ffmpeg': True
            })
        else:
            return {'status': 'error', 'message': "Invalid format", 'file_path': None}

        try:
            with YoutubeDL(ydl_opts) as ydl:
                progress.start_task(task)
                if playlist:
                    info = ydl.extract_info(url, download=False)
                    entries = info.get("entries", [])

                    for entry in entries:
                        if not entry:
                            continue
                        entry_url = entry.get('webpage_url') or entry.get('url')
                        entry_title = entry.get('title', 'video')
                        progress.update(task, description=f"Downloading: {entry_title}")

                        TEMP_DIR.mkdir(exist_ok=True)
                        with YoutubeDL(ydl_opts) as single_ydl:
                            single_ydl.download([entry_url])

                        for f in TEMP_DIR.iterdir():
                            if f.is_file():
                                clean_name = safe_filename(title or entry_title)
                                out_name = f"{clean_name}.{f.suffix.lstrip('.')}"
                                out_path = Path(output_path) / out_name
                                shutil.move(str(f), str(out_path))
                                print(f"Saved: {out_name}")
                        shutil.rmtree(TEMP_DIR, ignore_errors=True)
                else:
                    ydl.download([url])
                    # for f in TEMP_DIR.iterdir():
                    #     if f.is_file():
                    #         out_name = f"{title}.{f.suffix.lstrip('.')}" if title else f.name
                    #         out_path = Path(output_path) / out_name
                    #         shutil.move(str(f), str(out_path))
            for f in TEMP_DIR.iterdir():
                if f.is_file():
                    out_name = f"{title}.{f.suffix.lstrip('.')}" if title else f.name
                    out_path = Path(output_path) / out_name
                    shutil.move(str(f), str(out_path))
            return {'status': 'success', 'message': f"Saved to: {Path(output_path).resolve()}", 'file_path': str(Path(output_path).resolve())}
        except DownloadError as e:
            return {'status': 'error', 'message': f"Download failed: {e}", 'file_path': None}
        finally:
            shutil.rmtree(TEMP_DIR, ignore_errors=True)

def open_folder(path):
    try:
        if shutil.which('xdg-open'): subprocess.run(['xdg-open', path])
        elif shutil.which('open'): subprocess.run(['open', path])
        elif shutil.which('explorer'): subprocess.run(['explorer', path])
    except Exception: pass

def main():
    p = argparse.ArgumentParser(description="Fast YouTube Downloader")
    p.add_argument('url'), p.add_argument('--format', choices=['mp3','mp4'], default='mp4')
    p.add_argument('--output', default=str(Path.home()/"Downloads"))
    p.add_argument('--resolution', default='720')
    p.add_argument('--title')
    p.add_argument('--playlist', action='store_true', help='Download as playlist')
    p.add_argument('--open', action='store_true', help='Open folder after download')
    a = p.parse_args()
    r = a.resolution if a.format=='mp4' else '720'
    q = a.resolution if a.format=='mp3' else '192'
    res = download_youtube_media(
    a.url,
    a.format,
    a.output,
    resolution=a.resolution if a.format == 'mp4' else '720',
    quality=a.resolution if a.format == 'mp3' else '192',
    title=a.title,
    playlist=a.playlist )
    print(res['message'])
    if a.open and res['status'] == 'success': open_folder(a.output)

if __name__ == '__main__':
    main()
