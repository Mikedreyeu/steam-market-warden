import pickle
from threading import Event
from time import time

from telegram.ext import Dispatcher, Job, JobQueue, CallbackContext

from telegram_bot.constants import JOBS_PICKLE, JOB_TO_CHAT_DATA_KEY, JOBS, \
    II_ALERT_JOBS, II_REPEATING_JOBS, II_DAILY_JOBS, II_TIMED_JOBS


def _add_job_to_chat_data(dispatcher: Dispatcher, job: Job):
    if job.name == 'save_jobs_job':
        return

    chat_id = job.context['chat_id']
    job_chat_data_key = JOB_TO_CHAT_DATA_KEY[job.name]

    init_jobs_dict_chat_data(dispatcher.chat_data[chat_id])

    dispatcher.chat_data[chat_id][JOBS][job_chat_data_key].append(job)


def init_jobs_dict_chat_data(chat_data: dict):
    if not chat_data.get(JOBS):
        chat_data[JOBS] = {}
        for key in (II_ALERT_JOBS, II_REPEATING_JOBS,
                    II_DAILY_JOBS, II_TIMED_JOBS):
            chat_data[JOBS][key] = []


def remove_job(context: CallbackContext, chat_id: int, job: Job):
    job_key = JOB_TO_CHAT_DATA_KEY[job.name]
    context._dispatcher.chat_data[chat_id][JOBS][job_key].remove(job)
    job.schedule_removal()


def load_jobs(dispatcher: Dispatcher, jq: JobQueue):
    now = time()

    with open(JOBS_PICKLE, 'rb') as file_jobs_pickle:
        while True:
            try:
                next_t, job = pickle.load(file_jobs_pickle)
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
            _add_job_to_chat_data(dispatcher, job)


def save_jobs(jq: JobQueue):
    if jq:
        job_tuples = jq._queue.queue
    else:
        job_tuples = []

    with open(JOBS_PICKLE, 'wb') as file_jobs_pickle:
        for next_t, job in job_tuples:

            _job_queue = job._job_queue
            _remove = job._remove
            _enabled = job._enabled

            job._job_queue = None
            job._remove = job.removed
            job._enabled = job.enabled

            pickle.dump((next_t, job), file_jobs_pickle)

            job._job_queue = _job_queue
            job._remove = _remove
            job._enabled = _enabled
