class MeetingNotFoundError(Exception):
    pass


class MeetingNotReadyError(Exception):
    pass


class MeetingHasNoAudioError(Exception):
    pass


class MeetingAlreadyProcessedError(Exception):
    pass