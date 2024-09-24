from enum import Enum
from typing import List, Any, Optional
from datetime import datetime
from dataclasses import dataclass
from dataclasses_json import dataclass_json
import json

from sqlalchemy import Integer, DateTime
from sqlalchemy.orm import Mapped
from sqlalchemy.testing.schema import mapped_column

from action import ActionType
from db import Base


class FieldDataType(Enum):
    STRING = "STRING"
    DATE = "DATE"
    DATETIME = "DATETIME"
    NUMERIC = "NUMERIC"

class OperatorType(Enum):
    CONTAINS = "CONTAINS"
    NOT_CONTAINS = "NOT_CONTAINS"
    NOT_EQUALS = "NOT_EQUALS"
    EQUALS = "EQUALS"
    LESS_THAN = "LESS_THAN"
    GREATER_THAN = "GREATER_THAN"
    BETWEEN = "BETWEEN"

__NUMERIC_OPERATORS = [
    OperatorType.LESS_THAN, OperatorType.NOT_EQUALS,
    OperatorType.BETWEEN, OperatorType.GREATER_THAN, OperatorType.EQUALS
]
DATA_TYPE_OPERATOR_MAP: dict[FieldDataType, list[OperatorType]] = {
    FieldDataType.STRING: [OperatorType.CONTAINS, OperatorType.NOT_EQUALS, OperatorType.NOT_CONTAINS, OperatorType.EQUALS],
    FieldDataType.DATE: __NUMERIC_OPERATORS,
    FieldDataType.DATETIME: __NUMERIC_OPERATORS,
    FieldDataType.NUMERIC: __NUMERIC_OPERATORS
}

class MatchingType(Enum):
    ALL = "ALL"
    ANY = "ANY"


class FilterScheduler(Base):
    __tablename__: str = 'filter_scheduler'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    last_run_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)

@dataclass_json
@dataclass
class FieldDTO:
    name: str
    display_name: str
    data_type: FieldDataType
    

@dataclass_json
@dataclass
class ConditionDTO:
    field: FieldDTO
    operator: OperatorType
    value: list[str]
    
    def is_valid(self) -> bool:
        data_type: FieldDataType = self.field.data_type
        try:
            if self.operator not in DATA_TYPE_OPERATOR_MAP[data_type]:
                raise ValueError(f"Operator {self.operator} is not valid for field type {data_type}")
            if self.field.data_type == FieldDataType.NUMERIC:
                [float(v) for v in self.value]
            elif data_type == FieldDataType.DATE:
                [datetime.strptime(v, "%Y-%m-%d").date() for v in self.value]
            elif data_type == FieldDataType.DATETIME:
                [datetime.fromisoformat(v) for v in self.value] # "2023-01-01T00:00:00"
            if self.operator == OperatorType.BETWEEN and len(self.value) != 2:
                raise ValueError(f"BETWEEN operator requires exactly 2 values.")
            if self.operator != OperatorType.BETWEEN and len(self.value) > 1:
                raise ValueError(f"Operator {self.operator} expects a single value, not a list.")
        except ValueError as e:
            print(f"Value parsing failed for {data_type}: {str(e)}")
            return False
        
        return True
    

@dataclass_json
@dataclass
class ActionJSONDTO:
    action_type: ActionType
    config: Optional[str] = None

    
@dataclass_json
@dataclass
class FilterDTO:
    matching_type: MatchingType
    conditions: list[ConditionDTO]
    actions: list[ActionJSONDTO]
    
    @classmethod
    def from_dict(cls, d: dict[str, str]) -> Any:...
    
    @classmethod
    def from_json(cls, a: str) -> Any: ...
    
    def is_valid(self) -> bool:
        return all([condition.is_valid() for condition in self.conditions])

def load_filters_from_json(file_path: str) -> List[FilterDTO]:
    with open(file_path, 'r') as file:
        json_data: dict = json.load(file)
        filters: List[FilterDTO] = [FilterDTO.from_json(json.dumps(filter_item)) for filter_item in json_data]  # Deserialize each item
    return filters

FILTER_LIST = [filter for filter in load_filters_from_json('filters.json') if filter.is_valid()]
print(FILTER_LIST)
print(f"Number of filter - {len(FILTER_LIST)}")