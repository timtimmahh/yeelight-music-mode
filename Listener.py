import numpy as np
from pyaudio import PyAudio, paFloat32
from aubio import pitch, tempo, digital_filter
from multiprocessing import Queue, Event


class Listener:

    def __init__(self, **kwargs) -> None:
        super().__init__()
        self.sample_rate = kwargs.get('sample_rate', 44100)
        self.buffer_size = kwargs.get('buffer_size', 1024)

        self.pa = PyAudio()
        self.pitch = pitch('default', self.buffer_size, self.buffer_size // 2, self.sample_rate)
        self.pitch.set_unit('midi')
        self.pitch.set_tolerance(0.7)
        self.tempo = tempo('default', self.buffer_size, self.buffer_size // 2, self.sample_rate)
        low_filter = digital_filter(3)
        low_filter.set_biquad(
            7.89276652e-4,
            0.00157855,
            7.89276652e-4,
            -1.94146067,
            0.94461777
        )
        mid_filter = digital_filter(3)
        mid_filter.set_biquad(
            0.13357629,
            0.0,
            -0.13357629,
            -1.64841689,
            0.73284743
        )
        high_filter = digital_filter(3)
        high_filter.set_biquad(
            0.72530667,
            -1.45061333,
            0.72530667,
            -1.32614493,
            0.57508174
        )
        self.filters = [low_filter, mid_filter, high_filter]
        self.stream = None

    def start_stream(self):
        self.stream = self.pa.open(format=paFloat32,
                                   channels=1,
                                   rate=self.sample_rate,
                                   input=True,
                                   frames_per_buffer=self.buffer_size)

    def stop_stream(self):
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()
        self.stream = None

    def listen(self, data_queues, stop_event: Event):
        if self.stream is None:
            self.start_stream()
        try:
            def loop():
                # Get microphone data
                data = self.stream.read(self.buffer_size // 2)
                signal = np.fromstring(data, dtype=np.float32)
                for queue in data_queues:
                    queue.put_nowait(signal)
                # for i, signal_filter in enumerate(self.filters):
                #     f_sig = signal_filter(signal)
                #     pitch = self.pitch(f_sig)[0] / 128.0
                #     is_beat = self.tempo(f_sig)
                #     if is_beat > 0.:
                #         # print(f'[{", ".join(str(p) for p in pitches)}]')
                #         callback(pitch, i)

            while True:
                try:
                    loop()
                except KeyboardInterrupt:
                    print("Ctrl-C Terminating...")
                    break
                except Exception as e:
                    print(e)
                    print("ERROR Terminating...")
                    break
        finally:
            stop_event.set()
            # stop_callback()
            self.stop_stream()
