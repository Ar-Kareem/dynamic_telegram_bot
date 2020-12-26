from __future__ import annotations

import threading
from functools import partial
from typing import List, Any, NamedTuple, Callable


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
        # noinspection PyProtectedMember
        uploader._add_subscriber(custom_notifier)

    def check_feed_for(self, uploader_name: str) -> bool:
        """Checks whether the feed contains an upload from a specific uploader"""
        for e in self._feed:
            if e.uploader_name == uploader_name:
                return True
        return False

    def _clear(self) -> None:
        """Clears the internal feed"""
        with self._condmutex:
            self._feed.clear()


class Uploader:
    def __init__(self):
        self._subscriber_notifiers: List[Callable[[Any], None]] = []

    def _add_subscriber(self, notifier: Callable[[Any], None]) -> None:
        self._subscriber_notifiers.append(notifier)

    def dispatch(self, obj: Any = None) -> None:
        for subscriber_notifier in self._subscriber_notifiers:
            subscriber_notifier(obj)


class AffiliateManager:
    _Affiliates = NamedTuple('Affiliates',
                             [('uploaders', List[Uploader]),
                              ('subscribers', List[Subscriber]),
                              ('manager', Uploader)])

    def __init__(self):
        self._store = dict()
        self._lock = threading.Lock()

    def _add_subject_to_store(self, subject_name: str) -> None:
        if subject_name in self._store:
            return
        manager = Uploader()  # this is in case the AffiliateManager wanted to push to a subject by itself
        self._store[subject_name] = AffiliateManager._Affiliates(uploaders=[], subscribers=[], manager=manager)

    def bind_subscribe_to_subject(self, subject_name: str, subscriber: Subscriber) -> None:
        """Make a subscriber get notified whenever an event is dispatched to this subject."""
        subject_name = str(subject_name)
        with self._lock:
            self._add_subject_to_store(subject_name)  # make sure subject already in store
            affiliates = self._store[subject_name]
            affiliates.subscribers.append(subscriber)  # register as new subscriber to subject
            # notify every uploader to start notifying subscriber
            for uploader in affiliates.uploaders:
                subscriber.subscribe_to(uploader, uploader_name=subject_name)
            subscriber.subscribe_to(affiliates.manager, uploader_name=subject_name)

    def get_subscriber_for(self, subject_name: str) -> Subscriber:
        """Creates and Returns a new subscriber that is subscriber to the specified subject"""
        new_subscriber = Subscriber()
        self.bind_subscribe_to_subject(subject_name, new_subscriber)
        return new_subscriber

    def bind_uploader_to_subject(self, subject_name: str, uploader: Uploader) -> None:
        """Make a all dispatches from this uploader go to the subscribers of the given subject."""
        subject_name = str(subject_name)
        with self._lock:
            self._add_subject_to_store(subject_name)  # make sure subject already in store
            affiliates = self._store[subject_name]
            affiliates.uploaders.append(uploader)  # register as new uploader to subject
            # notify every subscriber to start listening uploader
            for subscriber in affiliates.subscribers:
                subscriber.subscribe_to(uploader, uploader_name=subject_name)

    def dispatch_to(self, subject_name: str, obj: Any = None) -> None:
        """Dispatch an event to all subscribers of a given subject"""
        subject_name = str(subject_name)
        if subject_name not in self._store:
            return
        self._store[subject_name].manager.dispatch(obj)
