"""
logger.py
Yapılandırılmış logging sistemi.
Konsol ve dosya çıktısı destekler.
"""

import logging
import os
from datetime import datetime

def setup_logger(name: str, log_file: str = None, level=logging.INFO) -> logging.Logger:
    """
    Yapılandırılmış logger oluşturur.
    
    Args:
        name: Logger adı
        log_file: Opsiyonel log dosyası yolu
        level: Log seviyesi
    
    Returns:
        Yapılandırılmış Logger objesi
    """
    # Formatter oluştur
    formatter = logging.Formatter(
        fmt='%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Logger al
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Daha önce handler eklenmişse tekrar ekleme
    if logger.handlers:
        return logger
    
    # Konsol handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Dosya handler (opsiyonel)
    if log_file:
        # Log klasörünü oluştur
        log_dir = os.path.dirname(log_file)
        if log_dir:
            os.makedirs(log_dir, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_training_logger() -> logging.Logger:
    """Model eğitimi için özel logger."""
    from config import LOGS_DIR
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, f'training_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')
    return setup_logger('training', log_file)


def get_prediction_logger() -> logging.Logger:
    """Tahmin işlemleri için özel logger."""
    from config import LOGS_DIR
    os.makedirs(LOGS_DIR, exist_ok=True)
    log_file = os.path.join(LOGS_DIR, 'predictions.log')
    return setup_logger('prediction', log_file)
