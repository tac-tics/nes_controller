import sys
import json
from controller import Device, Event, Key
import vlc
import time


class Player:
    def __init__(self, state):
        self.sources = state['sources']
        self.start_time = state.get('current_time', 0)

        try:
            current_source = state['current_source']
            self.source_index = self.sources.index(current_source)
        except ValueError:
            self.source_index = 0


        self.vlc_instance = vlc.Instance()
        self.player = self.vlc_instance.media_player_new()

    def current_source(self):
        return self.sources[self.source_index]

    def play(self):
        source = self.current_source()
        # print(source, self.start_time / 1000)
        media = self.vlc_instance.media_new(source)
        self.player.set_media(media)
        self.player.play()
        self.player.set_fullscreen(True)
        self.player.set_time(self.start_time)
        time.sleep(0.1)
        self.player.video_set_spu(-1) # disable subtitles

    def play_next(self):
        self.source_index += 1
        self.source_index %= len(self.sources)
        self.start_time = 0
        self.play()

    def play_prev(self):
        self.source_index -= 1
        self.source_index %= len(self.sources)
        self.start_time = 0
        self.play()

    def ff(self, amount):
        new_time = self.player.get_time() + amount
        if new_time > self.player.get_length():
            self.play_next()
        else:
            self.player.set_time(new_time)

    def rewind(self, amount):
        new_time = self.player.get_time() - amount
        if new_time < 0:
            self.play_prev()
        else:
            self.player.set_time(new_time)

    def pause(self):
        self.player.pause()

    def state(self):
        if self.player.is_playing:
            current_time = self.player.get_time()
        else:
            current_time = self.start_time

        return {
            'sources': self.sources,
            'current_source': self.sources[self.source_index],
            'current_time': current_time,
        }


def main():
    device = Device()
    with open('state.json') as infile:
        state = json.load(infile)

    player = Player(state)
    player.play()

    try:
        while True:
            event, key = device.read()
            if event == Event.keyup and key == Key.right:
                player.ff(3000)
            elif event == Event.keyup and key == Key.left:
                player.rewind(3000)
            elif event == Event.keyup and key == Key.shl:
                player.rewind(10000)
            elif event == Event.keyup and key == Key.shr:
                player.ff(10000)
            elif event == Event.keyup and key == Key.start:
                player.pause()
            elif event == Event.keydn and key == Key.select:
                break
#            elif event == Event.keydn and key == Key.a:
#                breakpoint()
    except KeyboardInterrupt:
        pass
    finally:
        with open('state.json', 'w') as outfile:
            json.dump(player.state(), outfile, indent=4, ensure_ascii=False)

        sys.exit(0)



if __name__ == '__main__':
    main()
