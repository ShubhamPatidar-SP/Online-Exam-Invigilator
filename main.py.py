import cv2
import winsound
import smtplib
import os
from datetime import datetime, timedelta
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from plyer import notification

def notifyMe():
    ttl = "ALERT!"
    msg = "THERE IS UNWANTED MOVEMENT RECORDED IN CAMERA. PLEASE BE ATTENTIVE IN EXAM"
    notification.notify(
        title=ttl,
        message=msg,
        app_icon=r"D:\SPARK\PROJECT\ONLINE_EXAM_INVIGILATOR\image\alert.ico",
        timeout=None,
        toast = False,
    )

def capture_and_send_attention_clip(cam,frame):
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    filename = f"Attention_{timestamp}.avi"
    height, width, _ = frame.shape
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    output_folder = r"D:\SPARK\PROJECT\ONLINE_EXAM_INVIGILATOR\attention_clips"  # Use raw string with 'r' to avoid escape characters
    os.makedirs(output_folder, exist_ok=True)  # Create the output folder if it doesn't exist
    output_filename = os.path.join(output_folder, filename)
    out = cv2.VideoWriter(output_filename, fourcc, 20.0, (width, height))

    # Record the video for 5 seconds
    end_time = datetime.now() + timedelta(seconds=5)
    while datetime.now() < end_time:
        ret, frame = cam.read()  # Read a new frame from the camera
        out.write(frame)  # Write the frame to the video
        cv2.imshow("Recording Examinee Video", frame)

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    out.release()


    # Send email with the video clip attachment
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    From_Eid = # Replace with your email address
    From_Pswd =   # Replace with your email password
    To_Eid = # Replace with invigilator's email address
    server.login(From_Eid, From_Pswd)

    subject = "Attention: Unwanted Movement Detected"
    message = "THERE IS UNWANTED MOVEMENT CAPTURED IN THE CAMERA OF A STUDENT. PLEASE PAY ATTENTION."

    msg = MIMEMultipart()
    msg['From'] = From_Eid
    msg['To'] = To_Eid
    msg['Subject'] = subject

    body = message
    msg.attach(MIMEText(body, 'plain'))

    # Attach the video clip to the email
    with open(output_filename, "rb") as f:
        attachment_data = f.read()

    attachment = MIMEBase("application", "octet-stream")
    attachment.set_payload(attachment_data)
    encoders.encode_base64(attachment)
    attachment.add_header("Content-Disposition", f"attachment; filename=Attention_{timestamp}.avi")
    msg.attach(attachment)

    server.sendmail(From_Eid, To_Eid, msg.as_string())
    server.quit()

def main():
    cam = cv2.VideoCapture(0)
    count = 0

    while cam.isOpened():
        ret, frame1 = cam.read()
        ret, frame2 = cam.read()
        if not ret:
            break

        diff = cv2.absdiff(frame1, frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        _, thresh = cv2.threshold(blur, 20, 255, cv2.THRESH_BINARY)
        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for c in contours:
            if cv2.contourArea(c) < 15000:
                continue

            x, y, w, h = cv2.boundingRect(c)
            cv2.rectangle(frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
            winsound.Beep(2000, 100)

            count += 1
            if count % 5 == 0:
                notifyMe()

            if count % 11 == 0:
                capture_and_send_attention_clip(cam,frame1)
                # SendMailToInvig()
                count = 0

        cv2.imshow('ONLINE INVIGILATOR', frame1)

        if cv2.waitKey(10) == ord('q'):
            break

    cam.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()



    # ========================end of project====================
    # =======oxfurvqbfrmgclce========="sdfsfajtysgtets"=========