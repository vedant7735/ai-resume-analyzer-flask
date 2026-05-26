from backend.services.model_service.config.model_registry import MODEL_REGISTRY


def get_model_config(model_key: str):
    """
    Returns full model configuration.
    """

    if model_key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model key: {model_key}")

    return MODEL_REGISTRY[model_key]


def get_model_name(model_key: str):
    """
    Returns actual provider model name.
    """

    config = get_model_config(model_key)

    return config["model"]


def supports_vision(model_key: str):
    """
    Checks whether model supports image input.
    """

    config = get_model_config(model_key)

    return config["capabilities"].get("vision", False)


def supports_json_mode(model_key: str):
    """
    Checks JSON structured output support.
    """

    config = get_model_config(model_key)

    return config["capabilities"].get("json_mode", False)


def supports_streaming(model_key: str):
    """
    Checks streaming support.
    """

    config = get_model_config(model_key)

    return config["capabilities"].get("streaming", False)


def get_temperature(model_key: str):
    """
    Returns default model temperature.
    """

    config = get_model_config(model_key)

    return config.get("temperature", 0.0)


def get_max_tokens(model_key: str):
    """
    Returns configured max token limit.
    """

    config = get_model_config(model_key)

    return config.get("max_tokens", 1000)