from enum import Enum

class AssetType(Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    FOREX = "forex"
    ETF = "etf"
    UNK = "unknown"
