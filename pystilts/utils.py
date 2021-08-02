def format_flags(config, capitalise=True, float_precision=6):
    """
    Capitalise config keys.
    Convert pathlib.Path types to str
    Convert int to str
    Convert float to six decimal place string
    Convert tuple of int to comma-separated string
    Convert tuple of float to comma-sep string with six decimal places.
    Do nothing to string.
    """
    formatted_config = {}
    for param, value in config.items():
        if capitalise:
            key = param.upper()
        else:
            key = param
        if value is None:
            value = "None"
        if isinstance(value, str):
            formatted_config[key] = value
        elif isinstance(value, Path):
            formatted_config[key] = str(value) # if it's a pathlib Path, fix it for JSON later.
        elif isinstance(value, float):
            formatted_config[key] = f"{value:.{float_precision}f}"
        elif isinstance(value, int):
            formatted_config[key] = str(value)
        elif isinstance(value, SkyCoord):
            formatted_config[key] = f"{value.ra.value:.{float_precision}f},{value.dec.value:.{float_precision}f}"
        elif isinstance(value, tuple):
            if all(isinstance(x, int) for x in value):
                formatted_config[key] = ','.join(f"{x}" for x in value)
            elif all(isinstance(x, float) for x in value):
                formatted_config[key] = ','.join(f"{x:.{float_precision}f}" for x in value)
            else:
                raise ValueError(f"Don't know how to format type {type(value)} - check element types?")
        else:
            raise ValueError(f"Don't know how to format type {type(value)}")
    return formatted_config
