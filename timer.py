import asyncio


class Timer:
    def __init__(self, timeout, callback):
        self._timeout = timeout
        self._callback = callback
        self._task = None

    async def _job(self):
        await asyncio.sleep(self._timeout)
        await self._callback()
        self._task = asyncio.create_task(self._job())

    async def cancel(self):
        if self._task is None:
            return

        self._task.cancel()

    async def start(self):
        if self._task:
            await self.cancel()

        self._task = asyncio.create_task(self._job())

    async def set_time(self, timeout):
        self._timeout = timeout
        await self.start()
