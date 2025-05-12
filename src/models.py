"""
Data models for the London Theater Show Scraper.

This module contains the data structures used to represent
theater shows and their details.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, List, Optional


@dataclass
class TheaterShow:
    """Data class representing a theater show."""
    
    title: str
    venue: str
    url: str  # URL to the booking/details page
    
    # Dates
    performance_start_date: Optional[datetime] = None
    performance_end_date: Optional[datetime] = None
    member_sale_date: Optional[datetime] = None
    general_sale_date: Optional[datetime] = None
    
    # Additional details
    price_range: Optional[str] = None
    genre: Optional[str] = None
    description: Optional[str] = None
    
    # Metadata
    theater_id: str = ""  # Identifier for the theater (e.g., "national", "donmar")
    last_updated: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """
        Convert the TheaterShow object to a dictionary for storage.
        
        Returns:
            Dict: Dictionary representation of the show
        """
        return {
            "title": self.title,
            "venue": self.venue,
            "url": self.url,
            "performance_start_date": self.performance_start_date.isoformat() if self.performance_start_date else None,
            "performance_end_date": self.performance_end_date.isoformat() if self.performance_end_date else None,
            "member_sale_date": self.member_sale_date.isoformat() if self.member_sale_date else None,
            "general_sale_date": self.general_sale_date.isoformat() if self.general_sale_date else None,
            "price_range": self.price_range,
            "genre": self.genre,
            "description": self.description,
            "theater_id": self.theater_id,
            "last_updated": self.last_updated.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'TheaterShow':
        """
        Create a TheaterShow object from a dictionary.
        
        Args:
            data: Dictionary containing show data
            
        Returns:
            TheaterShow: A show object created from the dictionary
        """
        # Process date fields
        for date_field in ['performance_start_date', 'performance_end_date', 
                          'member_sale_date', 'general_sale_date', 'last_updated']:
            if data.get(date_field):
                try:
                    data[date_field] = datetime.fromisoformat(data[date_field])
                except (ValueError, TypeError):
                    data[date_field] = None
        
        return cls(**data)
