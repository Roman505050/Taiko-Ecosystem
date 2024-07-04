from src.utils import console
import settings
from src.modules.kodo_exchange import KodoExchange

import asyncio
import random

async def runner(func, params):
    func_instance = func(params)
    try:
        tx, info = await func_instance.get_tx()
    except Exception as e:
        console.clog(f"Error: {e}", 'red')
        return

    if tx is not None:
        status, hash = await func_instance.manager.send_tx(tx)
    else:
        console.clog(f"Transaction is not created. Error: {info}", 'red')
    await asyncio.sleep(random.randint(5, 30))

async def runner_without_send(func, params):
    func_instance = func(params)
    status, info = await func_instance.run()

    if status == 1:
        console.clog(f"{info} is successful", 'green')
    else:
        console.clog(f"Failed: {info}", 'red')
    await asyncio.sleep(random.randint(5, 30))


modules = {
    1: (KodoExchange, runner, settings.Params_KodoExchange, 'Kodo Exchange'),
}

def main():
    path_to_data = f'./program_data/{settings.TAG}/'
    console.logging_path_file = f"{path_to_data}/log.txt"

    console.openlog()
    console.clog("Choose module:")
    for key, value in modules.items():
        console.clog(f"{key}. {value[3]}")

    while True:
        try:
            choice = int(console.cinput("Enter number: "))
        except:
            console.clog("Wrong number", 'red')
            continue
        # Validate choice if it is in modules
        if choice in modules.keys():
            break
        else:
            console.clog("Wrong number", 'red')
    console.clog(f"Your choice: {choice}")
    password = console.cgetpass("Enter password: ")
    if choice in modules.keys():
        if settings.SHUFFLE_ACCOUNTS:
            random.shuffle(settings.ACCOUNTS)
        for name_account in settings.ACCOUNTS:
            func, runner, params, name = modules[choice]
            params = params()
            params.name = name_account
            try:
                params.load(password)
            except Exception as e:
                console.clog(f"Incorrect password: {e}", 'red')
                while True:
                    new_password = console.cgetpass(f"Enter password for {name_account}: ")
                    if new_password == "cancel":
                        break
                    try:
                        params.load(new_password)
                        break
                    except Exception as e:
                        console.clog(f"Incorrect password: {e}", 'red')
                if new_password == "cancel":
                    console.clog(f"Account is skipped: {name_account}", 'yellow')
            # params.proxy = None
            asyncio.run(runner(func, params))
    else:
        console.clog("Wrong number", 'red')

    console.closelog()

if __name__ == '__main__':
    main()