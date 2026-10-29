import serial
import time
import numpy as np
import cv2

def rle_decode(data):
    decoded = []
    for byte in data:
        color = byte & 0xF0
        length = (byte & 0x0F) + 1
        decoded.extend([color] * length)
    return np.array(decoded, dtype=np.uint8)

def rle_encode(image):
    flat = image.flatten()
    result = bytearray()
    count = 1
    prev = flat[0] & 0xF0
    for i in range(1, len(flat)):
        current = flat[i] & 0xF0
        if current == prev and count < 16:
            count += 1
        else:
            result.append(prev | (count - 1))
            prev = current
            count = 1
    result.append(prev | (count - 1))
    return result

def perspective_correction(img):
    edges = cv2.Canny(img, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)

    for cnt in contours:
        epsilon = 0.02 * cv2.arcLength(cnt, True)
        approx = cv2.approxPolyDP(cnt, epsilon, True)
        if len(approx) == 4:
            pts = approx.reshape(4, 2)
            break
    else:
        print("No quadrilateral found!")
        return img

    def sort_pts(pts):
        s = pts.sum(axis=1)
        diff = np.diff(pts, axis=1)
        return np.array([
            pts[np.argmin(s)],
            pts[np.argmin(diff)],
            pts[np.argmax(s)],
            pts[np.argmax(diff)]
        ])

    pts = sort_pts(pts)
    dst_pts = np.array([[0, 0], [174, 0], [174, 144], [0, 144]], dtype=np.float32)
    M = cv2.getPerspectiveTransform(pts.astype(np.float32), dst_pts)
    warped = cv2.warpPerspective(img, M, (174, 144))
    return warped

def show_image(decoded):
    img = decoded.reshape((144, 174))
    cv2.imshow("Live Image", img)
    cv2.waitKey(1)

def wait_for_image(ser):
    is_aligned = False
    image_data = bytearray()

    while True:
        line = ser.readline().strip()
        if line == b"!ALIGN!":
            is_aligned = True
        elif line == b"!START!":
            break

    while True:
        line = ser.readline()
        if b"!END!" in line:
            break
        image_data.extend(line)

    return is_aligned, image_data

def send_corrected_image(ser, image):
    rle_data = rle_encode(image)
    print("[INFO] Sending aligned image back to STM32...")
    ser.write(b"!START!\r\n")
    time.sleep(0.01)
    ser.write(rle_data)
    time.sleep(0.01)
    ser.write(b"!END!\r\n")
    time.sleep(0.05)

def main():
    ser = serial.Serial("COM3", 115200, timeout=1)
    time.sleep(2)
    print("[INFO] Serial connected. Waiting for frames...")

    while True:
        try:
            is_aligned, img_data = wait_for_image(ser)
            decoded = rle_decode(img_data)
            image = decoded.reshape((144, 174))

            if is_aligned:
                print("[INFO] ALIGN flag detected! Performing perspective correction...")
                aligned = perspective_correction(image)
                cv2.imshow("Aligned Image", aligned)
                cv2.waitKey(1)
                send_corrected_image(ser, aligned)
            else:
                show_image(decoded)

        except KeyboardInterrupt:
            print("\n[INFO] Exiting...")
            break

    ser.close()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
