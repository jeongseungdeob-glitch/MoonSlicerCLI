def chunk_list(seq, size):
    """Yield successive size-sized chunks from seq."""
    for i in range(0, len(seq), size):
        yield seq[i : i + size]