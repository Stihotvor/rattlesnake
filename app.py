import time

import matplotlib
import matplotlib.pyplot as plt
import pyaudio
import numpy as np

matplotlib.use('Agg')
# https://stackoverflow.com/questions/7088672/pyaudio-working-but-spits-out-error-messages-each-time


class Plotter:
    def __init__(self):
        self.count = 0
        self.x = []
        self.y = []
        self.limit = 100
        plt.figure(figsize=(10, 7))
        plt.xlim(0, self.limit)
        plt.ylim(-1000, 1000)

    def plot(self, y):
        self.x.append(self.count)
        self.y.append(y)
        self.count += 1

    def save(self):
        plt.plot(self.x, self.y, 'o-k', linewidth=1)
        plt.savefig('fig.png')


class ANC:
    WIDTH = 2
    CHANNELS = 2
    RATE = 44100
    CHUNK = int(RATE / 20)  # RATE / number of updates per second

    def __init__(self, plotter):
        self.plotter = plotter
        self.pa = pyaudio.PyAudio()

    def callback(self, in_data, frame_count, time_info, status):
        # self.plotter.plot(in_data)
        invert_data = self.invert(in_data)
        return invert_data, pyaudio.paContinue

    def run(self):
        stream = self.pa.open(
            format=self.pa.get_format_from_width(self.WIDTH),
            channels=self.CHANNELS,
            rate=self.RATE,
            input=True,
            output=True,
            # frames_per_buffer=CHUNK,
            stream_callback=self.callback
        )

        stream.start_stream()

        while stream.is_active() and self.plotter.count <= self.plotter.limit:
            time.sleep(0.1)

        self.plotter.save()
        stream.stop_stream()
        stream.close()
        self.pa.terminate()

    def invert(self, data):
        """
        Inverts the byte data it received utilizing an XOR operation.

        :param data: A chunk of byte data
        :return inverted: The same size of chunked data inverted bitwise
        """

        # Convert the bytestring into an integer
        intwave = np.frombuffer(data, dtype=np.int16)
        peak = np.average(np.abs(intwave)) * 2
        self.plotter.plot(peak)

        # Invert the integer
        invintwave = np.invert(intwave)

        # Convert the integer back into a bytestring
        inverted = np.frombuffer(invintwave, dtype=np.byte)

        # Return the inverted audio data
        return inverted


if __name__ == '__main__':
    plotter = Plotter()
    anc = ANC(plotter=plotter)
    anc.run()
