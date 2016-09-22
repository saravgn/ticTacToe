"""utils.py - File for collecting general utility functions."""

import logging
from google.appengine.ext import ndb
import endpoints


def get_by_urlsafe(urlsafe, model):
    """Returns an ndb.Model entity that the urlsafe key points to. Checks
        that the type of entity returned is of the correct kind. Raises an
        error if the key String is malformed or the entity is of the incorrect
        kind
    Args:
        urlsafe: A urlsafe key string
        model: The expected entity kind
    Returns:
        The entity that the urlsafe Key string points to or None if no entity
        exists.
    Raises:
        ValueError:"""
    try:
        key = ndb.Key(urlsafe=urlsafe)
    except TypeError:
        raise endpoints.BadRequestException('Invalid Key')
    except Exception, e:
        if e.__class__.__name__ == 'ProtocolBufferDecodeError':
            raise endpoints.BadRequestException('Invalid Key')
        else:
            raise

    entity = key.get()
    if not entity:
        return None
    if not isinstance(entity, model):
        raise ValueError('Incorrect Kind')
    return entity


def boolFullCurrentBoard(currentBoard):
    # Check if the currentBoard is full
    for item in currentBoard:
        if not item:
            return False
    return True


def sameSigns(array):
    # Same signs on the array
    return all(x == array[0] for x in array)


def lookForWin(currentBoard, size=3):
    # Check all signs on DIAGONALS, ROWS AND COLUMNS
    for i in range(size):
        if currentBoard[i]:
            if sameSigns(currentBoard[i:size * size:size]):
                return currentBoard[i]

    for i in range(size):
        if currentBoard[size * i]:
            if sameSigns(currentBoard[size * i:size * i + size]):
                return currentBoard[size * i]

    if currentBoard[0]:
        if sameSigns(currentBoard[0:size * size:size + 1]):
            return currentBoard[0]

    if currentBoard[size - 1]:
        if sameSigns(currentBoard[size - 1:size * (size - 1) + 1:size - 1]):
            return currentBoard[size - 1]
