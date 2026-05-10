# 错误处理规范

## 响应格式

所有错误统一返回：

```json
{
    "error": {
        "code": "NOT_FOUND",
        "message": "可读的错误描述",
        "detail": "可选的详细信息"
    }
}
```

## 错误码

| HTTP 状态码 | code | 场景 |
|-------------|------|------|
| 400 | `VALIDATION_ERROR` | 请求参数校验失败 |
| 401 | `UNAUTHORIZED` | 缺少或无效的认证信息 |
| 403 | `FORBIDDEN` | 无权访问该资源 |
| 404 | `NOT_FOUND` | 资源不存在 |
| 409 | `CONFLICT` | Law 冲突或资源状态冲突 |
| 429 | `RATE_LIMIT` | 请求频率超限 |
| 500 | `INTERNAL_ERROR` | 服务器内部错误 |
| 502 | `LLM_ERROR` | LLM 调用失败 |

## 异常类

```python
class MeshMindError(Exception):
    status_code: int = 500
    code: str = "INTERNAL_ERROR"

class NotFoundError(MeshMindError):
    status_code = 404; code = "NOT_FOUND"

class UnauthorizedError(MeshMindError):
    status_code = 401; code = "UNAUTHORIZED"

class ForbiddenError(MeshMindError):
    status_code = 403; code = "FORBIDDEN"

class ConflictError(MeshMindError):
    status_code = 409; code = "CONFLICT"

class LLMError(MeshMindError):
    status_code = 502; code = "LLM_ERROR"
```

## FastAPI 异常处理器

```python
@app.exception_handler(MeshMindError)
async def mesh_mind_exception_handler(request, exc: MeshMindError):
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": {"code": exc.code, "message": str(exc)}}
    )
```
