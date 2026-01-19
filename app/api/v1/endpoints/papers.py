from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, BackgroundTasks
from typing import List
import os
from app.core.dependencies import get_current_user
from app.schemas.document import PaperCreate, PaperOut, VersionOut
from app.services.oss import upload_file_to_oss
from datetime import datetime  
from app.database import get_db
import pymysql 

router = APIRouter()

def init_paper_tables():
    """初始化papers和paper_versions表（确保表存在）"""
    db = None
    cursor = None
    try:
        db = get_db() if callable(get_db) else pymysql.connect(
            host=os.getenv("DB_HOST", "localhost"),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "paper_management"),
            charset="utf8mb4"
        )
        cursor = db.cursor()

        # 创建papers主表
        create_papers_table = """
        CREATE TABLE IF NOT EXISTS papers (
            id INT AUTO_INCREMENT PRIMARY KEY,
            owner_id INT NOT NULL,
            latest_version VARCHAR(20) NOT NULL,
            oss_key VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL,
            updated_at DATETIME NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文基础信息表';
        """
        cursor.execute(create_papers_table)

        # 创建paper_versions版本表
        create_versions_table = """
        CREATE TABLE IF NOT EXISTS paper_versions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            paper_id INT NOT NULL,
            version VARCHAR(20) NOT NULL,
            size INT NOT NULL,
            created_at DATETIME NOT NULL,
            status VARCHAR(20) NOT NULL,
            FOREIGN KEY (paper_id) REFERENCES papers(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='论文版本信息表';
        """
        cursor.execute(create_versions_table)

        add_indexes = [
            "CREATE INDEX IF NOT EXISTS idx_papers_owner_id ON papers(owner_id);",
            "CREATE INDEX IF NOT EXISTS idx_paper_versions_paper_id ON paper_versions(paper_id);",
            "CREATE INDEX IF NOT EXISTS idx_paper_versions_version ON paper_versions(version);"
        ]
        for idx_sql in add_indexes:
            cursor.execute(idx_sql)

        db.commit()
        print("论文相关数据表初始化成功（表已存在则忽略）")
    except pymysql.MySQLError as e:
        if db:
            db.rollback()
        print(f"初始化论文数据表失败: {str(e)}")
        raise
    finally:
        if cursor:
            cursor.close()
        if db:
            db.close()

@router.post("/upload", response_model=PaperOut)
async def upload_paper(
    file: UploadFile = File(...),
    db: pymysql.connections.Connection = Depends(get_db),
    # current_user=Depends(get_current_user),
):
    current_user = {"sub": 1}  # 模拟“已登录”
    # 验证文件扩展名
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="仅支持 .docx 格式")
    contents = await file.read()
    size = len(contents)
    if size > 100 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="文件大小超过 100MB")

    # 简单 OSS 上传（返回一个 oss_key）
    oss_key = upload_file_to_oss(file.filename, contents)

    # TODO: persist to DB, create paper record and initial version v1.0
    # 持久化到数据库：创建paper记录和初始版本v1.0
    cursor = None 
    try:
        cursor = db.cursor()
        user_id = current_user.get("sub", 0)
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        version = "v1.0"
        # 插入papers主表
        paper_sql = """
        INSERT INTO papers (owner_id, latest_version, oss_key, created_at, updated_at)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(paper_sql, (user_id, version, oss_key, now, now))
        paper_id = cursor.lastrowid 
        version_sql = """
        INSERT INTO paper_versions (paper_id, version, size, created_at, status)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(version_sql, (paper_id, version, size, now, "ok"))
        db.commit()
    except pymysql.MySQLError as e:
        db.rollback() 
        raise HTTPException(status_code=500, detail=f"数据库操作失败: {str(e)}")
    finally:
        if cursor: 
            cursor.close()
        db.close()

    return PaperOut(id=paper_id, owner_id=current_user.get("sub", 0), latest_version=version, oss_key=oss_key)


@router.get("/{paper_id}/versions", response_model=List[VersionOut])
def list_versions(
    paper_id: int,
    # current_user=Depends(get_current_user),  # 保留验证代码，注释掉
    db: pymysql.connections.Connection = Depends(get_db) 
):
    # 模拟“已登录”，和第一个接口的模拟逻辑保持一致
    current_user = {"sub": 1}
    # 实际业务逻辑：查询该paper_id对应的版本列表
    cursor = None
    try:
        cursor = db.cursor()
        # 验证paper归属
        check_owner_sql = "SELECT owner_id FROM papers WHERE id = %s"
        cursor.execute(check_owner_sql, (paper_id,))
        paper_info = cursor.fetchone()
        if not paper_info:
            raise HTTPException(status_code=404, detail="论文不存在")
        if paper_info[0] != current_user.get("sub"):
            raise HTTPException(status_code=403, detail="无权限查看该论文版本")
        # 查询版本表
        version_sql = """
        SELECT version, size, created_at, status 
        FROM paper_versions 
        WHERE paper_id = %s 
        ORDER BY created_at DESC
        """
        cursor.execute(version_sql, (paper_id,))
        versions = cursor.fetchall()
        # 组装返回数据
        result = []
        for version in versions:
            result.append(VersionOut(
                version=version[0],
                size=version[1],
                created_at=version[2].strftime("%Y-%m-%dT%H:%M:%SZ"),  # 格式化时间
                status=version[3]
            ))
        return result
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"数据库查询失败: {str(e)}")
    finally:
        if cursor:
            cursor.close()
        db.close()
    return [VersionOut(version="v1.0", size=12345, created_at="2025-01-01T00:00:00Z", status="ok")]
