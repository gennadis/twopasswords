from time import sleep
from cv2 import VideoCapture, imwrite, imread, rectangle

from face_recognition import (
    load_image_file,
    face_landmarks,
    compare_faces,
    face_encodings,
    face_locations,
)

from utils import emailer


"""
------------------
IT"S ALL GOOD HERE
------------------
"""


class FaceScan:
    """
    This Class is responsible for face recognition functionality.
    Instance of a class takes two arguments:
    - user_face for reference image path
    - try_face for image that should be compared with reference path
    """

    def __init__(self, user_face: str, try_face: str) -> None:
        self.user_face = user_face
        self.try_face = try_face

    def take_picture(self) -> None:
        """
        1. Take a picture with a builtin webcam.
        2. Write to a file.
        """
        cap = VideoCapture(0)
        sleep(1)
        ret, frame = cap.read()
        imwrite(self.try_face, frame)
        cap.release()

    def count_faces(self) -> int:
        """
        1. Load a picture
        2. Get a list of face landmarks
        return 0 if no faces detected
               1 if one face detected
               >1 if multiple faces detected
        """

        load_image = load_image_file(self.try_face)
        face_landmarks_list = face_landmarks(load_image)
        return len(face_landmarks_list)

    def draw_rectangle(self) -> None:
        """
        Draw a nice red rectangle around the face
        """

        img = imread(self.try_face)
        taken_img = load_image_file(self.try_face)
        taken_img_faces = face_locations(taken_img)

        for face in taken_img_faces:
            top_left = face[3], face[0]
            bottom_right = face[1], face[2]
            rectangle(img, top_left, bottom_right, (255, 0, 255), 2)
        imwrite(self.try_face, img)

    def compare_faces(self, tolerance: float = 0.6) -> bool:
        """
        1. Load and encode reference user image for comparison
        2. Load and get face landmarks from taken image for comparison
        3. Compare results.
        return numpy.bool_ - type object
        """

        reference_img = load_image_file(self.user_face)
        reference_encoding = face_encodings(reference_img)[0]

        try_img = load_image_file(self.try_face)
        try_encoding = face_encodings(try_img)

        results = compare_faces(
            [reference_encoding], try_encoding[0], tolerance=tolerance
        )
        return results[0]  # <class 'numpy.bool_'>

    def auth(self) -> bool:
        """
        Here's whe the main auth logic is scripted.
        1. Take a picture from a webcam
        2. Check the number of faces in a taken picture
        3. Compare face from a taken image to a Reference
        and send report email if stranger's face detected
        4. return
           -1 :   Stranger's face detected
            0 :   No face detected
            1 :   Auth OK
            2 :   Multiple faces detected
        """
        self.take_picture()

        if self.count_faces() == 0:
            return 0
        if self.count_faces() > 1:
            self.draw_rectangle()
            return 2

        if self.compare_faces() != [True]:  # some strange comparison here...
            self.draw_rectangle()
            emailer.send_auth_report(
                "Warning! Stranger's face detected. Check the image in attachments."
            )
            return -1

        return 1
