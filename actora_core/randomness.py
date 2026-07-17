"""Injected, serializable, and cross-runtime deterministic randomness.

The implementation deliberately does not wrap ``random.Random``.  Python's
stdlib random helpers are not a durable trace contract across CPython minor
versions, while Actora's native and browser runtimes may use different minors.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Any, MutableSequence, Protocol, Sequence, TypeVar, runtime_checkable

from .errors import ContractValidationError

T = TypeVar("T")

_UINT32_MASK = (1 << 32) - 1
_UINT64_MASK = (1 << 64) - 1
_PCG32_MULTIPLIER = 6364136223846793005
_DEFAULT_SEQUENCE = 54


def _normalize_seed(seed: int | str | bytes | bytearray) -> int:
    if isinstance(seed, bool):
        raise ContractValidationError("random seed must not be a boolean")
    if isinstance(seed, int):
        return seed & _UINT64_MASK
    if isinstance(seed, str):
        source = b"str\x00" + seed.encode("utf-8")
    elif isinstance(seed, (bytes, bytearray)):
        source = b"bytes\x00" + bytes(seed)
    else:
        raise ContractValidationError(
            "random seed must be an integer, string, or byte sequence"
        )
    digest = hashlib.sha256(source).digest()
    return int.from_bytes(digest[:8], byteorder="big", signed=False)


@dataclass(frozen=True, slots=True)
class RandomState:
    """Complete state for Actora's fully specified PCG32-v1 stream."""

    state: int
    increment: int
    algorithm: str = "pcg32-v1"

    def __post_init__(self) -> None:
        if self.algorithm != "pcg32-v1":
            raise ContractValidationError(
                f"Unsupported random-state algorithm '{self.algorithm}'"
            )
        if isinstance(self.state, bool) or not isinstance(self.state, int):
            raise ContractValidationError("rng.state must be an integer")
        if not 0 <= self.state <= _UINT64_MASK:
            raise ContractValidationError("rng.state must be an unsigned 64-bit integer")
        if isinstance(self.increment, bool) or not isinstance(self.increment, int):
            raise ContractValidationError("rng.increment must be an integer")
        if not 0 <= self.increment <= _UINT64_MASK:
            raise ContractValidationError(
                "rng.increment must be an unsigned 64-bit integer"
            )
        if self.increment % 2 == 0:
            raise ContractValidationError("rng.increment must be odd")

    @classmethod
    def from_dict(cls, data: object) -> "RandomState":
        if not isinstance(data, dict):
            raise ContractValidationError("rng must be an object")
        allowed_fields = {"algorithm", "state", "increment"}
        unknown_fields = sorted(
            str(field)
            for field in data
            if not isinstance(field, str) or field not in allowed_fields
        )
        if unknown_fields:
            raise ContractValidationError(
                "rng contains unknown fields: " + ", ".join(unknown_fields)
            )
        algorithm = data.get("algorithm", "pcg32-v1")
        if not isinstance(algorithm, str):
            raise ContractValidationError("rng.algorithm must be a string")
        state = cls._parse_uint64(data.get("state"), path="rng.state")
        increment = cls._parse_uint64(
            data.get("increment"),
            path="rng.increment",
        )
        return cls(
            state=state,
            increment=increment,
            algorithm=algorithm,
        )

    @staticmethod
    def _parse_uint64(value: object, *, path: str) -> int:
        # Hex strings are deliberate: JSON numbers cannot carry all uint64
        # values through JavaScript without precision loss.
        if not isinstance(value, str) or len(value) != 16:
            raise ContractValidationError(
                f"{path} must be a 16-character lowercase hexadecimal string"
            )
        if any(character not in "0123456789abcdef" for character in value):
            raise ContractValidationError(
                f"{path} must be a 16-character lowercase hexadecimal string"
            )
        return int(value, 16)

    def to_dict(self) -> dict[str, object]:
        return {
            "algorithm": self.algorithm,
            "state": f"{self.state:016x}",
            "increment": f"{self.increment:016x}",
        }


@runtime_checkable
class RandomSource(Protocol):
    """Minimum randomness API required by simulation code."""

    def random(self) -> float:
        ...

    def randint(self, a: int, b: int) -> int:
        ...

    def choice(self, values: Sequence[T]) -> T:
        ...

    def sample(self, population: Sequence[T], k: int) -> list[T]:
        ...

    def shuffle(self, values: MutableSequence[Any]) -> None:
        ...

    def snapshot(self) -> RandomState:
        ...


