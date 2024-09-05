import logging
import os
import shutil
import azure.functions as func

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

            # Define the output file name (same as input)
            file_name = os.path.basename(PDF_Path)
            out_file_path = os.path.join(Out_Path, file_name)

            # Copy the file from input path to output path
            try:
                shutil.copy2(PDF_Path, out_file_path)
            except Exception as e:
                logging.error(f"Error copying file: {str(e)}")
                return func.HttpResponse(
                    f"Error copying file: {str(e)}",
                    status_code=500
                )

            return func.HttpResponse(f"PDF file processed and saved to {out_file_path}", status_code=200)

        except Exception as e:
            logging.error(f"Unexpected error: {str(e)}")
            return func.HttpResponse(f"An unexpected error occurred: {str(e)}", status_code=500)
    else:
        return func.HttpResponse(
            f"Missing parameters: Approver: {Approver}, PDF_Path: {PDF_Path}, Out_Path: {Out_Path}",
            status_code=400
        )
