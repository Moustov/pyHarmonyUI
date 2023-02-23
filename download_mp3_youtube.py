import threading
import tkinter
from tkinter import Label, Entry, Button, END
from tkinter.ttk import Progressbar

from pytube import YouTube
import os


class DownloadMP3Youtube(tkinter.Tk):
    def __init__(self):
        self.list_of_songs = None
        self.song = None
        self.youtube_url = None
        self.url_label = None
        self.search_button = None
        self.progress_bar = None

    def display(self, root: tkinter.Tk):
        self.url_label = Label(root, text="Youtube URL to download")
        self.url_label.pack()
        self.youtube_url = Entry(root)
        self.youtube_url.pack()
        self.search_button = Button(root, text='Search', command=self._do_download_mp3_from_url)
        self.search_button.pack()

        self.progress_bar = Progressbar(root, orient='horizontal', mode='indeterminate', length=280)
        self.progress_bar.pack()

    def _do_download_mp3_from_url(self):
        download_thread = threading.Thread(target=self._download_mp3, name="_download_songs")
        download_thread.start()

    def _download_mp3(self):
        url = self.youtube_url.get()
        self.progress_bar.start()
        print(f"Collecting data from {url}")
        yt = YouTube(url)

        # extract only audio
        video = yt.streams.filter(only_audio=True).first()

        destination = "."

        # download the file
        out_file = video.download(output_path=destination)

        # save the file
        base, ext = os.path.splitext(out_file)
        new_file = base + '.mp3'
        os.rename(out_file, new_file)

        # result of success
        print(yt.title + " has been successfully downloaded.")
        print("Download complete... {}".format(new_file))
        self.progress_bar.stop()

