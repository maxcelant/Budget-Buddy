from typing import Optional, List
from datetime import date
from pydantic import BaseModel, field_validator


class TokenExchangeRequest(BaseModel):
    public_token: str


class AccessToken(BaseModel):
    access_token: str


class Location(BaseModel):
    address: Optional[str]
    city: Optional[str]
    region: Optional[str]
    postal_code: Optional[str]
    country: Optional[str]
    lat: Optional[float]
    lon: Optional[float]
    store_number: Optional[str]


class Transaction(BaseModel):
    account_id: str
    account_owner: Optional[str] = None
    amount: float
    category: List[str]
    date: str
    iso_currency_code: str
    location: Optional[Location] = None
    name: Optional[str] = None
    payment_channel: Optional[str] = None
