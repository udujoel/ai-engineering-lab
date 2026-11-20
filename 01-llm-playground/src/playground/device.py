"""Pick where PyTorch runs: the Apple GPU (mps) when available, otherwise the CPU.

Every module that runs a model asks this one function, so the choice is made in one place.
Set PLAYGROUND_DEVICE=cpu (or mps) in .env or the shell to override it, which helps when
checking whether an odd result comes from the GPU backend.
"""

import os

import torch

VALID_DEVICES = {"mps", "cpu"}


def pick_device() -> torch.device:
    override = os.getenv("PLAYGROUND_DEVICE", "").strip().lower()
    if override:
        if override not in VALID_DEVICES:
            raise ValueError(
                f"PLAYGROUND_DEVICE={override!r} is not valid, use one of {sorted(VALID_DEVICES)}"
            )
        if override == "mps" and not torch.backends.mps.is_available():
            raise RuntimeError("PLAYGROUND_DEVICE=mps was requested but MPS is not available")
        return torch.device(override)

    if torch.backends.mps.is_available():
        return torch.device("mps")
    return torch.device("cpu")
