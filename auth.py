import sys
import cv2
import face_recognition
from time import sleep

# from face_auth.rect_face import draw_rectangle
# from face_auth.emailer import send_email

LAST_IMAGE_PATH = "last_face.jpg"


class Auth:
    def __init__(self):
        pass

    # Take picture from default webcam and save it for future comparison
    @staticmethod
    def take_picture() -> None:
        cap = cv2.VideoCapture(0)
        sleep(1)
        ret, frame = cap.read()
        cv2.imwrite(LAST_IMAGE_PATH, frame)
        cap.release()

    # Load picture and get face landmarks from image
    # def get_landmarks(self, picture: str) -> list:
    #     load_image = face_recognition.load_image_file(picture)
    #     face_landmarks_list = face_recognition.face_landmarks(load_image)
    #     return face_landmarks_list

    @staticmethod
    def count_faces() -> int:
        # Load picture and get face landmarks from image
        load_image = face_recognition.load_image_file(LAST_IMAGE_PATH)
        face_landmarks_list = face_recognition.face_landmarks(load_image)

        face_count = len(face_landmarks_list)
        # if more than 1 face detected
        if face_count > 1:
            # self.draw_rectangle()
            print("Multiple faces detected. NOT SAFE!")
            return 2

        # if no faces detected
        elif face_count == 0:
            print("No face detected. TRY AGAIN!")
            return 0

        # if only 1 face detected
        return 1

    @staticmethod
    # Compare face image taken from webcam to a reference face images
    def compare_faces(tolerance: float = 0.6) -> None:

        # Load and encode reference user image for comparison
        reference_img = face_recognition.load_image_file("1.jpg")
        reference_encoding = face_recognition.face_encodings(reference_img)[0]

        # Load and get face landmarks from taken image for comparison
        last_img = face_recognition.load_image_file(LAST_IMAGE_PATH)
        last_encoding = face_recognition.face_encodings(last_img)[0]

        # Compare results. Result returns list ['True'] like.
        results = face_recognition.compare_faces(
            [reference_encoding], last_encoding, tolerance=tolerance
        )
        # If face comparison was successfull
        if results[0] == True:
            # self.draw_rectangle()
            print("AUTH OK! READY TO PROCEED...")

        # If face comparison was NOT successfull
        else:
            # self.draw_rectangle()
            # self.send_email()
            sys.exit("---------------- AUTH FAILED! ----------------")


def main():
    Auth.take_picture()
    check_result = Auth.count_faces()
    if check_result == 1:

        Auth.compare_faces()
    elif check_result == 0:
        print("No face detected")
    else:
        print("Multiple faces detected")


if __name__ == "__main__":
    main()
