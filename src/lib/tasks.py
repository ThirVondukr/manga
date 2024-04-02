import enum


class TaskStatus(enum.IntEnum):
    pending = 0
    done = 1
    error = 2
