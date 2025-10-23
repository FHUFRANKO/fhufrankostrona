"""
Unit tests for validators
Run with: pytest backend/tests/test_validators.py -v
"""
import pytest
from datetime import date, datetime
from validators import (
    validate_vin,
    validate_url,
    validate_registration_number,
    validate_production_year,
    validate_first_registration_date,
    validate_price,
    validate_mileage,
    validate_seats,
    validate_engine_displacement,
    validate_power,
    validate_gvw,
    validate_string_length
)


class TestVINValidator:
    """Test VIN validation"""
    
    def test_valid_vin(self):
        """Test valid VIN numbers"""
        assert validate_vin("1HGBH41JXMN109186") == "1HGBH41JXMN109186"
        assert validate_vin("JH4KA8170MC000000") == "JH4KA8170MC000000"
        assert validate_vin("WVWZZZ3CZBE123456") == "WVWZZZ3CZBE123456"
    
    def test_vin_case_insensitive(self):
        """VIN should be converted to uppercase"""
        assert validate_vin("1hgbh41jxmn109186") == "1HGBH41JXMN109186"
        assert validate_vin("wvwzzz3czbe123456") == "WVWZZZ3CZBE123456"
    
    def test_vin_invalid_length(self):
        """VIN must be exactly 17 characters"""
        with pytest.raises(ValueError, match="dokładnie 17 znaków"):
            validate_vin("1HGBH41JXMN10918")  # 16 chars
        
        with pytest.raises(ValueError, match="dokładnie 17 znaków"):
            validate_vin("1HGBH41JXMN1091866")  # 18 chars
    
    def test_vin_invalid_characters(self):
        """VIN cannot contain I, O, Q"""
        with pytest.raises(ValueError, match="bez I, O, Q"):
            validate_vin("1HGBH41JXMN10918I")  # Contains I
        
        with pytest.raises(ValueError, match="bez I, O, Q"):
            validate_vin("1HGBH41JXMN10918O")  # Contains O
        
        with pytest.raises(ValueError, match="bez I, O, Q"):
            validate_vin("1HGBH41JXMN10918Q")  # Contains Q
    
    def test_vin_none_or_empty(self):
        """VIN can be None or empty"""
        assert validate_vin(None) is None
        assert validate_vin("") is None
        assert validate_vin("   ") is None


class TestURLValidator:
    """Test URL validation"""
    
    def test_valid_urls(self):
        """Test valid URLs"""
        assert validate_url("https://www.facebook.com/profile") == "https://www.facebook.com/profile"
        assert validate_url("http://example.com") == "http://example.com"
        assert validate_url("https://otomoto.pl/listing/123") == "https://otomoto.pl/listing/123"
    
    def test_invalid_url_no_protocol(self):
        """URL must have protocol"""
        with pytest.raises(ValueError, match="protokół"):
            validate_url("www.facebook.com")
        
        with pytest.raises(ValueError, match="protokół"):
            validate_url("facebook.com")
    
    def test_invalid_url_wrong_protocol(self):
        """URL must use http or https"""
        with pytest.raises(ValueError, match="http:// lub https://"):
            validate_url("ftp://example.com")
    
    def test_url_none_or_empty(self):
        """URL can be None or empty"""
        assert validate_url(None) is None
        assert validate_url("") is None


class TestRegistrationNumberValidator:
    """Test Polish registration number validation"""
    
    def test_valid_registration_numbers(self):
        """Test valid registration numbers"""
        assert validate_registration_number("WA 12345") == "WA 12345"
        assert validate_registration_number("KR-ABC-123") == "KR-ABC-123"
        assert validate_registration_number("VS-071-K") == "VS-071-K"
    
    def test_registration_case_insensitive(self):
        """Registration number should be converted to uppercase"""
        assert validate_registration_number("wa 12345") == "WA 12345"
        assert validate_registration_number("kr-abc-123") == "KR-ABC-123"
    
    def test_registration_invalid_length(self):
        """Registration number must be 3-15 characters"""
        with pytest.raises(ValueError, match="od 3 do 15 znaków"):
            validate_registration_number("AB")  # Too short
        
        with pytest.raises(ValueError, match="od 3 do 15 znaków"):
            validate_registration_number("ABCDEFGHIJKLMNOP")  # Too long
    
    def test_registration_none_or_empty(self):
        """Registration number can be None or empty"""
        assert validate_registration_number(None) is None
        assert validate_registration_number("") is None


class TestProductionYearValidator:
    """Test production year validation"""
    
    def test_valid_production_years(self):
        """Test valid production years"""
        current_year = datetime.now().year
        assert validate_production_year(2020) == 2020
        assert validate_production_year(1990) == 1990
        assert validate_production_year(current_year) == current_year
    
    def test_production_year_too_old(self):
        """Production year cannot be before 1950"""
        with pytest.raises(ValueError, match="wcześniejszy niż 1950"):
            validate_production_year(1949)
    
    def test_production_year_future(self):
        """Production year cannot be in the future"""
        current_year = datetime.now().year
        with pytest.raises(ValueError, match="późniejszy niż"):
            validate_production_year(current_year + 1)


