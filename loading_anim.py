# Copyright (c) 2019 Weston Berg
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from sys import stdout
from threading import Thread
from time import sleep


class LoadingAnim(object):
    def __init__(self, character_str, rep_cnt, display_func, delay=0.1):
        self.character_str = character_str
        self.repeat_cnt = rep_cnt
        self.display_func = display_func
        self.delay = delay

        # Clear string length based on animation length to avoid cursor jitter
        if self.display_func == singular:
            self.num_clear_spaces = 1
        else:
            self.num_clear_spaces = self.repeat_cnt


def composition(character_str, cur_cnt):
    return character_str[0:cur_cnt]


def singular(character_str, cur_cnt):
    return character_str[cur_cnt:cur_cnt + 1]


_MAX_ANIM_LEN = 20

_dots = '.' * _MAX_ANIM_LEN
ANIM_DOT_LINE = LoadingAnim(_dots,
                            len(_dots),
                            composition)

_eq_bar = '=' * _MAX_ANIM_LEN
ANIM_EQ_BAR = LoadingAnim(_eq_bar,
                          len(_eq_bar),
                          composition)

_spinner = '/-\\|'
ANIM_SPINNER = LoadingAnim(_spinner,
                           len(_spinner),
                           singular)

_stop_anim = 0
_anim_thread = None
_anim_thread_started = 0


def __animation_behavior(animation):
    global _stop_anim

    cur_anim_cnt = 0
    clear_str = '\r%s' % (' ' * animation.num_clear_spaces)

    # Make local copies of data
    local_repeat_cnt = animation.repeat_cnt
    local_chars = animation.character_str
    local_display_func = animation.display_func
    local_delay = animation.delay

    while not _stop_anim:
        # Reset
        cur_anim_cnt = 0
        stdout.write(clear_str)
        stdout.flush()

        while cur_anim_cnt < local_repeat_cnt:
            # Print character
            stdout.write('\r%s' %
                         (local_display_func(local_chars, cur_anim_cnt)))
            stdout.flush()
            cur_anim_cnt += 1
            sleep(local_delay)

    # Write new line
    stdout.write('\n')
    stdout.flush()


def anim_start(animation):
    global _stop_anim
    global _anim_thread
    global _anim_thread_started

    # Sanity check
    if _anim_thread_started:
        _stop_anim = 1
        _anim_thread.join()
        raise RuntimeError('Calling \'anim_start\' while an '
                           'animation is already in-progress.')

    else:
        # Place in 'else' in case Exception is no longer raised
        # on error in the future
        _stop_anim = 0
        _anim_thread = Thread(target=__animation_behavior, args=(animation,))
        _anim_thread.start()
        _anim_thread_started = 1


def anim_stop():
    global _stop_anim
    global _anim_thread
    global _anim_thread_started

    # Sanity check
    if not _anim_thread_started:
        raise RuntimeError('Calling \'anim_stop\' on terminated animation.')

    else:
        # Place in 'else' in case Exception is no longer raised
        # on error in the future
        _stop_anim = 1
        _anim_thread.join()
        _anim_thread_started = 0


# Testing
if __name__ == '__main__':
    # Setup testing
    from msvcrt import getch

    done = 0
    # animation = ANIM_DOT_LINE
    # animation = ANIM_EQ_BAR
    animation = ANIM_SPINNER

    def in_monitor():
        global done

        while not done:
            key = ord(getch())
            if key == 27:
                done = 1

    # Start tests
    t = Thread(target=in_monitor)
    t.start()

    anim_start(animation)
    # anim_start(animation)

    while not done:
        pass

    anim_stop()
    # anim_stop()
    t.join()

    # Multiple animation test
#    done = 0
#    t = Thread(target=in_monitor)
#    t.start()
#
#    anim_start(animation)
#
#    while not done:
#        pass
#
#    anim_stop()
#    t.join()
