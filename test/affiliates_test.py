import unittest
import time
import threading
import guppy
from utils.affiliates import Store, Subscriber, BaseAction


class val1(BaseAction):
    name = '[BaseAction] val1'
    payload = 1
class val2(BaseAction):
    name = '[BaseAction] val2'
    payload = 2
class val3(BaseAction):
    name = '[BaseAction] val3'
    payload = 3
class val4(BaseAction):
    name = '[BaseAction] val4'
    payload = 4
class val5(BaseAction):
    name = '[BaseAction] val5'
    payload = 5
action_list = [val1, val2, val3, val4, val5]


class start_flag_upload(BaseAction):
    name = '[BaseAction] start_flag_upload'
class start_flag_consume(BaseAction):
    name = '[BaseAction] start_flag_consume'
class stop_flag(BaseAction):
    name = '[BaseAction] stop_flag'


def uploader_thread(store: Store, num: int):
    start_flag = store.get_new_subscriber()
    start_flag.subscribe_to(start_flag_upload, include_history=True)

    action_to_dispatch = action_list[num]

    print(f'code {num} ready to give out {int(dispatch_count / 2)}')
    start_flag.consume()  # wait for main thread to signal go
    for _ in range(int(dispatch_count / 2)):
        store.dispatch(action_to_dispatch())


# 5 topics with a total of 80 subscriptions between 32 subscribers
# each topic has two uploaders
# each uploader uploads 50k events to its topic
# (thus each subscription to a topic will get you 100k events)
# (total of 0.5 mill dispatches and 8 mill receives)
# 6 minutes

def subscriber_thread(store, code):
    start_flag = store.get_new_subscriber()
    start_flag.subscribe_to(start_flag_consume, include_history=True)
    me: Subscriber = store.get_new_subscriber()
    binary = bin(code)[2:][::-1]
    expected = 0
    for i in range(len(binary)):
        if binary[i] == '1':
            me.subscribe_to(action_list[i], include_history=True)
            expected += dispatch_count * (i + 1)
    me.subscribe_to(stop_flag, include_history=True)
    print(f'code {code} ready and expecting {expected}')
    start_flag.consume()  # wait for main thread to signal go
    while True:
        e = me.consume()
        if e is None:
            continue
        if isinstance(e, stop_flag):  # or subscriber.check_feed_for('halt_event'):
            break
        expected -= e.payload
    if expected != 0:
        print(f'\n !!!!!!!! code {code} ended up with {expected}')
        assert False
    else:
        print('ok ', end='')


def inspector(subscribers):
    while True:
        time.sleep(10)
        t = sum(len(i._feed) for i in subscribers)
        print(f' [{t}] ', end='', flush=True)


def main(store, sub_count, uploader_count):
    threads1 = []
    threads2 = []

    for i in range(sub_count):
        t = threading.Thread(target=subscriber_thread, args=(store, i))
        threads1 += [t]

    for i in range(uploader_count):
        t = threading.Thread(target=uploader_thread, args=(store, i))
        threads2 += [t]
    for i in range(uploader_count):
        t = threading.Thread(target=uploader_thread, args=(store, i))
        threads2 += [t]

    # inspect = threading.Thread(target = inspector, args = (subscribers, ))
    # inspect.daemon = True
    # inspect.start()

    # store.dispatch(start_flag_consume)
    store.dispatch(start_flag_upload())
    store.dispatch(start_flag_consume())

    # for i in range(max(len(threads1), len(threads2))):
    #     if i < len(threads1):
    #         threads1[i].start()
    #     if i < len(threads2):
    #         threads2[i].start()
    for i in threads2:
        i.start()
    for i in threads1:
        i.start()


    for t in threads2:
        t.join()

    print('uploaders finished, main thread halting')
    store.dispatch(stop_flag())

    for t in threads1:
        t.join()

    print("\nthread finished...exiting")



dispatch_count = int(100_000)


class MyTestCase(unittest.TestCase):
    def test_something(self):
        hp = guppy.hpy()
        hp.setrelheap()

        store = Store()
        garbage = []
        for _ in range(1):
            print('\n\n\n IN MAIN LOOP', _, ' \n\n\n')
            # garbage.append(store._store)
            main(store, sub_count=32, uploader_count=5)
            # store._store = dict()
        print(hp.heap())
        print(hp.heap().byid[0].sp)