class SeededRandomSource:
    """Portable PCG32-v1 stream with Actora-owned selection algorithms.

    Algorithm contract:
    - PCG-XSH-RR 64/32 state transition and output permutation.
    - Integer seeds use their low 64 bits; text/byte seeds use the first
      64 bits of SHA-256 over a type-tagged payload.
    - The stream increment is ``((sequence mod 2^64) << 1 | 1) mod 2^64``.
    - ``random`` combines 27 and 26 random bits into a 53-bit fraction.
    - integer selection uses ``(upper_bound - 1).bit_length()`` rejection
      sampling; low bits are consumed first from each 32-bit output word.
    - ``sample`` uses a forward partial Fisher-Yates pass.
    - ``shuffle`` uses a reverse Fisher-Yates pass.

    These rules are part of the serialized ``pcg32-v1`` contract and must be
    mirrored exactly by any non-Python runtime.
    """

    def __init__(
        self,
        seed: int | str | bytes | bytearray = 0,
        *,
        sequence: int = _DEFAULT_SEQUENCE,
    ):
        if isinstance(sequence, bool) or not isinstance(sequence, int):
            raise ContractValidationError("random sequence must be an integer")
        seed_value = _normalize_seed(seed)
        self._state = 0
        self._increment = ((sequence & _UINT64_MASK) << 1 | 1) & _UINT64_MASK
        self._next_uint32()
        self._state = (self._state + seed_value) & _UINT64_MASK
        self._next_uint32()

    @classmethod
    def from_state(cls, state: RandomState) -> "SeededRandomSource":
        source = cls.__new__(cls)
        source._state = state.state
        source._increment = state.increment
        return source

    def _next_uint32(self) -> int:
        old_state = self._state
        self._state = (
            old_state * _PCG32_MULTIPLIER + self._increment
        ) & _UINT64_MASK
        xorshifted = (((old_state >> 18) ^ old_state) >> 27) & _UINT32_MASK
        rotation = (old_state >> 59) & 31
        return (
            (xorshifted >> rotation)
            | (xorshifted << ((-rotation) & 31))
        ) & _UINT32_MASK

    def _getrandbits(self, bit_count: int) -> int:
        if bit_count <= 0:
            return 0
        result = 0
        produced = 0
        while produced < bit_count:
            word = self._next_uint32()
            take = min(32, bit_count - produced)
            result |= (word & ((1 << take) - 1)) << produced
            produced += take
        return result

    def _randbelow(self, upper_bound: int) -> int:
        if isinstance(upper_bound, bool) or not isinstance(upper_bound, int):
            raise TypeError("upper_bound must be an integer")
        if upper_bound <= 0:
            raise ValueError("upper_bound must be positive")
        bit_count = (upper_bound - 1).bit_length()
        while True:
            candidate = self._getrandbits(bit_count)
            if candidate < upper_bound:
                return candidate

    def random(self) -> float:
        high = self._next_uint32() >> 5
        low = self._next_uint32() >> 6
        return (high * (1 << 26) + low) / float(1 << 53)

    def randint(self, a: int, b: int) -> int:
        if isinstance(a, bool) or isinstance(b, bool):
            raise TypeError("randint bounds must be integers")
        if not isinstance(a, int) or not isinstance(b, int):
            raise TypeError("randint bounds must be integers")
        if b < a:
            raise ValueError("empty range for randint")
        return a + self._randbelow(b - a + 1)

    def choice(self, values: Sequence[T]) -> T:
        if not values:
            raise IndexError("cannot choose from an empty sequence")
        return values[self._randbelow(len(values))]

    def sample(self, population: Sequence[T], k: int) -> list[T]:
        if isinstance(k, bool) or not isinstance(k, int):
            raise TypeError("sample size must be an integer")
        if k < 0 or k > len(population):
            raise ValueError("sample larger than population or is negative")
        pool = list(population)
        for index in range(k):
            selected_index = index + self._randbelow(len(pool) - index)
            pool[index], pool[selected_index] = pool[selected_index], pool[index]
        return pool[:k]

    def shuffle(self, values: MutableSequence[Any]) -> None:
        for index in range(len(values) - 1, 0, -1):
            selected_index = self._randbelow(index + 1)
            values[index], values[selected_index] = (
                values[selected_index],
                values[index],
            )

    def snapshot(self) -> RandomState:
        return RandomState(state=self._state, increment=self._increment)
