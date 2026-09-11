"""Base schema compatibility layer: uses Pydantic when available, or stdlib fallback."""

from typing import Any, Callable, Dict, Optional

try:
    from pydantic import BaseModel as _PydanticBaseModel, Field as _PydanticField
    PYDANTIC_AVAILABLE = True

    class BaseModel(_PydanticBaseModel):
        pass

    Field = _PydanticField

except ImportError:
    PYDANTIC_AVAILABLE = False

    class BaseModel:
        """Lightweight stdlib fallback for BaseModel when pydantic is not installed."""

        def __init__(self, **kwargs):
            # Apply class-level defaults first
            for key, val in self.__class__.__dict__.items():
                if not key.startswith("_") and not callable(val):
                    setattr(self, key, val)
            # Apply passed kwargs
            for key, val in kwargs.items():
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
