import unittest
import time
import threading
import guppy
from utils.affiliates import AffiliateManager, Subscriber, Uploader


def uploader_thread(uploader, num, manager):
    start_flag = Subscriber()
    manager.bind_subscribe_to_subject(subject_name='start_flag_upload', subscriber=start_flag)
    manager.bind_uploader_to_subject(subject_name=num, uploader=uploader)
    print(f'code {num} ready to give out {int(dispatch_count / 2)}')
    start_flag.consume()  # wait for main thread to signal go
    for _ in range(int(dispatch_count / 2)):
        uploader.dispatch(num)


# 5 topics with a total of 80 subscriptions
# each topic has two uploaders
# each uploader uploads 50k events to its topic
# (thus each subscription to a topic will get you 100k events)
# (total of 0.5 mill dispatches and 8 mill receives)
# 6 minutes

dispatch_count = int(10_000)


def subscriber_thread(subscriber, code, manager):
    manager.bind_subscribe_to_subject(subject_name='halt_event', subscriber=subscriber)
    start_flag = Subscriber()
    manager.bind_subscribe_to_subject(subject_name='start_flag_consume', subscriber=start_flag)

    binary = bin(code)[2:][::-1]
    expected = 0
    for i in range(len(binary)):
        if binary[i] == '1':
            manager.bind_subscribe_to_subject(subject_name=i + 1, subscriber=subscriber)
            expected += dispatch_count * (i + 1)
    print(f'code {code} ready and expecting {expected}')
    start_flag.consume()  # wait for main thread to signal go
    while True:
        e = subscriber.consume()
        if e is None:
            continue
        if e.uploader_name == 'halt_event':  # or subscriber.check_feed_for('halt_event'):
            break
        # expected -= e.data
    expected = 0
    if expected != 0:
        print(f'\n !!!!!!!! code {code} ended up with {expected}')
    else:
        print('ok ', end='')


def inspector(subscribers):
    while True:
        time.sleep(10)
        t = sum(len(i._feed) for i in subscribers)
        print(f' [{t}] ', end='', flush=True)


def main(a, b, c, d):
    manager = a
    uploader_set1 = b
    uploader_set2 = c
    subscribers = d

    threads1 = []
    threads2 = []

    for i, u in enumerate(subscribers):
        t = threading.Thread(target=subscriber_thread, args=(u, i, manager))
        threads1 += [t]

    for i, u in enumerate(uploader_set1):
        t = threading.Thread(target=uploader_thread, args=(u, i + 1, manager))
        threads2 += [t]
    for i, u in enumerate(uploader_set2):
        t = threading.Thread(target=uploader_thread, args=(u, i + 1, manager))
        threads2 += [t]

    # inspect = threading.Thread(target = inspector, args = (subscribers, ))
    # inspect.daemon = True
    # inspect.start()

    for i in range(max(len(threads1), len(threads2))):
        if i < len(threads1):
            threads1[i].start()
        if i < len(threads2):
            threads2[i].start()

    time.sleep(0.25)
    print('starting')

    manager.dispatch_to(subject_name='start_flag_upload')
    time.sleep(1)
    print('uploaders finished, main thread halting')
    manager.dispatch_to(subject_name='halt_event')

    for t in threads2:
        t.join()

    manager.dispatch_to(subject_name='start_flag_consume')

    for t in threads1:
        t.join()

    print("\nthread finished...exiting")


class MyTestCase(unittest.TestCase):
    def test_something(self):
        hp = guppy.hpy()
        hp.setrelheap()

        main_manager = AffiliateManager()
        garbage = []
        for _ in range(2):
            print('\n\n\n IN MAIN LOOP', _, ' \n\n\n')
            garbage.append(main_manager._store)
            main_manager._store = dict()
            uploader_set1_ = [Uploader() for _ in range(5)]
            uploader_set2_ = [Uploader() for _ in range(5)]
            subscribers_ = [Subscriber() for _ in range(32)]
            main(main_manager, uploader_set1_, uploader_set2_, subscribers_)

        print(hp.heap())
        print(hp.heap().byid[0].sp)

        self.assertEqual(True, True)
