import logging
import os
import shutil
import azure.functions as func
import fitz  # pymupdf
import datetime

app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)

@app.route(route="WatermarkV2")
def WatermarkV2(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')
    
    # First, try to get the parameters from the URL
    Approver = req.params.get('Approver')
    PDF_Path = req.params.get('PDF_Path')
    Out_Path = req.params.get('Out_Path')

    # If one or more params are missing, try to get them from the body
    if not (Approver and PDF_Path and Out_Path):
        try:
            req_body = req.get_json()
        except ValueError:
            req_body = {}
        
        Approver = Approver or req_body.get('Approver')
        PDF_Path = PDF_Path or req_body.get('PDF_Path')
        Out_Path = Out_Path or req_body.get('Out_Path')
    
    # Check if all parameters are present
    if Approver and PDF_Path and Out_Path:
        try:
            # Check if the input PDF file exists
            if not os.path.exists(PDF_Path):
                return func.HttpResponse(
                    f"Error: Input PDF file at {PDF_Path} not found.",
                    status_code=400
                )

            # Use os.path.splitext() to get file name and extension
            file_name = os.path.splitext(os.path.basename(PDF_Path))[0]
            logging.info(f"Processing file: {file_name}")

            # Open PDF via PyMuPDF
            doc = fitz.open(PDF_Path)
            # Get current time
            now = datetime.datetime.now()
            # Transform to friendly string
            formatted_date = now.strftime("%Y/%#m/%#d %H:%M:%S")
            page = doc[0]  # new page, or choose doc[n]
            # The text strings, each having 3 lines
            remark_text = f"Confirmed by: {Approver}\nConfirm time: {formatted_date}"
            # Get center of the page
            center_x = page.rect.width / 2
            center_y = page.rect.height - 50  # Place the text at the bottom of the page, leaving some whitespace
            p1 = fitz.Point(center_x - 40, center_y + 25)

            # Create a Shape to draw on
            shape = page.new_shape()
            # Insert the text strings
            shape.insert_text(p1, remark_text, color=(1, 0, 0), fontname="helv")
            # Store our work to the page
            shape.commit()

            # Output modified PDF
            output_pdf_path = os.path.join(Out_Path, f"{file_name}_added.pdf")
            doc.save(output_pdf_path)

            # Check if the output directory exists, if not, create it
            if not os.path.exists(Out_Path):
                try:
                    os.makedirs(Out_Path)
                except Exception as e:
                    logging.error(f"Error creating output directory: {str(e)}")
                    return func.HttpResponse(
                        f"Error creating output directory: {str(e)}",
                        status_code=500
                    )

            return func.HttpResponse(f"PDF file processed and saved to {output_pdf_path}", status_code=200)

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return func.HttpResponse(f"An unexpected error occurred: {str(e)}", status_code=500)
    else:
        return func.HttpResponse(
            f"Missing parameters: Approver: {Approver}, PDF_Path: {PDF_Path}, Out_Path: {Out_Path}",
            status_code=400
        )
