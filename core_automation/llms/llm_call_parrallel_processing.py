import asyncio
from datetime import datetime, timedelta

from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_random_exponential,
)


class LlmCallParallelProcessing:
    def __init__(
        self, llm_calls: list[callable], rate_limit: int = 60, timeout: int = 3600
    ):
        self.queue = self.create_queue(llm_calls)
        self.rate_limit = rate_limit
        self.request_times = []
        self._result = {}
        self._valid_nb_target = len(llm_calls)

    @retry(
        wait=wait_random_exponential(min=1, max=60),
        stop=stop_after_attempt(6),
        retry=retry_if_exception_type(TimeoutError),
    )
    async def worker(self):
        while True:
            index, llm_call = await self.queue.get()
            await self.handle_rate_limit()
            res = await llm_call()
            self.queue.task_done()
            self._result = {**self._result, **{index: res}}

    async def handle_rate_limit(self):
        self.request_times.append(datetime.now())
        self.request_times = [
            time
            for time in self.request_times
            if time > datetime.now() - timedelta(hours=1)
        ]

        if len(self.request_times) >= self.rate_limit:
            await asyncio.sleep(
                3600 - (datetime.now() - self.request_times[0]).total_seconds()
            )

    async def start_workers(self):
        for _ in range(self.rate_limit):
            asyncio.create_task(self.worker())

    def create_queue(self, callables: list[callable]):
        queue = asyncio.Queue()
        for index, call in enumerate(callables):
            queue.put_nowait((index, call))
        return queue

    def is_finished(self):
        return len(self._result.values()) >= self._valid_nb_target

    def get_result(self):
        return [value for _, value in sorted(self._result.items())]