class TestFirstRegistrationDateValidator:
    """Test first registration date validation"""
    
    def test_valid_dates(self):
        """Test valid registration dates"""
        assert validate_first_registration_date(date(2020, 1, 15)) == date(2020, 1, 15)
        assert validate_first_registration_date(date(1990, 6, 1)) == date(1990, 6, 1)
    
    def test_date_too_old(self):
        """Registration date cannot be before 1950"""
        with pytest.raises(ValueError, match="wcześniejsza niż"):
            validate_first_registration_date(date(1949, 12, 31))
    
    def test_date_future(self):
        """Registration date cannot be in the future"""
        tomorrow = date.today().replace(day=date.today().day + 1) if date.today().day < 28 else date.today().replace(month=date.today().month + 1, day=1)
        with pytest.raises(ValueError, match="przyszłości"):
            validate_first_registration_date(date(2099, 1, 1))
    
    def test_date_none(self):
        """Registration date can be None"""
        assert validate_first_registration_date(None) is None


class TestPriceValidator:
    """Test price validation"""
    
    def test_valid_prices(self):
        """Test valid prices"""
        assert validate_price(0) == 0
        assert validate_price(50000) == 50000
        assert validate_price(1_000_000) == 1_000_000
    
    def test_price_negative(self):
        """Price cannot be negative"""
        with pytest.raises(ValueError, match="ujemna"):
            validate_price(-1)
        
        with pytest.raises(ValueError, match="ujemna"):
            validate_price(-50000)
    
    def test_price_too_high(self):
        """Price cannot exceed 1,000,000"""
        with pytest.raises(ValueError, match="1,000,000 PLN"):
            validate_price(1_000_001)


class TestMileageValidator:
    """Test mileage validation"""
    
    def test_valid_mileage(self):
        """Test valid mileage values"""
        assert validate_mileage(0) == 0
        assert validate_mileage(100000) == 100000
        assert validate_mileage(1_500_000) == 1_500_000
    
    def test_mileage_negative(self):
        """Mileage cannot be negative"""
        with pytest.raises(ValueError, match="ujemny"):
            validate_mileage(-1)
    
    def test_mileage_too_high(self):
        """Mileage cannot exceed 1,500,000 km"""
        with pytest.raises(ValueError, match="1,500,000 km"):
            validate_mileage(1_500_001)


class TestSeatsValidator:
    """Test number of seats validation"""
    
    def test_valid_seats(self):
        """Test valid seat numbers"""
        assert validate_seats(1) == 1
        assert validate_seats(5) == 5
        assert validate_seats(9) == 9
    
    def test_seats_too_low(self):
        """Seats must be at least 1"""
        with pytest.raises(ValueError, match="co najmniej 1"):
            validate_seats(0)
    
    def test_seats_too_high(self):
        """Seats cannot exceed 9"""
        with pytest.raises(ValueError, match="przekraczać 9"):
            validate_seats(10)
    
    def test_seats_none(self):
        """Seats can be None"""
        assert validate_seats(None) is None


class TestEngineDisplacementValidator:
    """Test engine displacement validation"""
    
    def test_valid_displacement(self):
        """Test valid displacement values"""
        assert validate_engine_displacement(100) == 100
        assert validate_engine_displacement(2300) == 2300
        assert validate_engine_displacement(10_000) == 10_000
    
    def test_displacement_too_low(self):
        """Displacement cannot be below 100 cc"""
        with pytest.raises(ValueError, match="mniejsza niż 100"):
            validate_engine_displacement(99)
    
    def test_displacement_too_high(self):
        """Displacement cannot exceed 10,000 cc"""
        with pytest.raises(ValueError, match="10,000 cm³"):
            validate_engine_displacement(10_001)
    
    def test_displacement_none(self):
        """Displacement can be None"""
        assert validate_engine_displacement(None) is None


class TestPowerValidator:
    """Test engine power validation"""
    
    def test_valid_power(self):
        """Test valid power values"""
        assert validate_power(20) == 20
        assert validate_power(163) == 163
        assert validate_power(2_000) == 2_000
    
    def test_power_too_low(self):
        """Power cannot be below 20 HP"""
        with pytest.raises(ValueError, match="mniejsza niż 20"):
            validate_power(19)
    
    def test_power_too_high(self):
        """Power cannot exceed 2,000 HP"""
        with pytest.raises(ValueError, match="2,000 KM"):
            validate_power(2_001)
    
    def test_power_none(self):
        """Power can be None"""
        assert validate_power(None) is None


class TestGVWValidator:
    """Test gross vehicle weight validation"""
    
    def test_valid_gvw(self):
        """Test valid GVW values"""
        assert validate_gvw(1_000) == 1_000
        assert validate_gvw(3_500) == 3_500
        assert validate_gvw(7_500) == 7_500
    
    def test_gvw_too_low(self):
        """GVW cannot be below 1,000 kg"""
        with pytest.raises(ValueError, match="mniejsza niż 1,000"):
            validate_gvw(999)
    
    def test_gvw_too_high(self):
        """GVW cannot exceed 7,500 kg"""
        with pytest.raises(ValueError, match="7,500 kg"):
            validate_gvw(7_501)
    
    def test_gvw_none(self):
        """GVW can be None"""
        assert validate_gvw(None) is None


class TestStringLengthValidator:
    """Test string length validation"""
    
    def test_valid_string_length(self):
        """Test valid string lengths"""
        assert validate_string_length("Test", "Field", 10) == "Test"
        assert validate_string_length("A" * 100, "Field", 100) == "A" * 100
    
    def test_string_too_long(self):
        """String cannot exceed max length"""
        with pytest.raises(ValueError, match="nie może przekraczać"):
            validate_string_length("A" * 101, "Field", 100)
    
    def test_string_none_or_empty(self):
        """String can be None or empty"""
        assert validate_string_length(None, "Field", 100) is None
        assert validate_string_length("", "Field", 100) is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
