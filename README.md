**#YT-DOWNLOADER**
  📥 YouTube Video Downloader (Windows &amp; Linux Compatible) This repository provides a powerful YouTube video downloader that supports downloading even lengthy videos at high resolutions.

**Features :**

🎥 Download YouTube videos in **mp4**(video) or **mp3**(audio only)

📶 Specify resolution: `720`, `1080`, etc.

📁 Save to a **custom directory** with **custom title**

✅ Terminal **progress bars** for download + conversion

⚙️ Works on **Windows & Linux**

💡 Silent mode – no unnecessary logs or errors

---

## 🛠️ **Setup Instructions**

### 1️⃣ Install Python (Skip if already installed)

**✅Windows**: [**Download Python**](https://www.python.org/downloads/windows/)

 During install: Check `Add Python to PATH`

<br>

**✅Linux (Debian/Ubuntu):**

  ```bash
  sudo apt update
  sudo apt install python3 python3-pip
  ```

---

### 2️⃣ Install Required Python Packages

```bash
pip install yt_dlp tqdm shutil rich pathlib argparse subprocess
```

---

### 3️⃣ Install **FFmpeg*(Required for mp4/mp3 Merging)

#### ✅ Windows Installation

1. Click here to download : [**FFMPEG**](https://www.gyan.dev/ffmpeg/builds/packages/ffmpeg-7.1.1-essentials_build.zip)
2. Extract **“Essentials build”**(ZIP file) and rename it to **ffmpeg**
3. paste ffmpeg folder at  (e.g., to `C:\ffmpeg`)
4. Add to PATH:

   Search **"Environment Variables"*→ Edit `Path`
   Add: `C:\ffmpeg\bin`
5. ✅ Verify:

   ```bash
   ffmpeg -version
   ```

#### ✅ Linux Installation

```bash
sudo apt update
sudo apt install libxml2
sudo apt install ffmpeg
```

✅ Verify:

```bash
ffmpeg -version
```

---

## ▶️ **How to Run Your Downloader**

### 📥 **Basic Usage (--format mp4 - Best Quality Available)**

```bash
python downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format mp4
```

### 📥 **Download with Custom Resolution (e.g. 1080p)**

```bash
python downloader.py "https://www.youtube.com/watch?v=abc123" --format mp4 --resolution 1080
```

### 🎵 **Download --format mp3 (Audio Only)**

```bash
python downloader.py "https://www.youtube.com/watch?v=abc123" --format mp3
```

### 📁 **Save with Custom Title**

```bash
python downloader.py "https://www.youtube.com/watch?v=abc123" --format mp4 --title "My Cool Video"
```

### 📁 **Save to Custom Directory**

```bash
python downloader.py "https://www.youtube.com/watch?v=abc123" --format mp4 --output "E:/Videos" --title "Python Tutorial"
```

---

## 🧪 **Test Commands with Sample YouTube URLs**

Here are some **working test URLs**:

```bash
python downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --format mp4 --resolution 720 --title "rickroll"

python downloader.py "https://www.youtube.com/watch?v=2Vv-BfVoq4g" --format mp3 --title "Perfect_Song"

python downloader.py "https://www.youtube.com/shorts/Bg4D4PW2WTo" --format mp4 --resolution 1080 --title "kulosa video song"
```

---

## 🧼 Bonus Tips

### 📁 **Change Default Download Folder (globally)**

Update:

```python
parser.add_argument('--output', default='downloads', help='Output directory')
```

to

```python
parser.add_argument('--output', default='E:/YTDownloads', help='Output directory')
```

---

### 🐛 Common Errors & Fixes

| Error                                  | Fix                                     |
| -------------------------------------- | --------------------------------------- |
| `ffmpeg not found`                     | Add `ffmpeg/bin` to `PATH`              |
| `Video unavailable`                    | Check URL or try a different resolution |
| `ValueError: Output format must be...` | Use `--format mp4` or `--format mp3` only                 |

---

Thank you for downloading our project — we truly appreciate your support and hope it enhances your workflow!
