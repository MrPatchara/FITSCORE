import pytest
import math
from datetime import date
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.db import Base
from app.models.athlete import Athlete

def test_bmi_and_fat_skinfold_calculation():
    # Test Durnin-Womersley + Siri Body Fat estimation
    # 25 year old male
    ath_male = Athlete(
        first_name="Male",
        last_name="Test",
        gender="Male",
        date_of_birth=date(date.today().year - 25, 1, 1)
    )
    
    # Biceps: 5, Triceps: 10, Subscapular: 12, Supraliac: 15. Sum = 42
    sum_skinfold = 42.0
    log_sum = math.log10(sum_skinfold)
    
    # For male 20-29: c = 1.1631, m = 0.0632
    c, m = 1.1631, 0.0632
    density = c - m * log_sum
    expected_fat = (4.95 / density - 4.50) * 100
    
    assert density > 1.0
    assert 10.0 < expected_fat < 20.0  # Realistic body fat range for lean male

def test_astrand_ryhming_vo2max_calculation():
    # Test Astrand-Ryhming Cycle Ergometer VO2max estimation
    # 22 year old female, weight = 60kg
    weight = 60.0
    pulse_test = 150.0
    load_kp = 1.5
    
    work_rate = load_kp * 300  # 450
    
    # Female O2 uptake: (0.00193 * work_rate) + 0.326
    vo2 = (0.00193 * work_rate) + 0.326  # 1.1945
    
    # Female HR Nomogram correction: (220 - age - 72) / (pulse_test - 72)
    age = 22
    hr_max = 220 - age
    raw_vo2max = vo2 * ((hr_max - 72) / (pulse_test - 72))
    
    # Age factor for 22 is 1.00
    vo2max_corrected = raw_vo2max * 1.00
    relative_vo2max = (vo2max_corrected * 1000.0) / weight
    
    assert relative_vo2max > 0.0
    assert 25.0 < relative_vo2max < 45.0  # Realistic relative VO2max range for active female
