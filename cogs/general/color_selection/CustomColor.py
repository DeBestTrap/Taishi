import json
import os
from typing import Dict, List, Union

class CustomColor():
    def __init__(self, name:str, hexcode:int, emoji:str = None, role_id:int = None):
        self.name = name
        self.hexcode = hexcode
        self.emoji = emoji
        self.role_id =role_id 
    
    def set_role_id(self, role_id:int) -> None:
        self.role_id = role_id

    def __eq__(self, other:"CustomColor") -> bool:
        return self.name == other.name

    def get_dict(self) -> Dict[str, Union[str, int]]:
        d = dict()
        d["name"] = self.name
        d["hexcode"] = self.hexcode
        d["emoji"] = self.emoji
        d["role_id"] = self.role_id
        return d

    def from_dict(d:Dict[str, Union[str, int]]) -> "CustomColor":
        return CustomColor(name=d["name"], hexcode=d["hexcode"], emoji=d["emoji"], role_id=d["role_id"])
    
    def fetch_colors(guild_id:int) -> List["CustomColor"]:
        if not os.path.exists(f"server_data/{guild_id}/color_selection.json"):
            return []

        with open(f"server_data/{guild_id}/color_selection.json", "r") as f:
            data = json.load(f)
            colors = list(map(lambda x: CustomColor.from_dict(x), data["colors"]))
        return colors
    
    def __str__(self) -> str:
        return f"{self.emoji} {self.name}: {self.hexcode:06X} ({self.role_id})"
    
    def __repr__(self) -> str:
        return self.__str__()