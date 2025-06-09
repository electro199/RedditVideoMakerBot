from pathlib import Path
from typing import Any, Dict

import toml
from rich.console import Console

from utils.config_model import Config
from utils.console import print_substep

from typing import Any, get_args, get_origin

from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined

console = Console()
config: dict  # autocomplete

def prompt_recursive(obj: BaseModel):
    """
    Recursively prompt for missing or invalid fields in a Pydantic model instance 'obj'.
    """
    for field_name, field in obj.model_fields.items():
        value = getattr(obj, field_name, None)
        # If field is a nested BaseModel, recurse into it
        if hasattr(field.annotation, "model_fields"):
            nested_obj = value or field.annotation.model_construct()
            fixed_nested = prompt_recursive(nested_obj)
            setattr(obj, field_name, fixed_nested)
            continue

        # If the value is valid and not None, skip prompt
        if value not in [None, "", [], {}]:
            continue

        description = field.description or ""
        default_str = (
            f" (default: {field.default})"
            if (field.default is not None) or field.default == PydanticUndefined
            else ""
        )
        prompt_msg = f"🧩 {field_name}\n   📘 {description}{default_str}\n   ⚠️ Required: {field.is_required()}\n   ❓ Enter value: "

        while True:
            user_input = input(prompt_msg).strip()
            if not user_input:
                if field.default is not None:
                    value_to_set = field.default
                elif not field.is_required():
                    value_to_set = None
                else:
                    print("⚠️ This field is required.")
                    continue
            else:
                # Convert input based on type, you can expand this logic
                try:
                    value_to_set = parse_value(user_input, field.annotation)
                except Exception as e:
                    print(f"⚠️ Invalid input: {e}")
                    continue

            # Validate the assignment
            try:
                obj.__pydantic_validator__.validate_assignment(
                    obj, field_name, value_to_set
                )
                setattr(obj, field_name, value_to_set)
                break
            except ValidationError as ve:
                for err in ve.errors():
                    print(f"❌ {err['loc'][0]}: {err['msg']}")

    return obj


def parse_value(raw: str, expected_type: type):

    origin = get_origin(expected_type)
    args = get_args(expected_type)

    if expected_type == bool:
        if raw.lower() in ("true", "yes", "1"):
            return True
        elif raw.lower() in ("false", "no", "0"):
            return False
        else:
            raise ValueError("Expected boolean value (true/false)")
    elif expected_type == int:
        return int(raw)
    elif expected_type == float:
        return float(raw)
    elif expected_type == str:
        return raw
    elif origin == list and args:
        return [parse_value(x.strip(), args[0]) for x in raw.split(",")]
    else:
        raise ValueError(f"Unsupported field type: {expected_type}")


def check_toml(config_file: str) -> Dict[str, Any]:
    """
    Load the template and config TOML files.
    Validate config with Pydantic.
    If invalid, prompt for missing or invalid fields.
    Save fixed config back.
    Return the valid Config model.
    """
    try:
        config_dict = toml.load(config_file)
    except Exception as e:
        print(f"Failed to load config {config_file}: {e}")
        config_dict = {}

    try:
        config_instance = Config.model_validate(config_dict)
    except ValidationError as e:
        print("Config validation failed, will prompt for missing/invalid fields:")
        print(e)
        # Start from a clean model
        config_instance = Config.model_construct()
        # Update model with any valid partial data loaded from config
        for k, v in config_dict.items():
            if hasattr(config_instance, k):
                setattr(config_instance, k, v)

        # Prompt for missing or invalid fields recursively
        config_instance = prompt_recursive(config_instance)

        # Validate again to be sure
        config_instance = Config.model_validate(config_instance.model_dump())

        # Save fixed config back to file
        with open(config_file, "w", encoding="utf-8") as f:
            toml.dump(config_instance.model_dump(), f)
        print(f"Updated config saved to {config_file}")
        config = config_instance.model_dump()
    return config


if __name__ == "__main__":
    directory = Path().absolute()
    check_toml("config.toml")
