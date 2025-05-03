from abc import abstractmethod
from typing import Any, Dict, List, Optional

from pydantic import Field
from pydantic.dataclasses import dataclass

from chainlit.types import InputWidgetType
from chainlit.input_widget import InputWidget

@dataclass
class MCPServerSetting(InputWidget):
    """Useful to create a multi-input widget."""

    type: InputWidgetType = "mcpinput"
    initial: Optional[str] = None
    name: Optional[str] = None
    url: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        print("MCPServerSetting to_dict called")
        return {
            "type": self.type,
            "id": self.id,
            "label": self.label,
            "name": self.name,
            "url": self.url,
            "initial": self.initial,
            "tooltip": self.tooltip,
            "description": self.description,
        }