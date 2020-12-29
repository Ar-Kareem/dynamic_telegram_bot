from __future__ import annotations

import threading
from functools import partial
from typing import List, Any, NamedTuple, Callable, Union, Iterable
from collections.abc import Iterable as Iterable_abc


Event = NamedTuple('Event', [('data', Any), ('uploader_name', str)])


class Subscriber:
    def __init__(self):
        self._condmutex = threading.Condition()
        self._feed: List[Event] = []

    def _wait_for_event(self) -> None:
        """blocks until an item arrives in the feed."""
        while True:
            # will wait for 49 days but add a while loop just in case an event takes even longer to come
            flag = self._condmutex.wait_for(lambda: len(self._feed) > 0, threading.TIMEOUT_MAX)
            if flag:
                break

    def consume(self) -> Event:
        """Consumes the top item in the feed. If no elements then blocks until an item appears in the feed"""
        with self._condmutex:
            self._wait_for_event()
            return self._feed.pop(0)

    def _new_upload(self, data, uploader_name: str) -> None:
        """Used to add a new event to the feed and notify a single waiter"""
        new_event = Event(data, uploader_name)
        with self._condmutex:
            self._feed.append(new_event)
            self._condmutex.notify(n=1)

    def subscribe_to(self, uploader: Uploader, uploader_name: str) -> None:
        """Starts listening to dispatches from a subscriber"""
        # use partial since the uploader should not specify their name but only dispatch events, the subscriber is
        # the one that chooses the name this design is by choice and it could be the other way around but I prefer
        # this way since it is more explicit to the subscriber who dispatched the event
        custom_notifier = partial(self._new_upload, uploader_name=str(uploader_name))
        uploader._add_to_notify_list(custom_notifier)

    def check_feed_for(self, uploader_name: str) -> bool:
        """Checks whether the feed contains an upload from a specific uploader"""
        for e in self._feed:
            if e.uploader_name == uploader_name:
                return True
        return False


class Uploader:
    def __init__(self):
        self._subscriber_notifiers: List[Callable[[Any], None]] = []

    def _add_to_notify_list(self, notifier: Callable[[Any], None]) -> None:
        self._subscriber_notifiers.append(notifier)

    def dispatch(self, obj: Any = None) -> None:
        for subscriber_notifier in self._subscriber_notifiers:
            subscriber_notifier(obj)


class Store:
    _Subject = NamedTuple('Affiliates',
                          [('manager', Uploader),
                           ('history', List[Event]),
                           ('lock', threading.Lock)])

    def __init__(self):
        self._store: dict[str, Store._Subject] = dict()
        self._lock = threading.Lock()

    def _add_subject_to_store(self, subject_name: str) -> None:
        if subject_name in self._store:
            return
        with self._lock:
            if subject_name not in self._store:
                manager = Uploader()
                self._store[subject_name] = Store._Subject(manager=manager, history=[], lock=threading.Lock())

    def bind_subscribe_to_subject(self, subject_name: str, subscriber: Subscriber, include_history: bool = True) -> None:
        """Make a subscriber get notified whenever an event is dispatched to this subject."""
        subject_name = str(subject_name)
        self._add_subject_to_store(subject_name)  # make sure subject already in store
        subject = self._store[subject_name]
        with subject.lock:  # lock for editing subject
            manager = subject.manager
            subscriber.subscribe_to(manager, uploader_name=subject_name)
            if include_history:
                for data in subject.history:
                    subscriber._new_upload(data, subject_name)

    def bind_uploader_to_subject(self, subject_name: str, uploader: Uploader) -> None:
        """Make a all dispatches from this uploader go to the subscribers of the given subject."""
        subject_name = str(subject_name)
        self._add_subject_to_store(subject_name)  # make sure subject already in store

        # uploader will call dispatch_to with the proper subject name and the subject manager will take care of the rest
        def subject_notifier(obj=None):
            return self.dispatch_to(subject_name=subject_name, obj=obj)

        uploader._add_to_notify_list(subject_notifier)

    def dispatch_to(self, subject_name: str, obj: Any = None) -> None:
        """Dispatch an event to all subscribers of a given subject"""
        subject_name = str(subject_name)
        self._add_subject_to_store(subject_name)  # make sure subject already in store
        subject = self._store[subject_name]
        with subject.lock:  # lock for editing subject
            subject.manager.dispatch(obj)
            subject.history.append(obj)

    def get_subscriber_for(self, subject_name: Union[Iterable[str], str], include_history: bool = True) -> Subscriber:
        """Creates and Returns a new subscriber that is subscribed to the specified subject(s)"""
        new_subscriber = Subscriber()
        # make sure it can be safely iterated on
        if isinstance(subject_name, str) or not isinstance(subject_name, Iterable_abc):
            subject_name = [subject_name]
        for sn in subject_name:
            self.bind_subscribe_to_subject(str(sn), new_subscriber, include_history)
        return new_subscriber
