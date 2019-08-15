# Copyright (c) 2019 Weston Berg
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from shutil import get_terminal_size
from sys import stdout
from threading import Thread
from time import sleep


class LoadingAnim(object):
    '''
    Structure representing an animation set
    '''
    def __init__(self, characters, rep_cnt, display_func, delay=0.1):
        self.characters = characters
        self.repeat_cnt = rep_cnt
        self.display_func = display_func
        self.delay = delay

        # Construct clear string dynamically to eliminate cursor jitter
        if self.display_func == singular:
            self.num_clear_spaces = 1

        else:
            self.num_clear_spaces = self.repeat_cnt


def composition(characters, cur_cnt):
    return characters[0:cur_cnt + 1]


def singular(characters, cur_cnt):
    return characters[cur_cnt]


_MAX_ANIM_LEN = 20

__dots = ('.' * _MAX_ANIM_LEN)
ANIM_DOT_LINE = LoadingAnim(__dots,
                            len(__dots),
                            composition)

__eq_bar = ('=' * _MAX_ANIM_LEN)
ANIM_EQ_BAR = LoadingAnim(__eq_bar,
                          len(__eq_bar),
                          composition)

__spinner = '/-\\|'
ANIM_SPINNER = LoadingAnim(__spinner,
                           len(__spinner),
                           singular)

__stop_anim = 0
__anim_thread = None
__anim_thread_started = 0


def __animation_behavior(animation, annotation, newline):
    '''
    Behavior to running in animation thread for displaying in terminal
    :param animation: Animation set to display
    :param annotation: Message to display to left of animation
    :param newline: Flag determining whether terminal cursor moves
                    to next line once animation is stopped
    '''
    global __stop_anim

    cur_anim_cnt = 0
    clear_str = '\r' + annotation + '%s' % (' ' * animation.num_clear_spaces)

    local_repeat_cnt = animation.repeat_cnt
    local_chars = animation.characters
    local_display_func = animation.display_func
    local_delay = animation.delay

    while not __stop_anim:
        # Reset
        cur_anim_cnt = 0
        stdout.write(clear_str)
        stdout.flush()

        while cur_anim_cnt < local_repeat_cnt:
            # Print character
            stdout.write('\r' + annotation + '%s' %
                         (local_display_func(local_chars, cur_anim_cnt)))
            stdout.flush()

            cur_anim_cnt += 1
            sleep(local_delay)

    if newline:
        # Write new line
        stdout.write('\n')
    else:
        # Go back to beginning of this line
        stdout.write('\r')

    stdout.flush()


def start(animation, annotation='', newline=True):
    '''
    Starts an animation
    :throws RuntimeError: Animation is already in progress
    :param animation: Animation set to display
    :param annotation: Message to display to left of animation
    :param newline: Flag determining whether terminal cursor moves
                    to next line once animation is stopped
    '''
    global __stop_anim
    global __anim_thread
    global __anim_thread_started

    # Sanity check
    if __anim_thread_started:
        __stop_anim = 1
        __anim_thread.join()
        raise RuntimeError('Calling \'start\' while an '
                           'animation is already in-progress.')

    else:
        # Place in 'else' in case Exception is no longer raised
        # on error in the future
        __stop_anim = 0
        __anim_thread = Thread(target=__animation_behavior,
                               args=(animation, annotation, newline))
        __anim_thread.start()
        __anim_thread_started = 1


def stop(stop_msg=''):
    '''
    Stops current animation and writes ending message if provided
    :throws RuntimeError: Called when no animation is running
    :param stop_msg: Message to write to terminal after stopping animation
    '''
    global __stop_anim
    global __anim_thread
    global __anim_thread_started

    # Sanity check
    if not __anim_thread_started:
        raise RuntimeError('Calling \'stop\' on terminated animation.')

    else:
        # Place in 'else' in case Exception is no longer raised
        # on error in the future
        __stop_anim = 1
        __anim_thread.join()
        __anim_thread_started = 0

        # Print out completion message if proveded
        if len(stop_msg) > 0:
            # Clear and stay on the same terminal line
            # Subtracting 1 from column count because writing an entire line
            # automatically places you down a line in the terminal
            cols, rows = get_terminal_size()
            stdout.write('\r' + (' ' * (cols - 1)))

            # Print message
            stdout.write('\r' + stop_msg + '\n')
            stdout.flush()


# Testing
if __name__ == '__main__':
    # Setup testing
    from msvcrt import getch

    done = 0
    animation = ANIM_SPINNER
    # animation = ANIM_EQ_BAR
    # animation = ANIM_DOT_LINE

    def in_monitor():
        global done

        while not done:
            key = ord(getch())

            if key == 27:
                done = 1

    # Start tests
    t = Thread(target=in_monitor)
    t.start()

    start(animation, annotation="Loading ", newline=False)
    # start(animation)

    while not done:
        pass

    # If no newline is desired and stop message is not provided then the
    # caller is responsible for getting cursor to the next line
    stop('done')
    # print()
    # stop()
    t.join()

    # Multiple animation test
#    done = 0
#    t = Thread(target=in_monitor)
#    t.start()
#
#    start(animation)
#
#    while not done:
#        pass
#
#    stop()
#    t.join()
