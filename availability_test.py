import asyncio
import aiohttp
import time
import subprocess

total_requests = 0
total_successes = 0
uptime_total = 0


def get_minikube_ip():
    """
    Получение IP-адреса Minikube с помощью команды `minikube ip`.
    """
    try:
        result = subprocess.check_output(["minikube", "ip"], text=True).strip()
        return result
    except subprocess.CalledProcessError as e:
        print(f"Ошибка при получении IP-адреса Minikube: {e}")
        return None


async def make_load_test(host: str, session: aiohttp.ClientSession):
    """
    Function for ddosing host specified with result saving
    :param session:
    :param host:
    :return:
    """

    requests_made = 0
    successes = 0
    uptime = 0

    while True:
        try:
            requests_made += 1
            last_attempt = time.time_ns()

            async with session.get(host) as response:
                await response.text()
                if response.ok:
                    successes += 1
                    uptime = uptime + time.time_ns() - last_attempt

        except asyncio.CancelledError:
            # print("Sync results")
            global total_requests
            global total_successes
            global uptime_total
            total_requests += requests_made
            total_successes += successes
            uptime_total += uptime
            break
        except Exception as e:
            pass
            # print(f"{e}")


async def main(host: str, threads: int, experiment_time: int):
    """
    Entrypoint for start of the testing
    :return:
    """

    tasks = []

    timeouts = aiohttp.ClientTimeout(
        total=60, connect=15, sock_connect=15, sock_read=15
    )
    async with aiohttp.ClientSession(timeout=timeouts) as session:
        for i in range(threads):
            tasks.append(
                asyncio.create_task(
                    coro=make_load_test(host=host, session=session),
                    name=f"Task_{i}",
                )
            )

        await asyncio.sleep(experiment_time)

        for task in tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                print(f"{task.get_name()} was cancelled")

    # print(f"Availability time {total_successes * 100 / total_requests:.2f} %")
    print(f"{total_requests / experiment_time:.2f} requests/s")
    print(f"{(uptime_total/threads)*100 / (experiment_time*10**9) :.2f} % uptime")
    # print(total_requests)


# Получение IP Minikube
minikube_ip = get_minikube_ip()
if minikube_ip:
    asyncio.run(
        main(
            host=f"http://{minikube_ip}:31111/",
            threads=20,
            experiment_time=120,
        )
    )
else:
    print("Не удалось получить IP Minikube. Проверьте доступность команды `minikube ip`.")

