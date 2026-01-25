import asyncio
import websockets
import signal
import json
import queue
import time

from multiprocessing import Manager, Process

from judger import Judger, JudgeResult
from exceptions import JudgeServiceError


def judge(task, result_queue):
    try:
        Judger(task_id=task['task_id'],
               case_id=task['case_id'],
               spj_id=task['spj_id'],
               test_case_config=task['test_case_config'],
               subcheck_config=task['subcheck_config'],
               result_queue=result_queue).judge(
                   task['code'],
                   task['lang'],
                   task['limit'],
               )
    except JudgeServiceError as e:
        result_queue.put(
            Judger.make_report(status=JudgeResult.SYSTEM_ERROR,
                               score=0,
                               max_time=0,
                               max_memory=0,
                               log=str(e),
                               detail=[]))
    except Exception as e:
        result_queue.put(
            Judger.make_report(status=JudgeResult.SYSTEM_ERROR,
                               score=0,
                               max_time=0,
                               max_memory=0,
                               log=f'Unexpected error: {type(e).__name__}: {e}',
                               detail=[]))
    finally:
        result_queue.put(None)


async def handler(websocket):
    async for message in websocket:
        try:
            task = json.loads(message)
        except json.decoder.JSONDecodeError:
            print(f'Decode failed: {message}')
            continue
        manager = Manager()
        result_queue = manager.Queue()
        loop = asyncio.get_event_loop()

        proc = Process(target=judge, args=(task, result_queue), daemon=False)
        proc.start()
        start = time.monotonic()
        timeout = float(task.get('timeout', 0) or 0)
        if timeout <= 0:
            timeout = 300.0

        while True:
            if time.monotonic() - start > timeout:
                try:
                    proc.terminate()
                    proc.join(timeout=1)
                except Exception:
                    pass
                data = json.dumps(
                    Judger.make_report(status=JudgeResult.SYSTEM_ERROR,
                                       score=0,
                                       max_time=0,
                                       max_memory=0,
                                       log='Judge server task timeout',
                                       detail=[]))
                await websocket.send(data)
                break

            try:
                item = await loop.run_in_executor(
                    None, lambda: result_queue.get(timeout=1))
            except queue.Empty:
                if not proc.is_alive():
                    data = json.dumps(
                        Judger.make_report(status=JudgeResult.SYSTEM_ERROR,
                                           score=0,
                                           max_time=0,
                                           max_memory=0,
                                           log='Judge worker exited unexpectedly',
                                           detail=[]))
                    await websocket.send(data)
                    break
                continue

            if item is None:
                break
            data = json.dumps(item)
            await websocket.send(data)

        try:
            if proc.is_alive():
                proc.terminate()
                proc.join(timeout=1)
        finally:
            try:
                manager.shutdown()
            except Exception:
                pass


async def main():
    loop = asyncio.get_running_loop()
    stop = loop.create_future()
    # TODO: ?????
    # loop.add_signal_handler(signal.SIGTERM, stop.set_result, None)

    print("Listening on :8080")
    async with websockets.serve(handler, "", 8080):
        await stop
        print("SIGTERM received, exiting...")


if __name__ == "__main__":
    asyncio.run(main())
