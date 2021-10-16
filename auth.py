import os
import sys
import cv2
import dotenv
import face_recognition
from time import sleep
from emailer import Email

dotenv.load_dotenv()
last_image_file = os.environ.get("LAST_IMAGE_PATH")
reference_user_face = os.environ.get("USER_FACE")


class Auth:
    """
    This class is responsible for the face authorization
    - taking image
    operations needed in the program such as:
    - counting faces on taken image
    - comparing face from taken image to a reference face
    """

    # Take picture from default webcam and save it for future comparison
    @staticmethod
    def take_picture() -> None:
        cap = cv2.VideoCapture(0)
        sleep(1)
        ret, frame = cap.read()
        cv2.imwrite(last_image_file, frame)
        cap.release()

    @staticmethod
    def count_faces() -> int:
        # Load picture and get face landmarks from image
        load_image = face_recognition.load_image_file(last_image_file)
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
    def draw_rectangle():
        img = cv2.imread(last_image_file)
        taken_img = face_recognition.load_image_file(last_image_file)
        taken_img_faces = face_recognition.face_locations(taken_img)
        # print(f"{len(taken_img_faces)} FACE(S) WAS DETECTED")  # face counter for tests

        for face in taken_img_faces:
            top_left = face[3], face[0]
            bottom_right = face[1], face[2]
            cv2.rectangle(img, top_left, bottom_right, (255, 0, 255), 2)
        cv2.imwrite(last_image_file, img)

    @staticmethod
    # Compare face image taken from webcam to a reference face images
    def compare_faces(tolerance: float = 0.6) -> None:

        # Load and encode reference user image for comparison
        reference_img = face_recognition.load_image_file(reference_user_face)
        reference_encoding = face_recognition.face_encodings(reference_img)[0]

        # Load and get face landmarks from taken image for comparison
        last_img = face_recognition.load_image_file(last_image_file)
        last_encoding = face_recognition.face_encodings(last_img)[0]

        # Compare results. Result returns list ['True'] like.
        results = face_recognition.compare_faces(
            [reference_encoding], last_encoding, tolerance=tolerance
        )
        # If face comparison was successfull
        if results[0]:
            print("AUTH OK! READY TO PROCEED...")

        # If face comparison was NOT successfull
        else:
            report_email = Email(
                "Face auth report",
                "Warning! Last face auth failed! Check the image attached!!!",
                last_image_file,
            )
            report_email.send_email()
            print("---------------- AUTH FAILED! ----------------")
            sys.exit()


def main():

    Auth.take_picture()
    check_result = Auth.count_faces()
    if check_result == 1:
        Auth.draw_rectangle()
        Auth.compare_faces()

    elif check_result == 0:
        print("No face detected")

    else:
        Auth.draw_rectangle()
        print("Multiple faces detected")


if __name__ == "__main__":
    main()
