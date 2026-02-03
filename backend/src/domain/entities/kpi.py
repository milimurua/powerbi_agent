from dataclasses import dataclass
from typing import Literal, Optional

KPIOwner = Literal["system","user"]
KPIStatus= Literal["active", "inactive", "proposed"]

@dataclass(frozen=True) #lo hace inmutable
class KPI:
    id: str
    name: str
    description: str
    sql_template: str
    owner: KPIOwner
    status: KPIStatus