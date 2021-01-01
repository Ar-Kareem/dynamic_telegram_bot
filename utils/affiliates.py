from __future__ import annotations

import threading
from typing import List, NamedTuple, Type, Union
from abc import ABC, abstractmethod


class BaseAction(ABC):
    @property
    @abstractmethod
    def name(self) -> str:
        """:return: the name of the action"""
    @property
    def payload(self) -> any:
        """:return: the payload of the action"""


class TestAction(BaseAction):
    name = '[BaseAction] TestAction'
    payload = 123
    def __repr__(self):
        return str(self.payload)

class Subscriber:
    def __init__(self, store: Store):
        self.store = store # user Weakref here
        self._condmutex = threading.Condition()
        self._feed: List[BaseAction] = []

    def consume(self, timeout=None) -> Union[BaseAction, None]:
        """Consumes the top action in the feed. If no action then blocks until an action is received or timeout"""
        with self._condmutex:
            new_item = self._wait_for_event(timeout)
            if new_item:
                return self._feed.pop(0)
            else:
                return None

    def subscribe_to(self, action: Type[BaseAction], history: bool = True) -> Subscriber:
        """Start getting notified whenever this action is dispatched to the store. Returns self"""
        self.store._bind_subscriber_to_action(self, action, history)
        return self

    def _wait_for_event(self, timeout=None) -> bool:
        """blocks until an action arrives in the feed or timeout length. Returns False if timeout occurred"""
        wait_for_timeout = timeout if timeout is not None else threading.TIMEOUT_MAX
        while True:
            # will wait for 49 days but add a while loop just in case an event takes even longer to come
            flag = self._condmutex.wait_for(lambda: len(self._feed) > 0, wait_for_timeout)
            if flag or timeout is not None:
                return flag

    def _new_upload(self, data: BaseAction) -> None:
        """Used to add a new action to the feed and notify a single waiter"""
        with self._condmutex:
            self._feed.append(data)
            self._condmutex.notify(n=1)

    def check_feed_action_name(self, action_name: str) -> bool:
        """Checks whether the feed contains the specified action by name"""
        for e in self._feed:
            if e.name == action_name:
                return True
        return False

    def check_feed_action_type(self, action_type: Type[BaseAction]) -> bool:
        """Checks whether the feed contains the specified action or any of its subclassed action by type"""
        for e in self._feed:
            if isinstance(e, action_type):
                return True
        return False


class Store:
    _Shelf = NamedTuple('Shelf',
                        [('subscribers', List[Subscriber]),
                         ('history', List[BaseAction]),
                         ('lock', threading.Lock)])

    def __init__(self):
        self._store: dict[str, Store._Shelf] = dict()
        self._lock = threading.Lock()

    def get_new_subscriber(self) -> Subscriber:
        """Return a brand new subscriber that belongs to this store."""
        return Subscriber(store=self)

    def _register_new_action(self, action_name: str) -> None:
        """Instantiates the key:value pair for a new action. Does nothing if action already exists in this store"""
        if action_name in self._store:
            return
        with self._lock:
            if action_name not in self._store:
                self._store[action_name] = Store._Shelf(subscribers=[], history=[], lock=threading.Lock())

    def _bind_subscriber_to_action(self, subscriber: Subscriber, action: Type[BaseAction],
                                   include_history: bool = True) -> None:
        """Make a subscriber get notified whenever an event is dispatched to this subject."""
        assert issubclass(action, BaseAction), "Expected subclass of BaseAction, got " + str(type(action))
        assert isinstance(action.name, str), "Expected action.name to be of type str (Maybe you gave BaseAction class?)"
        assert not isinstance(action, BaseAction), "Expected type of BaseAction not an actual instance"
        action_name = str(action.name)
        self._register_new_action(action_name)  # make sure action already in store
        shelf = self._store[action_name]
        with shelf.lock:  # lock for editing shelf
            shelf.subscribers.append(subscriber) # user weakref here
            if include_history:
                for past_action in shelf.history:
                    subscriber._new_upload(past_action)

    def dispatch(self, action: BaseAction) -> None:
        """Dispatch an event to all subscribers of a given subject"""
        self._register_new_action(action.name)  # make sure action already in store
        shelf = self._store[action.name]
        with shelf.lock:  # lock for editing shelf
            for subscriber in shelf.subscribers:
                subscriber._new_upload(action)
            shelf.history.append(action)
