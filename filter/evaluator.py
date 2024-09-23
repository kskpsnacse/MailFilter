from typing import List, Union, Optional
from datetime import datetime
from filter import OperatorType, FieldDataType, FieldDTO, FilterDTO, MatchingType, ConditionDTO
from mail import MailDTO

def __compare_values(
    operator: OperatorType, field_value: Union[str, float], condition_values: list[Union[str, float]]
)-> bool :
    if isinstance(field_value, str) and operator == OperatorType.CONTAINS:
        if isinstance(condition_values[0], str) :
            return condition_values[0].lower() in field_value.lower()
    
    elif operator == OperatorType.NOT_EQUALS:
        return str(condition_values[0]).lower() != str(field_value).lower()
    
    elif isinstance(field_value, float) and operator == OperatorType.LESS_THAN:
        if isinstance(condition_values[0], float):
            return field_value < condition_values[0]
    
    elif isinstance(field_value, float) and operator == OperatorType.GREATER_THAN:
        if isinstance(condition_values[0], float):
            return field_value > condition_values[0]
    
    elif isinstance(field_value, float) and operator == OperatorType.BETWEEN:
        if isinstance(condition_values[0], float) and isinstance(condition_values[1], float):
            return condition_values[0] <= field_value <= condition_values[1]
    return False

def __resolve(field: FieldDTO, mail: MailDTO) -> Optional[str]:
    field_value = getattr(mail, field.name, None)
    if field_value is None:
        return None
    if isinstance(field_value, datetime):
        if field.data_type == FieldDataType.DATETIME:
            return field_value.isoformat()
        elif field.data_type == FieldDataType.DATE:
            return field_value.date().isoformat()
    return str(field_value)

def __evaluate_condition(
     condition: ConditionDTO, mail: MailDTO
) -> bool:
    field_value: Optional[str] = __resolve(condition.field, mail)
    if not field_value:
        return False
    condition_values: list[str] = condition.value
    operator: OperatorType = condition.operator
    field_data_type: FieldDataType = condition.field.data_type
    modified_field_value: Union[str, float]
    modified_condition_values: List[Union[str, float]]
    
    if field_data_type == FieldDataType.NUMERIC:
        modified_field_value = float(field_value)
        modified_condition_values = [float(value) for value in condition_values]
    elif field_data_type == FieldDataType.DATE:
        modified_field_value = datetime.combine(
            datetime.strptime(field_value, "%Y-%m-%d").date(), datetime.min.time()
        ).timestamp()
        modified_condition_values = [
            datetime.combine(datetime.strptime(value, "%Y-%m-%d").date(), datetime.min.time()).timestamp()
            for value in condition_values
        ]
    elif field_data_type == FieldDataType.DATETIME:
        modified_field_value = datetime.fromisoformat(field_value).timestamp()
        modified_condition_values = [
            datetime.fromisoformat(value).timestamp() for value in condition_values
        ]
    else:
        modified_field_value = field_value
        modified_condition_values = [value for value in condition_values]
    
    return __compare_values(operator, modified_field_value, modified_condition_values)
    
def evaluate(filter: FilterDTO, mail: MailDTO) -> bool:
    try:
        condition_results: list[bool] = [__evaluate_condition(condition, mail) for condition in filter.conditions]
        if filter.matching_type == MatchingType.ALL:
            return all(condition_results)
        return any(condition_results)
    except Exception as e:
        print(f"error in evaluate {e}")
        raise e
    