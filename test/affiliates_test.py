import unittest
import time
import threading
import guppy
from utils.affiliates import Store, Subscriber, BaseAction
import gc

class Val(BaseAction):
    def __init__(self, value: int):
        super(Val, self).__init__(payload=value)
class Val1(Val):
    def __init__(self):
        super(Val1, self).__init__(1)
class Val2(Val):
    def __init__(self):
        super(Val2, self).__init__(2)
class Val3(Val):
    def __init__(self):
        super(Val3, self).__init__(3)
class Val4(Val):
    def __init__(self):
        super(Val4, self).__init__(4)
class Val5(Val):
    def __init__(self):
        super(Val5, self).__init__(5)
action_list = [Val1, Val2, Val3, Val4, Val5]


class start_flag_upload(BaseAction):
    pass
class start_flag_consume(BaseAction):
    pass
class stop_flag(BaseAction):
    pass

def uploader_thread(store: Store, num: int):
    start_flag = store.get_new_subscriber().subscribe_to(start_flag_upload)

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
    me: Subscriber = store.get_new_subscriber()
    binary = bin(code)[2:][::-1]
    expected = 0
    for i in range(len(binary)):
        if binary[i] == '1':
            me.subscribe_to(action_list[i], history=True)
            expected += dispatch_count * (i + 1)
    me.subscribe_to(stop_flag, history=True)
    print(f'code {code} ready and expecting {expected}')
    # wait for main thread to signal go
    store.get_new_subscriber().subscribe_to(start_flag_consume, history=True).consume()
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




dispatch_count = int(50_000)


