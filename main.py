def strip_special_chars(input_str: str) -> str:
    """
    Remove special characters from a string, leaving only alphanumeric characters.

    Args:
        input_str (str): The string to process.

    Returns:
        str: The processed string with only alphanumeric characters.
    """

    return ''.join(char for char in str(input_str) if char.isalnum())
