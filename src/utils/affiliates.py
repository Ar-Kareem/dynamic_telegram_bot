from __future__ import annotations

import threading
from typing import List, NamedTuple, Type, Union, Tuple, Callable, Optional
from abc import ABC

import logging
logger = logging.getLogger(__name__)


class BaseAction(ABC):
    pass


class ChildAction(BaseAction):
    pass


# noinspection PyProtectedMember
class Subscriber:
    def __init__(self, store: Store):
        self._store = store
        self._cond_mutex = threading.Condition()
        self._feed: List[BaseAction] = []
        self._subscribed_action: List[Type[BaseAction]] = []  # list of subbed to actions for checking sub/parents

    def consume(self, timeout=None) -> Union[BaseAction, None]:
        """Consumes the top action in the feed. If no action then blocks until an action is received or timeout"""
        with self._cond_mutex:
            new_item = self._wait_for_event(timeout)
            if new_item:
                return self._feed.pop(0)
            else:
                return None

    def subscribe_to(self, action: Type[BaseAction], history: bool = True) -> Subscriber:
        """Start getting notified whenever this action is dispatched to the store. Returns self"""
        with self._cond_mutex:
            if action in self._subscribed_action:
                logger.warning('Attempting to subscribe to action that has already been subscribed to.')
                return self
            for t in self._subscribed_action:
                if issubclass(action, t) or issubclass(t, action):
                    logger.warning('Attempting to subscribe to action that is a parent/child of an already subscribed '
                                   'action. This behavior is not supported. Exiting subscribe')
                    return self
            self._subscribed_action.append(action)
        self._store._bind_subscriber_to_action(self, action, history)
        return self

    def _wait_for_event(self, timeout=None) -> bool:
        """blocks until an action arrives in the feed or timeout length. Returns False if timeout occurred"""
        wait_for_timeout = timeout if timeout is not None else threading.TIMEOUT_MAX
        while True:
            # will wait for 49 days but add a while loop just in case an event takes even longer to come
            flag = self._cond_mutex.wait_for(lambda: len(self._feed) > 0, wait_for_timeout)
            if flag or timeout is not None:
                return flag

    def _new_upload(self, data: BaseAction) -> None:
        """Used to add a new action to the feed and notify a single waiter"""
        with self._cond_mutex:
            self._feed.append(data)
            self._cond_mutex.notify(n=1)

    def check_feed_action(self, action_type: Union[Type[BaseAction], List[Type[BaseAction]]]) -> bool:
        """Checks whether the feed contains the specified action or any of its subclassed action by type"""
        for e in self._feed:
            if isinstance(e, action_type):
                return True
        return False


# noinspection PyProtectedMember
class Store:
    _Shelf = NamedTuple('Shelf',
                        [('subscribers', List[Subscriber]),
                         ('history', List[BaseAction]),
                         ('lock', threading.Lock)])

    def __init__(self):
        self._store: dict[type, Store._Shelf] = dict()
        self._lock = threading.Lock()

    def get_new_subscriber(self) -> Subscriber:
        """Return a brand new subscriber that belongs to this store."""
        return Subscriber(store=self)

    def _register_new_action_type(self, action_type: Type[BaseAction]) -> None:
        """Instantiates the key:value pair for a new action. Does nothing if action already exists in this store"""
        if action_type in self._store:
            return
        with self._lock:
            for t in action_type.mro():  # go through mro and register all
                if t not in self._store:
                    self._store[t] = Store._Shelf(subscribers=[], history=[], lock=threading.Lock())

    def _bind_subscriber_to_action(self, subscriber: Subscriber, action_type: Type[BaseAction],
                                   include_history: bool = True) -> None:
        """Make a subscriber get notified whenever an event is dispatched to this subject."""
        assert issubclass(action_type, BaseAction), "Expected subclass of BaseAction, got: " + str(action_type)
        self._register_new_action_type(action_type)  # make sure action already in store
        if not include_history:  # simple case
            self._store[action_type].subscribers.append(subscriber)
            return
        # complicated case, need to make sure history of all children in sync with new subscriber
        with self._lock:  # make sure no new actions are registered while locking all children actions
            children_shelves = [shelf for shelf_action_type, shelf in self._store.items()
                                if issubclass(shelf_action_type, action_type)]
            for shelf in children_shelves:  # lock all children
                shelf.lock.acquire()
            # all children locked, now its safe to add subscriber to the list and append all children histories
            self._store[action_type].subscribers.append(subscriber)
        for shelf in children_shelves:
            for past_action in shelf.history:
                subscriber._new_upload(past_action)
        for shelf in children_shelves:  # release all children
            shelf.lock.release()

    def dispatch(self, action: BaseAction) -> None:
        """Dispatch an event to all subscribers of a given action"""
        self._register_new_action_type(type(action))  # make sure action already in store
        shelf = self._store[type(action)]
        with shelf.lock:  # lock for editing shelf
            # add to history and notify all subscribers
            shelf.history.append(action)
            for subscriber in shelf.subscribers:
                subscriber._new_upload(action)
            # notify all parent subscribers
            parent_shelves = [self._store[parent] for parent in type(action).mro()[1:]]
            for parent_shelf in parent_shelves:
                for subscriber in parent_shelf.subscribers:
                    subscriber._new_upload(action)


# Define Types
BaseActionType = Type[BaseAction]
BaseActionTypeTuple = Union[BaseActionType, Tuple[BaseActionType, ...]]
Callback = Callable[[BaseAction], None]


class Reducer:
    def __init__(self, store: Store):
        self._subscriber = store.get_new_subscriber().subscribe_to(BaseAction, history=True)
        self._handlers: List[Tuple[BaseActionTypeTuple, Callback]] = []
        self._history: List[BaseAction] = []
        self._lock = threading.RLock()  # need RLock in case of register_handler is used while resolving _handle_action

    def register_handler(self, trigger: BaseActionTypeTuple, callback: Callback) -> None:
        with self._lock:
            for action in self._history:
                if isinstance(action, trigger):
                    # noinspection PyBroadException
                    try:
                        callback(action)
                    except Exception:
                        logger.exception('Exception occurred while handling reducer for: ' + str(callback))
            self._handlers.append((trigger, callback))

    def start(self, stop_action: BaseActionType = None) -> BaseAction:
        """This is the main function for a reducer object which starts listening and handling actions"""
        while True:
            new_action = self._subscriber.consume()
            self._handle_action(new_action)
            if stop_action is not None and isinstance(new_action, stop_action):
                return new_action

    def _handle_action(self, new_action: Optional[BaseAction]) -> None:
        if new_action is None:
            return
        with self._lock:
            for trigger, callback in self._handlers:
                # noinspection PyBroadException
                try:
                    if isinstance(new_action, trigger):
                        callback(new_action)
                except Exception:
                    logger.exception('Exception occurred while handling reducer for: ' + str(callback))
            # only register to history after handlers are done.
            self._history.append(new_action)

    def start_non_blocking(self, stop_action: BaseActionType = None) -> threading.Thread:
        """This runs the start function in a separate thread"""
        t = threading.Thread(target=self.start, kwargs={'stop_action': stop_action})
        t.start()
        return t
