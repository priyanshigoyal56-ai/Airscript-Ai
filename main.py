# ==========================================================
# AirScript AI
# Main Program
# Final Version
# ==========================================================

import cv2

from Modules.HandTrackingModule import HandDetector
from Modules.CursorModule import Cursor
from Modules.ProjectionModule import Projection
from Modules.WhiteboardModule import Whiteboard
from Modules.DrawingModule import DrawingEngine
from Modules.ToolbarModule import Toolbar
from Modules.OCRModule import OCR
from Modules.TextRenderer import TextRenderer
from Modules.SaveModule import SavePDF


def main():

    # ======================================================
    # Camera
    # ======================================================

    cap = cv2.VideoCapture(0)

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    if not cap.isOpened():

        print("Camera not found!")
        return

    # ======================================================
    # Modules
    # ======================================================

    detector = HandDetector()

    cursor = Cursor(smoothening=3)

    projection = Projection()

    whiteboard = Whiteboard()

    drawing = DrawingEngine()

    toolbar = Toolbar()

    ocr = OCR()

    renderer = TextRenderer()
    pdf = SavePDF()

    

    print("===================================")
    print(" AirScript AI Started Successfully ")
    print("===================================")
    print("Q : Quit")
    print("C : Clear")
    print("U : Undo")
    print("R : Redo")
    print("O : OCR")
    print("===================================")
    # ======================================================
    # Main Loop
    # ======================================================

    while True:

        success, frame = cap.read()

        if not success:
            break

        frame = cv2.flip(frame, 1)

        frame = detector.findHands(frame)

        lmList = detector.findPosition(
            frame,
            draw=False
        )

        board = whiteboard.create()

        # ==================================================
        # Hand Detection
        # ==================================================

        if len(lmList) != 0:

            fingers = detector.fingersUp(lmList)
        

            x, y = lmList[8][1], lmList[8][2]

            smoothX, smoothY = cursor.update(x, y)

            boardX, boardY = projection.project(
                smoothX,
                smoothY
            )
            pinching = detector.isPinching(lmList)
            # ==============================================
            # Toolbar Selection
            # ==============================================
            if  not pinching:

              selectedTool = toolbar.checkSelection(
                boardX,
                boardY
              )
            else:

              selectedTool = None
            

            if selectedTool == "White":
                drawing.enableBrush()
                drawing.setColor((255, 255, 255))

            elif selectedTool == "Red":
                drawing.enableBrush()
                drawing.setColor((0, 0, 255))

            elif selectedTool == "Green":
                drawing.enableBrush()
                drawing.setColor((0, 255, 0))

            elif selectedTool == "Blue":
                drawing.enableBrush()
                drawing.setColor((255, 0, 0))
            
            elif selectedTool == "Eraser":

                drawing.enableEraser()

            elif selectedTool == "Brush +":

                drawing.setThickness(
                    min(drawing.thickness + 2, 60)
                )

            elif selectedTool == "Brush -":

                drawing.setThickness(
                    max(drawing.thickness - 2, 2)
                )
            elif selectedTool == "Clear":

                drawing.clear()
            

            # ==============================================
            # Drawing Area
            # ==============================================

            if projection.insideBoard(boardX, boardY):

                # ==========================================
                # Cursor Preview
                # ==========================================

                if drawing.eraserMode:

                        distance = detector.findDistance(
                            4,
                            8,
                            lmList
                        )

                        size = int(distance * 0.8)

                        # Limit eraser size
                        size = max(10, min(size, 60))

                        drawing.setThickness(size)

                        # Show only eraser preview
                        cv2.circle(
                            board,
                            (boardX, boardY),
                            size,
                            (0, 255, 255),
                            2
                        )

                else:

                        # Normal cursor
                        cv2.circle(
                            board,
                            (boardX, boardY),
                            8,
                            (255, 255, 255),
                            -1
                        )

                        cv2.circle(
                            board,
                            (boardX, boardY),
                            16,
                            (0, 255, 255),
                            2
                        )

                # ==========================================
                # Drawing / Erasing
                # ==========================================
                if pinching:

                        drawing.draw(
                            boardX,
                            boardY
                        )
                # Erase (Index + Middle Finger)
                elif drawing.eraserMode and fingers == [0, 1, 1, 0, 0]:

                    drawing.draw(
                        boardX,
                        boardY
                    )


                else:

                        drawing.stopStroke()

            else:

               drawing.stopStroke()

                

    
        # ======================================================
        # Merge Drawing
        # ======================================================

        board = drawing.merge(board)

        # ======================================================
        # Draw Toolbar
        # ======================================================

        board = toolbar.draw(board)

        # ======================================================
        # Camera Preview
        # ======================================================

        board = whiteboard.placeCamera(
            board,
            frame
        )

        # ======================================================
        # Show Window
        # ======================================================

        cv2.imshow(
            "AirScript AI",
            board
        )

        # ======================================================
        # Keyboard Controls
        # ======================================================

        key = cv2.waitKey(1) & 0xFF

        # Quit
        if key == ord("q"):
            break

        # Clear Canvas
        # Clear Canvas
        elif key == ord("c"):
          drawing.clear()

        # Undo
        elif key == ord("u"):
          drawing.undo()

        # Redo
        elif key == ord("r"):
          drawing.redo()
            
        # OCR
        
        elif key == ord("o"):

            print("OCR Button Pressed")

            text = ocr.recognize(drawing.canvas)

            print("Recognized Text:", text)

            # If text is detected
            if text.strip():

                # Convert handwriting into typed text
                 
                typedImage = renderer.render(
                    drawing.canvas,
                    text
            )

            pdfPath = pdf.save(text)

            print("PDF Saved:", pdfPath)

            cv2.imshow(
                "Typed Text",
                typedImage
            )

            print("Text converted successfully!")

        else:

            print("No text detected.")


    # ======================================================
    # Release Camera
    # ======================================================

    cap.release()

    cv2.destroyAllWindows()


# ==========================================================
# Program Entry
# ==========================================================

if __name__ == "__main__":
    main()