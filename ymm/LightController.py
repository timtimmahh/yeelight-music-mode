from multiprocessing import Process, Queue, Event
from .Listener import Listener
from .Configuration import Configuration


def audio_callback_process(device, signal_filter, get_pitch, get_tempo,
                           data_queue: Queue, stop_event: Event):
    """
    A process for handling audio signal data for a specific frequency band.

    :param DeviceConfig device: The device to use for this frequency band.
    :param signal_filter: The signal filter function from aubio.digital_filter.
    :param get_pitch: The pitch function from aubio.pitch.
    :param get_tempo: The tempo function from aubio.tempo.
    :param Queue data_queue: A queue used to obtain audio signal data.
    :param Event stop_event: An event for being notified when the process should stop.
    """
    if device.data.music_mode:
        device.data.stop_music()
    device.data.start_music()
    while not stop_event.is_set():
        try:
            signals = data_queue.get()
            if stop_event.is_set():
                break
            f_sig = signal_filter(signals)
            pitch = get_pitch(f_sig)[0] / 128.0
            is_beat = get_tempo(f_sig)
            if is_beat > 0.:
                device.data.set_color(pitch)
        except KeyboardInterrupt:
            print('Process exiting...')
            break
        except ValueError as e:
            print(e)
            break
    device.data.stop_music()


class Controller(object):

    def __init__(self, config_data) -> None:
        """
        Controls audio analysis and bulb coloring.

        :param Configuration config_data: The configuration data to use.
        """
        super().__init__()
        self.config_data = config_data
        self.devices = config_data.devices
        self.color_schemes = config_data.color_schemes
        self.currentScheme = None if len(self.color_schemes) == 0 else self.color_schemes[0]
        self.listener = Listener()

    # def audio_callback(self, data, i):
    #     # pass
    #     # for i, d in enumerate(data):
    #     if data > 0.:
    #         self.devices[i].data.set_color(data)

    # def stop_callback(self):
    #     for device in self.devices:
    #         device.data.stop_music()

    def start_music(self):
        """
        Starts an audio callback process for each device and starts listening to audio.
        """
        processes = []
        queues = []
        stop_event = Event()
        for i, device in enumerate(self.devices):
            queue = Queue()
            queues.append(queue)
            p = Process(target=audio_callback_process,
                        args=(device, self.listener.filters[i],
                              self.listener.pitch, self.listener.tempo,
                              queue, stop_event))
            processes.append(p)
            p.start()
        self.listener.listen(queues, stop_event)
        for proc in processes:
            proc.join()
