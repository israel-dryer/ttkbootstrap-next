from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Optional
import time
import tkinter as tk


@dataclass(eq=False)
class Job:
    """Handle for a scheduled task."""
    owner: tk.Misc
    after_id: Optional[str]
    active: bool = True

    def cancel(self) -> None:
        if not self.active:
            return
        try:
            if self.after_id is not None:
                self.owner.after_cancel(self.after_id)
        except Exception:
            pass
        finally:
            self.after_id = None
            self.active = False

    def __bool__(self) -> bool:  # truthy while active
        return self.active


class Schedule:
    """
    Tiny wrapper around Tk's after/after_idle with a clean API:

        .after(ms, fn, *a, **k)     # one-shot
        .idle(fn, *a, **k)          # run after current events
        .at(dt, fn, *a, **k)        # absolute time
        .interval(ms, fn, *a, **k)  # repeating
        .cancel(job)                # cancel one
        .cancel_all()               # cancel everything anchored here

    All jobs auto-cancel on owner <Destroy>.
    """
    __slots__ = ("owner", "_jobs")

    def __init__(self, owner: tk.Misc) -> None:
        self.owner = owner
        self._jobs: set[Job] = set()
        try:
            owner.bind("<Destroy>", self._on_destroy, add=True)
        except Exception:
            pass

    # ---------------- core ----------------

    def after(self, ms: int, fn: Callable, *args, **kwargs) -> Job:
        """Run once after `ms` milliseconds."""
        ms = max(0, int(ms))
        job = Job(self.owner, None)

        def run(*_args: object):
            job.after_id = None
            if job.active:
                job.active = False
                try:
                    fn(*args, **kwargs)
                finally:
                    self._jobs.discard(job)

        job.after_id = self.owner.after(ms, run)
        self._jobs.add(job)
        return job

    def idle(self, fn: Callable, *args, **kwargs) -> Job:
        """Run once when Tk is idle (after current event processing)."""
        job = Job(self.owner, None)

        def run():
            job.after_id = None
            if job.active:
                job.active = False
                try:
                    fn(*args, **kwargs)
                finally:
                    self._jobs.discard(job)

        job.after_id = self.owner.after_idle(run)
        self._jobs.add(job)
        return job

    def at(self, when: datetime, fn: Callable, *args, **kwargs) -> Job:
        """Run once at an absolute datetime."""
        delay_ms = max(0, int((when - datetime.now()).total_seconds() * 1000))
        return self.after(delay_ms, fn, *args, **kwargs)

    def interval(self, ms: int, fn: Callable, *args, **kwargs) -> Job:
        """
        Repeat every `ms` milliseconds (until cancelled). Attempts to compensate
        for callback time to reduce drift.
        """
        period = max(1, int(ms))
        job = Job(self.owner, None)

        def tick():
            if not job.active:
                return
            start = time.perf_counter()
            try:
                fn(*args, **kwargs)
            finally:
                elapsed = int((time.perf_counter() - start) * 1000)
                next_ms = max(0, period - elapsed)
                try:
                    job.after_id = self.owner.after(next_ms, tick)
                except Exception:
                    job.active = False
                    job.after_id = None
                    self._jobs.discard(job)

        job.after_id = self.owner.after(period, tick)
        self._jobs.add(job)
        return job

    def cancel(self, job: Optional[Job]) -> None:
        """Cancel a specific job."""
        if job is None:
            return
        job.cancel()
        self._jobs.discard(job)

    def cancel_all(self) -> None:
        """Cancel all jobs created by this Schedule."""
        for j in list(self._jobs):
            try:
                j.cancel()
            except Exception:
                pass
        self._jobs.clear()

    # ------------- internal -------------

    def _on_destroy(self, *_):
        self.cancel_all()
