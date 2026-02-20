from fastapi import APIRouter, UploadFile, File, HTTPException
from app.schemas.upload import UploadResponse
from app.utils.logger import get_logger
import uuid
from app.aws.upload_file import upload_file_to_s3


logger = get_logger(__name__)

router = APIRouter(prefix="/api", tags=["chats"])

@router.post('/upload-chat', response_model=UploadResponse, status_code=201)
async def uploadChat(file : UploadFile = File(...)):
    """
    Api Endpoint to accept and validate whatsapp chats and store it in aws s3 and return the key
    """

    #Validating file type
    if not file.filename or not file.filename.endswith('.txt'):
        logger.warning('File not uploaded. Wrong file format or missing filename')
        raise HTTPException(status_code=400 , detail='Only .txt files are allowed')
    
    uid = uuid.uuid4()
    s3_key = f'raw/{uid}_{file.filename}'

    logger.info('key for S3 object generated successfully')

    try:
        await upload_file_to_s3(file.file, s3_key)
        logger.info('File uploaded successfully')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"some error occured :{e}")
    

    return UploadResponse(
        message = "File Uploaded",
        s3_key = s3_key
    )