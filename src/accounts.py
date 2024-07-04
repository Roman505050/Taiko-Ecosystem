from src.utils.accountmanager import AccountManager
import settings

if __name__ == "__main__":
    manager = AccountManager(tag=settings.TAG)
    manager.run()