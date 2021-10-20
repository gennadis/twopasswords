import os
import cv2
import face_recognition
from time import sleep
from dotenv import load_dotenv
from emailer import Email


"""
------------------
IT"S ALL GOOD HERE
------------------
"""


load_dotenv()
EMAIL_ADDRESS = os.environ.get("EMAIL_ADDRESS")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD")
EMAIL_SERVER = os.environ.get("EMAIL_SERVER")
EMAIL_PORT = os.environ.get("EMAIL_PORT")


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
        cap = cv2.VideoCapture(0)
        sleep(1)
        ret, frame = cap.read()
        cv2.imwrite(self.try_face, frame)
        cap.release()

    def count_faces(self) -> int:
        """
        1. Load a picture
        2. Get a list of face landmarks
        return 0 if no faces detected
               1 if one face detected
               >1 if multiple faces detected
        """

        load_image = face_recognition.load_image_file(self.try_face)
        face_landmarks_list = face_recognition.face_landmarks(load_image)
        return len(face_landmarks_list)

    def draw_rectangle(self) -> None:
        """
        Draw a nice red rectangle around the face
        """

        img = cv2.imread(self.try_face)
        taken_img = face_recognition.load_image_file(self.try_face)
        taken_img_faces = face_recognition.face_locations(taken_img)

        for face in taken_img_faces:
            top_left = face[3], face[0]
            bottom_right = face[1], face[2]
            cv2.rectangle(img, top_left, bottom_right, (255, 0, 255), 2)
        cv2.imwrite(self.try_face, img)

    def compare_faces(self, tolerance: float = 0.6) -> bool:
        """
        1. Load and encode reference user image for comparison
        2. Load and get face landmarks from taken image for comparison
        3. Compare results.
        return numpy.bool_ - type object
        """

        reference_img = face_recognition.load_image_file(self.user_face)
        reference_encoding = face_recognition.face_encodings(reference_img)[0]

        try_img = face_recognition.load_image_file(self.try_face)
        try_encoding = face_recognition.face_encodings(try_img)

        results = face_recognition.compare_faces(
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
        4. return False if auth Failed
                  True  if auth Succeeded
        """

        self.take_picture()

        if self.count_faces() == 0:
            print("No face detected")
            return False
        if self.count_faces() > 1:
            self.draw_rectangle()
            print("Multiple faces detected")
            return False

        if self.compare_faces() != [True]:  # some strange comparison here...
            self.draw_rectangle()
            Email(
                "Face auth report",
                "Warning! Last face auth was failed! Check the image in attachments!!!",
                EMAIL_ADDRESS,
                EMAIL_PASSWORD,
                self.try_face,
                EMAIL_SERVER,
                EMAIL_PORT,
            ).send_email()
            print("---------------- AUTH FAILED! ----------------")
            return False

        print("Auth OK! Ready to proceed.")
        return True


if __name__ == "__main__":

    load_dotenv()
    new_picture = os.environ.get("LAST_IMAGE_PATH")
    user_picture = os.environ.get("USER_FACE")

    if FaceScan(user_picture, new_picture).auth() is True:
        print("YEEEHAAAAAHH")
    else:
        print("Noooo")
