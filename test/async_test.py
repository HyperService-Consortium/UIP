import asyncio
import time
import random
start = time.time()


async def transact(x):
    print("Waiting:", x)
    await asyncio.sleep(x)
    return "Done after {}s".format(x)


def keyboardinput():
    res = []
    wt = time.time()
    waittime = 0
    for _ in range(3):
        query = random.random() # int(input())
        waittime += query
        res.append(transact(query))
        if time.time() - wt > 2:
            break
    return res, waittime + time.time() - wt


def run(num):
    cnt, waittime, wt = 0, 0, 0
    loop = asyncio.get_event_loop()

    while cnt < num:
        # tasks = keyboardinput()
        tasks, wt = keyboardinput()
        res = loop.run_until_complete(asyncio.wait(tasks))[0]
        waittime += wt
        for tasksres in res:
            print(tasksres.result())
        cnt += len(tasks)
    loop.close()
    return waittime


if __name__ == '__main__':
    compare_time = run(10)
    print(time.time() - start, compare_time)


'''
    Waiting: 1
    Waiting: 2
    Waiting: 4
    Task ret: Done after 1s
    Task ret: Done after 2s
    Task ret: Done after 4s
    Time: 4.001978397369385
    
    Process finished with exit code 0
'''
