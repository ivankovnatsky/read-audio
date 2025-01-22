import click


def percentage_type(value: str) -> int:
    """Custom type for percentage values that handles both '30' and '30%' formats."""
    try:
        # Strip % if present
        clean_value = value.strip().rstrip("%")
        percentage = int(clean_value)
        if not 1 <= percentage <= 100:
            raise ValueError("Percentage must be between 1 and 100")
        return percentage
    except ValueError as e:
        raise click.BadParameter(str(e))
