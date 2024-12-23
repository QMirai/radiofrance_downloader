
# Podcast Audio Downloader

A Python script to download podcasts and audio files from **Radio France** and **ListenNotes** websites. The script uses Selenium for web scraping and supports parallel downloading with `aria2`.

## Features
- Downloads podcast episodes from Radio France and ListenNotes.
- Automatically organizes files into folders based on podcast titles.
- Supports parallel downloads using `aria2` for faster performance.
- Includes options for testing and customizable output paths.

---

## Prerequisites
### 1. Install Python Dependencies
Install the required Python libraries using `pip`:
```bash
pip install -r requirements.txt
```

### 2. Install `aria2`
`aria2` is used for downloading audio files. Install it based on your operating system:

#### On Arch Linux:
```bash
sudo pacman -S aria2
```

#### On Ubuntu/Debian:
```bash
sudo apt install aria2
```

#### On macOS:
```bash
brew install aria2
```

#### On Windows:
Download `aria2c` from [the official website](https://aria2.github.io/) and add it to your `PATH`.

### 3. Install ChromeDriver
Ensure you have a compatible version of ChromeDriver installed. You can automate this step with `webdriver-manager`:
```bash
pip install webdriver-manager
```

Alternatively, download ChromeDriver manually from [here](https://chromedriver.chromium.org/downloads) and ensure it matches your Chrome version.

---

## Usage
Run the script with the following options:

```bash
python audio.py <link> [options]
```

### Positional Argument
- **`<link>`**: The URL of the podcast page (Radio France or ListenNotes).

### Options
- **`-p, --output_path`**: Directory where the downloaded files will be saved. Default is `D:/podcasts`.
- **`-l, --parallel`**: Number of parallel downloads. Default is `4`.
- **`-t, --test`**: Test mode to download only the first file.

---

## Example
### Download Podcasts from Radio France
```bash
python audio.py "https://www.radiofrance.fr/example-podcast" -p "/home/user/podcasts" -l 3
```

---

## How It Works
1. **Web Scraping**: The script uses Selenium to load the podcast webpage and retrieve audio URLs.
2. **File Organization**: Creates folders based on podcast titles and saves episodes with cleaned filenames.
3. **Parallel Downloads**: Uses `aria2` and threading for fast and efficient downloads.

---

## Notes
- Ensure that `aria2` is installed and accessible from your system's `PATH`.

---

## Troubleshooting
1. **`aria2c: command not found`**  
   Install `aria2` and ensure it's in your `PATH`.

2. **WebDriver Errors**  
   Ensure ChromeDriver is installed and matches your Chrome browser version.

---

## License
This script is open-source and available under the MIT License.
