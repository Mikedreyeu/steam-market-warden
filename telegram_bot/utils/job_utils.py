import pickle
from collections import defaultdict
from threading import Event
from time import time

from telegram_bot.constants import JOBS_PICKLE


def init_chat_data(chat_data):
    if not chat_data.get('timed_item_info_jobs'):
        chat_data['timed_item_info_jobs'] = defaultdict(list)
    if not chat_data.get('item_info_alert_jobs'):
        chat_data['item_info_alert_jobs'] = []


def load_jobs(jq):
    now = time()

    with open(JOBS_PICKLE, 'rb') as fp:
        while True:
            try:
                next_t, job = pickle.load(fp)
            except EOFError:
                break

            enabled = job._enabled
            removed = job._remove

            job._enabled = Event()
            job._remove = Event()

            if enabled:
                job._enabled.set()

            if removed:
                job._remove.set()

            next_t -= now

            jq._put(job, next_t)


def save_jobs(jq):
    if jq:
        job_tuples = jq._queue.queue
    else:
        job_tuples = []

    with open(JOBS_PICKLE, 'wb') as fp:
        for next_t, job in job_tuples:

            _job_queue = job._job_queue
            _remove = job._remove
            _enabled = job._enabled

            job._job_queue = None
            job._remove = job.removed
            job._enabled = job.enabled

            pickle.dump((next_t, job), fp)

            job._job_queue = _job_queue
            job._remove = _remove
            job._enabled = _enabled
