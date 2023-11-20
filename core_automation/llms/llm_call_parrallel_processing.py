import asyncio
from collections import deque
from datetime import datetime, timedelta


class LlmCallParallelProcessing:
    def __init__(
        self,
        llm_calls: list[callable],
        request_times: deque[float] = [],
        rate_limit: int = 60,
        timeout: int = 3600,
    ):
        self.request_times = request_times
        self.queue = self.create_queue(llm_calls)
        self._rate_limit = rate_limit
        self._result = {}
        self._timeout = timeout

    async def retryable_call(self, llm_call: callable):
        return await llm_call()

    async def worker(self):
        while True:
            index, llm_call = await self.queue.get()
            await self.handle_rate_limit()
            res = await self.retryable_call(llm_call)
            self.queue.task_done()
            self._result = {**self._result, **{index: res}}

    async def handle_rate_limit(self):
        self.request_times.append(datetime.now())
        self.request_times = [
            time
            for time in self.request_times
            if time > datetime.now() - timedelta(hours=1)
        ]

        if len(self.request_times) >= self._rate_limit:
            await asyncio.sleep(
                3600 - (datetime.now() - self.request_times.popleft()).total_seconds()
            )

    async def start_workers(self):
        return [asyncio.create_task(self.worker()) for _ in range(self._rate_limit)]

    async def close_workers(self, workers: list[asyncio.Task]):
        return [worker.cancel() for worker in workers]

    async def run(self):
        workers = await self.start_workers()
        await asyncio.wait_for(self.queue.join(), timeout=self._timeout)
        await self.close_workers(workers)
        return [value for _, value in sorted(self._result.items())]

    def create_queue(self, callables: list[callable]):
        queue = asyncio.Queue()
        for index, call in enumerate(callables):
            queue.put_nowait((index, call))
        return queue
