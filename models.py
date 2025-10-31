"""Data models for the MDM system using Pydantic."""
from typing import Optional, List, Dict
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re

class Location(BaseModel):
    """Location/Address model."""
    location_id: str = Field(..., description="Unique location identifier")
    address: str
    city: str
    state: str
    zip_code: str
    country: str = "USA"
    location_type: Optional[str] = None  # practice, hospital, clinic
    
    @field_validator('zip_code')
    def validate_zip(cls, v):
        if not re.match(r'^\d{5}(-\d{4})?$', v):
            raise ValueError('Invalid ZIP code format')
        return v

class Specialty(BaseModel):
    """Medical specialty model."""
    specialty_code: str = Field(..., description="Unique specialty code")
    specialty_name: str
    specialty_type: str  # primary, secondary
    taxonomy_code: Optional[str] = None
    board_certified: bool = False
    certification_date: Optional[datetime] = None

class Credential(BaseModel):
    """Professional credential model."""
    credential_id: str = Field(..., description="Unique credential identifier")
    license_number: str
    license_type: str  # MD, DO, NP, PA, etc.
    license_state: str
    issue_date: datetime
    expiration_date: datetime
    status: str = "active"  # active, expired, suspended
    
    @field_validator('status')
    def validate_status(cls, v):
        valid_statuses = ['active', 'expired', 'suspended', 'revoked']
        if v not in valid_statuses:
            raise ValueError(f'Status must be one of {valid_statuses}')
        return v

class Affiliation(BaseModel):
    """Hospital/Organization affiliation model."""
    affiliation_id: str = Field(..., description="Unique affiliation identifier")
    organization_name: str
    organization_type: str  # hospital, medical_group, insurance
    relationship_type: str  # employed, affiliated, contracted
    start_date: datetime
    end_date: Optional[datetime] = None
    is_active: bool = True

class Provider(BaseModel):
    """Healthcare provider model."""
    npi: str = Field(..., description="10-digit National Provider Identifier")
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    suffix: Optional[str] = None
    email: Optional[str] = None
    phone: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    gender: Optional[str] = None
    
    # Status fields
    is_active: bool = True
    is_accepting_patients: bool = True
    
    # Audit fields
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    source_system: Optional[str] = None
    
    # MDM fields
    is_golden_record: bool = False
    master_record_id: Optional[str] = None
    confidence_score: Optional[float] = None
    
    @field_validator('npi')
    def validate_npi(cls, v):
        if not re.match(r'^\d{10}$', v):
            raise ValueError('NPI must be exactly 10 digits')
        return v
    
    @field_validator('email')
    def validate_email(cls, v):
        if v and not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', v):
            raise ValueError('Invalid email format')
        return v
    
    @field_validator('phone')
    def validate_phone(cls, v):
        if v and not re.match(r'^\+?1?\d{10,15}$', v):
            raise ValueError('Invalid phone format')
        return v

class ProviderComplete(Provider):
    """Complete provider model with all relationships."""
    locations: List[Location] = []
    specialties: List[Specialty] = []
    credentials: List[Credential] = []
    affiliations: List[Affiliation] = []

class MatchResult(BaseModel):
    """Model for match results between providers."""
    provider1_npi: str
    provider2_npi: str
    match_score: float
    match_type: str  # exact, high, medium, low
    matching_attributes: List[str]
    confidence_level: str
    recommended_action: str  # merge, review, ignore
    
class DataQualityResult(BaseModel):
    """Model for data quality check results."""
    provider_npi: str
    is_valid: bool
    issues: List[str] = []
    quality_score: float
    checked_at: datetime = Field(default_factory=datetime.now)

class MergeHistory(BaseModel):
    """Model for tracking merge history."""
    merge_id: str
    source_npi: str
    target_npi: str
    merged_by: str
    merged_at: datetime = Field(default_factory=datetime.now)
    merge_reason: str
    attributes_merged: List[str]
    is_reversed: bool = False
