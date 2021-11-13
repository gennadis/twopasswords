"""
# TODO: should place some nice text here...

This module is responsible for face 
recognition authentification processes.
...

"""

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


class FaceScan:
    """
    A class used to represent a FaceScan
    functionality and face recognition
    processes needed for user authentification.

    Attributes
    ----------
    user_face : str
        Reference user face picture file path
    try_face : str
        Image that should be compared file path

    Methods
    -------
    take_picture
        Takes image with a webcam
    count_faces
        Counts faces on taken image
    draw_rectangle
        Draws nice red rectangles around faces
    compare_faces(tolerance=0.6)
        Compares reference image face with other
    auth
        Implements main face authentification logic

    """

    def __init__(self, user_face: str, try_face: str) -> None:
        """
        Attributes
        ----------
        user_face : str
            Reference user face picture file path
        try_face : str
            Image that should be compared file path

        """

        self.user_face = user_face
        self.try_face = try_face

    def take_picture(self) -> None:
        """
        Takes a picture with a default builtin
        webcam and saves taken image on a disk.

        """
        cap = VideoCapture(0)

        # images from a webcam are too dark
        # without a small sleep pause:
        sleep(1)

        ret, frame = cap.read()
        imwrite(self.try_face, frame)
        cap.release()

    def count_faces(self) -> int:
        """
        Loads a picture and counts faces detected in one.

        Returns
        -------
        int
            Number of faces detected in image:
            0 if no faces detected
            1 if one face detected
            >1 if multiple faces detected

        """

        load_image = load_image_file(self.try_face)
        face_landmarks_list = face_landmarks(load_image)
        return len(face_landmarks_list)

    def draw_rectangle(self) -> None:
        """
        Draws nice red rectangles around all
        faces that were detected on the image.

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
        Compares reference user face with other face.

        Parameters
        ----------
        tolerance : float
            The tolerance that will be
            applied in face recognition process.
            Use 0.6 for optimal security & performance.
            Though tolerance lower than 0.6 is more strict.

        Returns
        -------
        numpy.bool_
            True if compare successfull,
            False otherwise.

        """

        # Load and encode reference user image
        reference_img = load_image_file(self.user_face)
        reference_encoding = face_encodings(reference_img)[0]

        # Load and get face landmarks from taken image
        try_img = load_image_file(self.try_face)
        try_encoding = face_encodings(try_img)

        results = compare_faces(
            [reference_encoding], try_encoding[0], tolerance=tolerance
        )

        # returns <class 'numpy.bool_'> object
        return results[0]

    def auth(self) -> int:
        """
        Authentificates user via face recognition.

        Returns
        -------
        int
            Authentification result matrix:
           -1 : Stranger's face detected
            0 : No face detected
            1 : Auth OK
            2 : Multiple faces detected

        """

        self.take_picture()

        if self.count_faces() == 0:
            return 0

        if self.count_faces() > 1:
            self.draw_rectangle()
            return 2

        # if result of auth is not True:
        if self.compare_faces() != [True]:
            self.draw_rectangle()
            emailer.send_auth_report(
                "Warning! Stranger's face detected. Check the image in attachments."
            )
            return -1

        # else: AUTH OK
        return 1
