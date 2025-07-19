from utils.gatekeeper import gatekeeper

# DONT USED


class LapsManager:
    def __init__(self):
        super().__init__()

    def get(self) -> int:
        temp = self.get_temp()
        return temp.get("laps")

    def clear(self) -> bool:
        gatekeeper.update(laps=0)
        return True

    def add_one(self) -> bool:
        laps = self.get()
        gatekeeper.update(laps=laps + 1)
        return True
