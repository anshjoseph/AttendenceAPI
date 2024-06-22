from .verification_system import ImageVerification
from threading import Thread
from pydantic import BaseModel
from io import BytesIO
from PIL import Image
import asyncio
from base64 import b64encode, b64decode
import numpy as np
import logging
from uuid import uuid4
VALID_LOGGING_LEVELS = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


def configure_logger(file_name, enabled=True, logging_level='INFO'):
    if logging_level not in VALID_LOGGING_LEVELS:
        logging_level = "INFO"

    logging.basicConfig(
        level=logging_level,
        format="%(asctime)s.%(msecs)03d %(levelname)s {%(module)s} [%(funcName)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger = logging.getLogger(file_name)

    if not enabled:
        logger.disabled = True
    return logger

logger = configure_logger(__name__)
class Task(BaseModel):
    comp1: str
    comp2: str

class ImageComp:
    def __init__(self,model_name = "VGG-Face") -> None:
        self.metrics = ["cosine", "euclidean", "euclidean_l2"]
        self.image_verfication = ImageVerification(model_name)
        logger.info(f"model selected: {model_name}")

    def __process(self,task:Task,ret:list):
        img1 = np.asarray(Image.open(BytesIO(b64decode(task.comp1))).convert("RGB"))
        img2 = np.asarray(Image.open(BytesIO(b64decode(task.comp2))).convert("RGB"))
        ret.append(self.image_verfication.verify(img1,img2))
    
    async def get_prediction(self,task:Task):
        ret:list = list()
        thread = Thread(target=self.__process,args=(task,ret,))
        thread.setName(f"{uuid4()}")
        thread.start()
        logger.info(f"new thread is strated {thread.getName()}")
        while thread.is_alive():
            logger.info(f"waiting for thread {thread.getName()} to complete")
            await asyncio.sleep(0.5)
        logger.info(f"thread {thread.getName()} is completed with result { ret[0] }")
        return ret.pop()

    
