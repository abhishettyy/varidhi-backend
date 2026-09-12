"""Base schema compatibility layer: uses Pydantic when available, or stdlib fallback."""

import typing
from typing import Any, Callable, Dict, Optional

try:
    from pydantic import BaseModel as _PydanticBaseModel, Field as _PydanticField
    PYDANTIC_AVAILABLE = True

    class BaseModel(_PydanticBaseModel):
        pass

    Field = _PydanticField

except ImportError:
    PYDANTIC_AVAILABLE = False

    def _resolve_model_type(type_hint: Any) -> Optional[type]:
        """Resolves target BaseModel subclass from type hints (including Optional/Union)."""
        if isinstance(type_hint, type) and issubclass(type_hint, BaseModel):
            return type_hint
        origin = typing.get_origin(type_hint)
        if origin is typing.Union or (hasattr(typing, "UnionType") and origin is typing.UnionType):
            args = typing.get_args(type_hint)
            for arg in args:
                if isinstance(arg, type) and issubclass(arg, BaseModel):
                    return arg
        return None

    class BaseModel:
        """Lightweight stdlib fallback for BaseModel when pydantic is not installed."""

        def __init__(self, **kwargs):
            # Apply class-level defaults first
            for key, val in self.__class__.__dict__.items():
                if not key.startswith("_") and not callable(val):
                    setattr(self, key, val)
            
            # Resolve type annotations for nested BaseModel parsing
            annotations = getattr(self.__class__, "__annotations__", {})
            for key, val in kwargs.items():
                if isinstance(val, dict):
                    hint = annotations.get(key)
                    target_cls = _resolve_model_type(hint) if hint else None
                    if target_cls:
                        val = target_cls(**val)
                setattr(self, key, val)

        def model_dump(self) -> Dict[str, Any]:
            """Recursively dump model attributes to dictionary."""
            result = {}
            for k, v in self.__dict__.items():
                if k.startswith("_"):
                    continue
                if hasattr(v, "model_dump"):
                    result[k] = v.model_dump()
                elif isinstance(v, list):
                    result[k] = [
                        item.model_dump() if hasattr(item, "model_dump") else item
                        for item in v
                    ]
                elif isinstance(v, dict):
                    result[k] = {
                        dk: dv.model_dump() if hasattr(dv, "model_dump") else dv
                        for dk, dv in v.items()
                    }
                else:
                    result[k] = v
            return result

        @classmethod
        def model_validate(cls, obj: Any):
            """Validate and instantiate object from dictionary or instance."""
            if isinstance(obj, cls):
                return obj
            if isinstance(obj, dict):
                return cls(**obj)
            raise ValueError(f"Cannot validate {type(obj)} into {cls.__name__}")

        @classmethod
        def model_json_schema(cls) -> Dict[str, Any]:
            """Return minimal JSON schema representation."""
            return {"type": "object", "title": cls.__name__}

        def __repr__(self) -> str:
            attrs = ", ".join(f"{k}={v!r}" for k, v in self.__dict__.items() if not k.startswith("_"))
            return f"{self.__class__.__name__}({attrs})"

    def Field(
        default: Any = None,
        default_factory: Optional[Callable[[], Any]] = None,
        description: Optional[str] = None,
        **kwargs
    ) -> Any:
        """Fallback Field specifier."""
        if default_factory is not None:
            return default_factory()
        return default
