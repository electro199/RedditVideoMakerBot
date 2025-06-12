from pathlib import Path
from typing import Any, Dict, Optional, get_args, get_origin

import toml
from pydantic import BaseModel, ValidationError
from pydantic_core import PydanticUndefined
from rich.console import Console

from utils.config_model import Config
from utils.console import print_substep

console = Console()
config: dict  # autocomplete


def parse_value(raw: str, expected_type: type[Any] | None):
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


def prompt_recursive(
    obj: BaseModel, validation_errors: Optional[Dict[str, Any]] = None
) -> BaseModel:
    validation_errors = validation_errors or {}

    for field_name, field in obj.model_fields.items():
        field_value = getattr(obj, field_name, None)
        is_invalid = field_name in validation_errors
        is_missing = field_value in [None, [], {}]

        if hasattr(field.annotation, "model_fields"):
            nested_model = field_value or field.annotation.model_construct()

            field_err = validation_errors.get(field_name)
            nested_errors = field_err if isinstance(field_err, dict) else {}

            fixed_nested = prompt_recursive(nested_model, nested_errors)
            setattr(obj, field_name, fixed_nested)
            continue

        if not (is_invalid or is_missing):
            continue

        description = field.description or ""
        default_str = (
            f" (default: {field.default})" if not field.is_required() else "  "
        )
        prompt_msg = (
            f"🧩 {field_name}\n"
            f"   * {description}{default_str}\n"
            f"   - Required: {field.is_required()}\n"
            f"❓ Enter value >"
        )

        while True:
            user_input = input(prompt_msg).strip()
            if not user_input and field.is_required():
                print("⚠️ This field is required.")
                continue

            try:
                value_to_set = parse_value(user_input, field.annotation)
            except Exception as e:
                print(f"⚠️ Invalid input: {e}")
                continue

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


def get_config(config_file: str) -> Dict[str, Any]:
    try:
        config_dict = toml.load(config_file)
    except Exception as e:
        console.print(f"[red]Failed to load config {config_file}: {e}[/red]")
        config_dict = {}

    try:
        config_instance = Config.model_validate(config_dict)
        return config_instance.model_dump()
    except ValidationError as e:
        console.print(
            "[yellow]Config validation failed, prompting for missing/invalid fields...[/yellow]"
        )

        config_instance = Config.model_construct()
        for k, v in config_dict.items():
            if hasattr(config_instance, k):
                setattr(config_instance, k, v)

        validation_tree = {}
        for error in e.errors():
            path = error["loc"]
            current = validation_tree
            for part in path[:-1]:
                current = current.setdefault(part, {})
            current[path[-1]] = error["msg"]

        config_instance = prompt_recursive(config_instance, validation_tree)
        config_instance = Config.model_validate(
            config_instance.model_dump(mode="python")
        )

        print(config_instance.reddit.creds.password)
        with open(config_file, "w", encoding="utf-8") as f:
            toml.dump(config_instance.model_dump(mode="python"), f)
        console.print(f"[green]Updated config saved to {config_file}[/green]")

        return config_instance.model_dump()


if __name__ == "__main__":
    directory = Path().absolute()
    get_config("config.toml")