class MyTestCase(unittest.TestCase):
    def test_main(self):
        def main(store, sub_count, uploader_count):
            threads1 = [threading.Thread(target=subscriber_thread, args=(store, i)) for i in range(sub_count)]
            threads2 = [threading.Thread(target=uploader_thread, args=(store, i % uploader_count)) for i in
                        range(uploader_count * 2)]
            # inspect = threading.Thread(target = inspector, args = (subscribers, ))
            # inspect.daemon = True
            # inspect.start()
            [i.start() for i in threads2]
            [i.start() for i in threads1]
            store.dispatch(start_flag_upload())
            store.dispatch(start_flag_consume())
            for t in threads2:
                t.join()
            print('uploaders finished, main thread halting')
            store.dispatch(stop_flag())
            for t in threads1:
                t.join()
            print("\nthread finished...exiting")
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

    def test_wait(self):
        def slow_uploader(store):
            for _ in range(5):
                time.sleep(.2)
                store.dispatch(Val1())
            time.sleep(.1)
            store.dispatch(stop_flag())
        store = Store()
        t = threading.Thread(target=slow_uploader, args=(store, ))
        t.start()
        sub = store.get_new_subscriber()
        sub.subscribe_to(Val1)
        sub.subscribe_to(stop_flag)
        while True:
            k = sub.consume(timeout=0.05)
            if k is None:
                print('TIMEOUT')
            elif isinstance(k, stop_flag):
                print('STOP FLAG')
                break
            elif isinstance(k, Val1):
                print('GOT 1')

    def test_weakref(self):
        def sub(store: Store, i):
            for _ in range(i):
                store.get_new_subscriber().subscribe_to(start_flag_consume, history=False).consume()
            store.get_new_subscriber().subscribe_to(stop_flag, history=False).consume()
        hp = guppy.hpy()
        hp.setrelheap()
        storee = Store()
        count = 5
        threads1 = [threading.Thread(target=sub, args=(storee, count)) for _ in range(1000)]
        for t in threads1:
            t.daemon = True
            t.start()
        for _ in range(count):
            time.sleep(0.1)
            storee.dispatch(start_flag_consume())
        time.sleep(1)
        gc.collect()
        print(hp.heap())
        # print(hp.heap().byid[0].sp)

    def test_basic_mro(self):
        def sub(subscriber: Subscriber):
            while True:
                c = subscriber.consume()
                if isinstance(c, stop_flag):
                    break
                print('got', c.payload)
        hp = guppy.hpy()
        hp.setrelheap()
        store = Store()
        count = 5
        threads1 = [threading.Thread(target=sub, args=(store.get_new_subscriber().subscribe_to(stop_flag).subscribe_to(Val), )) for _ in range(3)]
        for t in threads1:
            t.daemon = True
            t.start()
        for _ in range(count):
            time.sleep(0.1)
            store.dispatch(Val1())
            store.dispatch(Val2())
            store.dispatch(Val3())
        store.dispatch(stop_flag())
        time.sleep(1)
        print(hp.heap())
        # print(hp.heap().byid[0].sp)

    def test_many_subclasses_mro(self):
        parents = [
            type('val-' + str(i), (Val,), {'__init__': lambda self, inp, i=i: Val.__init__(self, i * 100 + inp)})
            for i in range(100)]
        children = [type(p.__name__ + '-' + str(i), (p,), {'__init__': lambda self, p=p, i=i: p.__init__(self, i)}) for
                    p in parents for i in range(100)]
        record_keeping_parents = [[] for _ in range(100)]
        record_keeping_children = [[] for _ in range(10000)]
        import random
        def uploader(store: Store, count: int):
            store.get_new_subscriber().subscribe_to(start_flag_upload, history=False).consume()
            for _ in range(count):
                r = random.randint(0, 9999)
                record_keeping_parents[r//100].append(r)
                record_keeping_children[r].append(r)
                store.dispatch(children[r]())
        def sub(store: Store, count: int):
            me = store.get_new_subscriber()
            store.get_new_subscriber().subscribe_to(start_flag_consume, history=False).consume()
            comp = []
            for _ in range(count):
                r = random.randint(0, 9999)
                me.subscribe_to(children[r])
                comp.append(r)
            me.subscribe_to(stop_flag)
            tot = 0
            while True:
                c = me.consume()
                if isinstance(c, stop_flag):
                    break
                elif c is None:
                    continue
                tot += c.payload
            tot2 = 0
            for i in list(set(comp)):
                tot2 += sum(record_keeping_children[i])
            assert tot == tot2, str(tot) + ' ' + str(tot2) + str(list(set(comp)))
            store.dispatch(BaseAction(payload=tot == tot2))
        def subp(store: Store, count: int):
            me = store.get_new_subscriber()
            store.get_new_subscriber().subscribe_to(start_flag_consume, history=False).consume()
            comp = []
            for _ in range(count):
                r = random.randint(0, 99)
                me.subscribe_to(parents[r])
                comp.append(r)
            me.subscribe_to(stop_flag)
            tot = 0
            while True:
                c = me.consume()
                if isinstance(c, stop_flag):
                    break
                elif c is None:
                    continue
                tot += c.payload
            tot2 = 0
            for i in list(set(comp)):
                tot2 += sum(record_keeping_parents[i])
            assert tot == tot2, str(tot) + ' ' + str(tot2) + str(list(set(comp)))
            store.dispatch(BaseAction(payload=tot == tot2))

        store = Store()
        random.seed(3243)
        threads1 = [threading.Thread(target=uploader, args=(store, 3000)) for _ in range(30)]
        threads2 = [threading.Thread(target=sub, args=(store, 100)) for _ in range(20)]
        threads3 = [threading.Thread(target=subp, args=(store, 3)) for _ in range(10)]
        for t in threads1:
            t.daemon = True
            t.start()
        for t in threads2:
            t.daemon = True
            t.start()
        for t in threads3:
            t.daemon = True
            t.start()
        store.dispatch(start_flag_upload())
        time.sleep(0.2)
        store.dispatch(start_flag_consume())
        for t in threads1:
            t.join()
        print('stop flag')
        store.dispatch(stop_flag())
        for t in threads2:
            t.join()
        for t in threads3:
            t.join()
        print([x.payload for x in store._store[BaseAction].history])
        print([i for i in range(len(record_keeping_children)) if len(record_keeping_children[i]) == 0])
