# built-in dependencies
import time
from typing import Any, Dict, Optional, Union, List, Tuple

# 3rd party dependencies
import numpy as np

# project dependencies
from deepface.modules import  detection, modeling
from deepface.models.FacialRecognition import FacialRecognition
from deepface.commons import logger as log

import numpy as np

# project dependencies
from deepface.commons import image_utils
from deepface.modules import modeling, detection, preprocessing
from deepface.models.FacialRecognition import FacialRecognition









logger = log.get_singletonish_logger()
class ImageVerification:
    def __init__(self,model_name:str) -> None:
        self.model_name = model_name
        self.model:FacialRecognition = modeling.build_model(self.model_name)

    def represent(
            self,
            img_path: Union[str, np.ndarray],
            enforce_detection: bool = True,
            detector_backend: str = "opencv",
            align: bool = True,
            expand_percentage: int = 0,
            normalization: str = "base",
            anti_spoofing: bool = False,
    ) -> List[Dict[str, Any]]:
    
        resp_objs = []

        model: FacialRecognition = self.model

        # ---------------------------------
        # we have run pre-process in verification. so, this can be skipped if it is coming from verify.
        target_size = model.input_shape
        if detector_backend != "skip":
            img_objs = detection.extract_faces(
                img_path=img_path,
                detector_backend=detector_backend,
                grayscale=False,
                enforce_detection=enforce_detection,
                align=align,
                expand_percentage=expand_percentage,
                anti_spoofing=anti_spoofing,
            )
        else:  # skip
            # Try load. If load error, will raise exception internal
            img, _ = image_utils.load_image(img_path)

            if len(img.shape) != 3:
                raise ValueError(f"Input img must be 3 dimensional but it is {img.shape}")

            # make dummy region and confidence to keep compatibility with `extract_faces`
            img_objs = [
                {
                    "face": img,
                    "facial_area": {"x": 0, "y": 0, "w": img.shape[0], "h": img.shape[1]},
                    "confidence": 0,
                }
            ]
        # ---------------------------------
        for img_obj in img_objs:
            if anti_spoofing is True and img_obj.get("is_real", True) is False:
                raise ValueError("Spoof detected in the given image.")
            img = img_obj["face"]

            # rgb to bgr
            img = img[:, :, ::-1]

            region = img_obj["facial_area"]
            confidence = img_obj["confidence"]

            # resize to expected shape of ml model
            img = preprocessing.resize_image(
                img=img,
                # thanks to DeepId (!)
                target_size=(target_size[1], target_size[0]),
            )

            # custom normalization
            img = preprocessing.normalize_input(img=img, normalization=normalization)

            embedding = model.forward(img)

            resp_obj = {}
            resp_obj["embedding"] = embedding
            resp_obj["facial_area"] = region
            resp_obj["face_confidence"] = confidence
            resp_objs.append(resp_obj)

        return resp_objs
    def verify(
            self,
            img1_path: Union[str, np.ndarray, List[float]],
            img2_path: Union[str, np.ndarray, List[float]],
            detector_backend: str = "opencv",
            distance_metric: str = "cosine",
            enforce_detection: bool = True,
            align: bool = True,
            expand_percentage: int = 0,
            normalization: str = "base",
            silent: bool = False,
            threshold: Optional[float] = None,
            anti_spoofing: bool = False,
    ) -> Dict[str, Any]:

            tic = time.time()

            model: FacialRecognition = self.model
            dims = model.output_shape

            # extract faces from img1
            if isinstance(img1_path, list):
                # given image is already pre-calculated embedding
                if not all(isinstance(dim, float) for dim in img1_path):
                    raise ValueError(
                        "When passing img1_path as a list, ensure that all its items are of type float."
                    )

                if silent is False:
                    logger.warn(
                        "You passed 1st image as pre-calculated embeddings."
                        f"Please ensure that embeddings have been calculated for the {self.model_name} model."
                    )

                if len(img1_path) != dims:
                    raise ValueError(
                        f"embeddings of {self.model_name} should have {dims} dimensions,"
                        f" but it has {len(img1_path)} dimensions input"
                    )

                img1_embeddings = [img1_path]
                img1_facial_areas = [None]
            else:
                try:
                    img1_embeddings, img1_facial_areas = self.__extract_faces_and_embeddings(
                        img_path=img1_path,
                        detector_backend=detector_backend,
                        enforce_detection=enforce_detection,
                        align=align,
                        expand_percentage=expand_percentage,
                        normalization=normalization,
                        anti_spoofing=anti_spoofing,
                    )
                except ValueError as err:
                    raise ValueError("Exception while processing img1_path") from err

            # extract faces from img2
            if isinstance(img2_path, list):
                # given image is already pre-calculated embedding
                if not all(isinstance(dim, float) for dim in img2_path):
                    raise ValueError(
                        "When passing img2_path as a list, ensure that all its items are of type float."
                    )

                if silent is False:
                    logger.warn(
                        "You passed 2nd image as pre-calculated embeddings."
                        f"Please ensure that embeddings have been calculated for the {self.model_name} model."
                    )

                if len(img2_path) != dims:
                    raise ValueError(
                        f"embeddings of {self.model_name} should have {dims} dimensions,"
                        f" but it has {len(img2_path)} dimensions input"
                    )

                img2_embeddings = [img2_path]
                img2_facial_areas = [None]
            else:
                try:
                    img2_embeddings, img2_facial_areas = self.__extract_faces_and_embeddings(
                        img_path=img2_path,
                        detector_backend=detector_backend,
                        enforce_detection=enforce_detection,
                        align=align,
                        expand_percentage=expand_percentage,
                        normalization=normalization,
                        anti_spoofing=anti_spoofing,
                    )
                except ValueError as err:
                    raise ValueError("Exception while processing img2_path") from err

            no_facial_area = {
                "x": None,
                "y": None,
                "w": None,
                "h": None,
                "left_eye": None,
                "right_eye": None,
            }

            distances = []
            facial_areas = []
            for idx, img1_embedding in enumerate(img1_embeddings):
                for idy, img2_embedding in enumerate(img2_embeddings):
                    distance = self.find_distance(img1_embedding, img2_embedding, distance_metric)
                    distances.append(distance)
                    facial_areas.append(
                        (img1_facial_areas[idx] or no_facial_area, img2_facial_areas[idy] or no_facial_area)
                    )

            # find the face pair with minimum distance
            threshold = threshold or self.find_threshold(self.model_name, distance_metric)
            distance = float(min(distances))  # best distance
            facial_areas = facial_areas[np.argmin(distances)]

            toc = time.time()

            resp_obj = {
                "verified": distance <= threshold,
                "distance": distance,
                "threshold": threshold,
                "model": self.model_name,
                "detector_backend": detector_backend,
                "similarity_metric": distance_metric,
                "facial_areas": {"img1": facial_areas[0], "img2": facial_areas[1]},
                "time": round(toc - tic, 2),
            }

            return resp_obj


    def __extract_faces_and_embeddings(
            self,
            img_path: Union[str, np.ndarray],
            detector_backend: str = "opencv",
            enforce_detection: bool = True,
            align: bool = True,
            expand_percentage: int = 0,
            normalization: str = "base",
            anti_spoofing: bool = False,
    ) -> Tuple[List[List[float]], List[dict]]:
        """
        Extract facial areas and find corresponding embeddings for given image
        Returns:
            embeddings (List[float])
            facial areas (List[dict])
        """
        embeddings = []
        facial_areas = []

        img_objs = detection.extract_faces(
            img_path=img_path,
            detector_backend=detector_backend,
            grayscale=False,
            enforce_detection=enforce_detection,
            align=align,
            expand_percentage=expand_percentage,
            anti_spoofing=anti_spoofing,
        )

        # find embeddings for each face
        for img_obj in img_objs:
            if anti_spoofing is True and img_obj.get("is_real", True) is False:
                raise ValueError("Spoof detected in given image.")
            img_embedding_obj = self.represent(
                img_path=img_obj["face"],
                enforce_detection=enforce_detection,
                detector_backend="skip",
                align=align,
                normalization=normalization,
            )
            # already extracted face given, safe to access its 1st item
            img_embedding = img_embedding_obj[0]["embedding"]
            embeddings.append(img_embedding)
            facial_areas.append(img_obj["facial_area"])

        return embeddings, facial_areas


    def find_cosine_distance(
        self,
        source_representation: Union[np.ndarray, list], test_representation: Union[np.ndarray, list]
    ) -> np.float64:
        """
        Find cosine distance between two given vectors
        Args:
            source_representation (np.ndarray or list): 1st vector
            test_representation (np.ndarray or list): 2nd vector
        Returns
            distance (np.float64): calculated cosine distance
        """
        if isinstance(source_representation, list):
            source_representation = np.array(source_representation)

        if isinstance(test_representation, list):
            test_representation = np.array(test_representation)

        a = np.matmul(np.transpose(source_representation), test_representation)
        b = np.sum(np.multiply(source_representation, source_representation))
        c = np.sum(np.multiply(test_representation, test_representation))
        return 1 - (a / (np.sqrt(b) * np.sqrt(c)))


    def find_euclidean_distance(
            self,
        source_representation: Union[np.ndarray, list], test_representation: Union[np.ndarray, list]
    ) -> np.float64:
        """
        Find euclidean distance between two given vectors
        Args:
            source_representation (np.ndarray or list): 1st vector
            test_representation (np.ndarray or list): 2nd vector
        Returns
            distance (np.float64): calculated euclidean distance
        """
        if isinstance(source_representation, list):
            source_representation = np.array(source_representation)

        if isinstance(test_representation, list):
            test_representation = np.array(test_representation)

        euclidean_distance = source_representation - test_representation
        euclidean_distance = np.sum(np.multiply(euclidean_distance, euclidean_distance))
        euclidean_distance = np.sqrt(euclidean_distance)
        return euclidean_distance


    def l2_normalize(self, x: Union[np.ndarray, list]) -> np.ndarray:
        """
        Normalize input vector with l2
        Args:
            x (np.ndarray or list): given vector
        Returns:
            y (np.ndarray): l2 normalized vector
        """
        if isinstance(x, list):
            x = np.array(x)
        return x / np.sqrt(np.sum(np.multiply(x, x)))


    def find_distance(
            self,
            alpha_embedding: Union[np.ndarray, list],
            beta_embedding: Union[np.ndarray, list],
            distance_metric: str,
    ) -> np.float64:
        """
        Wrapper to find distance between vectors according to the given distance metric
        Args:
            source_representation (np.ndarray or list): 1st vector
            test_representation (np.ndarray or list): 2nd vector
        Returns
            distance (np.float64): calculated cosine distance
        """
        if distance_metric == "cosine":
            distance = self.find_cosine_distance(alpha_embedding, beta_embedding)
        elif distance_metric == "euclidean":
            distance = self.find_euclidean_distance(alpha_embedding, beta_embedding)
        elif distance_metric == "euclidean_l2":
            distance = self.find_euclidean_distance(
                self.l2_normalize(alpha_embedding), self.l2_normalize(beta_embedding)
            )
        else:
            raise ValueError("Invalid distance_metric passed - ", distance_metric)
        return distance


    def find_threshold(self, model_name: str, distance_metric: str) -> float:
        """
        Retrieve pre-tuned threshold values for a model and distance metric pair
        Args:
            model_name (str): Model for face recognition. Options: VGG-Face, Facenet, Facenet512,
                OpenFace, DeepFace, DeepID, Dlib, ArcFace, SFace and GhostFaceNet (default is VGG-Face).
            distance_metric (str): distance metric name. Options are cosine, euclidean
                and euclidean_l2.
        Returns:
            threshold (float): threshold value for that model name and distance metric
                pair. Distances less than this threshold will be classified same person.
        """

        base_threshold = {"cosine": 0.40, "euclidean": 0.55, "euclidean_l2": 0.75}

        thresholds = {
            # "VGG-Face": {"cosine": 0.40, "euclidean": 0.60, "euclidean_l2": 0.86}, # 2622d
            "VGG-Face": {
                "cosine": 0.68,
                "euclidean": 1.17,
                "euclidean_l2": 1.17,
            },  # 4096d - tuned with LFW
            "Facenet": {"cosine": 0.40, "euclidean": 10, "euclidean_l2": 0.80},
            "Facenet512": {"cosine": 0.30, "euclidean": 23.56, "euclidean_l2": 1.04},
            "ArcFace": {"cosine": 0.68, "euclidean": 4.15, "euclidean_l2": 1.13},
            "Dlib": {"cosine": 0.07, "euclidean": 0.6, "euclidean_l2": 0.4},
            "SFace": {"cosine": 0.593, "euclidean": 10.734, "euclidean_l2": 1.055},
            "OpenFace": {"cosine": 0.10, "euclidean": 0.55, "euclidean_l2": 0.55},
            "DeepFace": {"cosine": 0.23, "euclidean": 64, "euclidean_l2": 0.64},
            "DeepID": {"cosine": 0.015, "euclidean": 45, "euclidean_l2": 0.17},
            "GhostFaceNet": {"cosine": 0.65, "euclidean": 35.71, "euclidean_l2": 1.10},
        }

        threshold = thresholds.get(model_name, base_threshold).get(distance_metric, 0.4)

        return threshold
