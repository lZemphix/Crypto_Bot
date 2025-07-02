from client.bases import GatekeeperBase
from utils.gatekeeper import Gatekeeper

# DONT USED


class LapsManager(GatekeeperBase):
    def __init__(self):
        super().__init__()
        self.gatekeeper = Gatekeeper()

    def get(self):
        temp = self.get_temp()
        return temp.get("laps")

    def clear(self):
        self.gatekeeper.update(laps=0)
        return True

    def add_one(self):
        laps = self.get()
        self.gatekeeper.update(laps=laps + 1)
        return True
