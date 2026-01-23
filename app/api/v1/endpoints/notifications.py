from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Optional
from datetime import datetime
import json
import pymysql

from app.database import get_db
from app.schemas.notification import NotificationPush, NotificationQueryResponse, NotificationItem

router = APIRouter()


@router.post(
    "/push",
    summary="信息推送",
<<<<<<< HEAD
    description="推送一条通知信息，记录到user_messages表"
=======
    description="推送一条通知信息，记录到操作日志表（operation_logs）"
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
)
def push_notification(
    payload: NotificationPush,
    db: pymysql.connections.Connection = Depends(get_db),
    # 可接入真实用户：current_user=Depends(get_current_user)
):
    cursor = None
    try:
        cursor = db.cursor()
<<<<<<< HEAD
        insert_sql = (
            "INSERT INTO user_messages (user_id, username, title, content, source, status, received_time) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s)"
=======
        # 组装 operation_params
        op_params = {
            "title": payload.title,
            "content": payload.content,
            "target_user_id": payload.target_user_id,
            "target_username": payload.target_username,
        }
        now = datetime.now()
        # 示例：如果无真实登录，这里使用空用户标识
        user_id = payload.target_user_id or "system"
        username = payload.target_username or "system"
        insert_sql = (
            "INSERT INTO operation_logs (user_id, username, operation_type, operation_path, "
            "operation_params, ip_address, operation_time, status) "
            "VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
        )
        cursor.execute(
            insert_sql,
            (
<<<<<<< HEAD
                payload.target_user_id,
                payload.target_username,
                payload.title,
                payload.content,
                "system",  # 假设来源为系统
                "unread",
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
=======
                user_id,
                username,
                "notify",
                "/api/v1/notifications/push",
                json.dumps(op_params, ensure_ascii=False),
                None,
                now.strftime("%Y-%m-%d %H:%M:%S"),
                "success",
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
            ),
        )
        db.commit()
        return {"message": "推送成功", "id": cursor.lastrowid}
    except pymysql.MySQLError as e:
        db.rollback()
<<<<<<< HEAD
        raise HTTPException(status_code=500, detail=f"推送失败：{str(e)}")
=======
        raise HTTPException(status_code=500, detail=f"日志写入失败：{str(e)}")
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
    finally:
        if cursor:
            cursor.close()


@router.get(
    "/query",
    response_model=NotificationQueryResponse,
    summary="信息查询",
<<<<<<< HEAD
    description="查询通知类消息（user_messages），支持按用户筛选与分页"
=======
    description="查询通知类操作日志（operation_type=notify），支持按用户筛选与分页"
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
)
def query_notifications(
    target_user_id: Optional[str] = Query(None, description="按用户ID筛选"),
    page: int = 1,
    page_size: int = 20,
    db: pymysql.connections.Connection = Depends(get_db),
):
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20

    cursor = None
    try:
        cursor = db.cursor()
<<<<<<< HEAD
        base_where = ""
        params = []
        if target_user_id:
            base_where = "WHERE user_id = %s"
            params.append(target_user_id)

        count_sql = f"SELECT COUNT(*) FROM user_messages {base_where}"
=======
        base_where = "operation_type = 'notify'"
        params = []
        if target_user_id:
            base_where += " AND user_id = %s"
            params.append(target_user_id)

        count_sql = f"SELECT COUNT(*) FROM operation_logs WHERE {base_where}"
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]

        offset = (page - 1) * page_size
        select_sql = (
<<<<<<< HEAD
            "SELECT id, user_id, username, title, content, source, status, received_time "
            f"FROM user_messages {base_where} ORDER BY received_time DESC LIMIT %s OFFSET %s"
=======
            "SELECT id, user_id, username, operation_params, operation_time, status "
            "FROM operation_logs WHERE " + base_where + " ORDER BY operation_time DESC LIMIT %s OFFSET %s"
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
        )
        cursor.execute(select_sql, params + [page_size, offset])
        rows = cursor.fetchall()

        items = []
        for row in rows:
<<<<<<< HEAD
            # row: (id, user_id, username, title, content, source, status, received_time)
=======
            # row: (id, user_id, username, operation_params, operation_time, status)
            try:
                op_params = json.loads(row[3]) if row[3] else {}
            except Exception:
                op_params = {}
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
            items.append(
                NotificationItem(
                    id=row[0],
                    user_id=row[1],
                    username=row[2],
<<<<<<< HEAD
                    title=row[3],
                    content=row[4],
                    target_user_id=row[1],  # 假设目标用户就是接收用户
                    target_username=row[2],
                    operation_time=row[7].strftime("%Y-%m-%d %H:%M:%S") if row[7] else None,
                    status=row[6],
=======
                    title=op_params.get("title", ""),
                    content=op_params.get("content", ""),
                    target_user_id=op_params.get("target_user_id"),
                    target_username=op_params.get("target_username"),
                    operation_time=row[4].strftime("%Y-%m-%d %H:%M:%S") if row[4] else None,
                    status=row[5],
>>>>>>> 40e9b1dd2e386e695098aeeedd9792aeb48569b2
                )
            )

        return NotificationQueryResponse(
            items=items,
            page=page,
            page_size=page_size,
            total=total,
            total_pages=(total + page_size - 1) // page_size,
        )
    except pymysql.MySQLError as e:
        raise HTTPException(status_code=500, detail=f"查询失败：{str(e)}")
    finally:
        if cursor:
            cursor.close()
