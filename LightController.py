from Listener import Listener
from Configuration import Configuration, discover_bulbs
from multiprocessing import Process, Queue, Event


def audio_callback_process(device, signal_filter, get_pitch, get_tempo,
                           data_queue: Queue, stop_event: Event):
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

    def __init__(self, config_data: Configuration) -> None:
        super().__init__()
        self.config_data = config_data
        self.devices = config_data.devices
        self.color_schemes = config_data.color_schemes
        self.currentScheme = None if len(self.color_schemes) == 0 else self.color_schemes[0]
        self.scan_devices()
        self.listener = Listener()

    def scan_devices(self):
        bulbs = discover_bulbs()
        ids = [device.name for device in self.devices]
        for bulb in bulbs:
            if bulb.dev_id not in ids:
                self.config_data.add_device(bulb)

    # def audio_callback(self, data, i):
    #     # pass
    #     # for i, d in enumerate(data):
    #     if data > 0.:
    #         self.devices[i].data.set_color(data)

    # def stop_callback(self):
    #     for device in self.devices:
    #         device.data.stop_music()

    def start_music(self):
        # for device in self.devices:
        #     device.data.start_music()
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
