"""Document upload endpoint"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import pymysql
from app.database import get_db
from app.services.document import DocumentService
from app.schemas.document import DocumentResponse

router = APIRouter()

# 初始化documents表的函数
def init_documents_table(db: pymysql.connections.Connection):
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS documents (
        id INT AUTO_INCREMENT PRIMARY KEY,
        filename VARCHAR(255) NOT NULL,
        content LONGBLOB NOT NULL,
        content_type VARCHAR(100) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """
    cursor = None
    try:
        cursor = db.cursor()
        cursor.execute(create_table_sql)
        db.commit()
    except pymysql.MySQLError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create documents table: {str(e)}")
    finally:
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass

@router.post("/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...), db: pymysql.connections.Connection = Depends(get_db)):
    """Upload a document and store it in the database."""
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must have a filename")
    if not file.content_type:
        raise HTTPException(status_code=400, detail="Uploaded file must have a content type")
    try:
        content = await file.read()
        if not content:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read uploaded file: {str(e)}")
    cursor = None
    try:
        cursor = db.cursor(pymysql.cursors.DictCursor)
        insert_sql = """
            INSERT INTO documents (filename, content, content_type, created_at)
            VALUES (%s, %s, %s, NOW())
        """
        cursor.execute(insert_sql, (file.filename, content, file.content_type))
        db.commit()
        doc_id = cursor.lastrowid
        doc = {
            "id": doc_id,
            "filename": file.filename,
            "content_type": file.content_type,
            "size": len(content),
            "created_at": cursor.execute("SELECT NOW() as created_at") and cursor.fetchone()["created_at"]
        }
        return doc
    except pymysql.MySQLError as e:
        # 数据库异常回滚事务
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        # 关闭游标
        if cursor:
            try:
                cursor.close()
            except Exception:
                pass
