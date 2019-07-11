from sys import stdout
from threading import Thread
from time import sleep


class LoadingAnim(object):
    def __init__(self, characters, rep_cnt, display_func, delay=0.1):
        self.characters = characters
        self.repeat_cnt = rep_cnt
        self.display_func = display_func
        self.delay = delay


def composition(characters, cur_cnt):
    return ''.join(x for x in characters[0:cur_cnt])


def incremental(characters, cur_cnt):
    return characters[cur_cnt]   


__MAX_ANIM_LEN = 20
__CLEAR_LINE_STR = '\r%s' % (' ' * __MAX_ANIM_LEN)

__dots = ('.,' * (__MAX_ANIM_LEN - 1)).split(',')
ANIM_DOT_LINE = LoadingAnim(__dots,
                            len(__dots),
                            composition)

__eq_bar = ('=,' * (__MAX_ANIM_LEN - 1)).split(',')
ANIM_EQ_BAR = LoadingAnim(__eq_bar,
                          len(__eq_bar),
                          composition)

__spinner = ['/', '-', '\\', '|', '']
ANIM_SPINNER = LoadingAnim(__spinner,
                           len(__spinner),
                           incremental)

__stop_anim = 0
__anim_thread = None
__anim_thread_started = 0


def __animation_behavior(animation):
    global __stop_anim

    cur_anim_cnt = 0
    local_repeat_cnt = animation.repeat_cnt
    local_chars = animation.characters
    local_display_func = animation.display_func
    local_delay = animation.delay

    while not __stop_anim:
        # Reset
        cur_anim_cnt = 0
        stdout.write(__CLEAR_LINE_STR)
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
    global __stop_anim
    global __anim_thread
    global __anim_thread_started

    # Sanity check
    if __anim_thread_started:
        __stop_anim = 1
        __anim_thread.join()
        raise RuntimeError('Calling \'anim_start\' while an '
                           'animation is already in-progress.')

    else:
        # Place in 'else' in case Exception is no longer raised
        # on error in the future
        __stop_anim = 0
        __anim_thread = Thread(target=__animation_behavior, args=(animation,))
        __anim_thread.start()
        __anim_thread_started = 1


def anim_stop():
    global __stop_anim
    global __anim_thread
    global __anim_thread_started

    # Sanity check
    if not __anim_thread_started:
        raise RuntimeError('Calling \'anim_stop\' on terminated animation.')

    else:
        # Place in 'else' in case Exception is no longer raised
        # on error in the future
        __stop_anim = 1
        __anim_thread.join()
        __anim_thread_started = 0


# Testing
if __name__ == '__main__':
    # Setup testing
    from msvcrt import getch

    done = 0
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
