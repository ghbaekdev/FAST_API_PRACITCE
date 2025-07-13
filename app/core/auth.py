from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from app.core.security import verify_token

# HTTP Bearer 토큰 스키마
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 인증된 사용자를 가져오는 가드 함수"""
    token = credentials.credentials
    
    # 토큰 검증
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # 사용자 ID 추출 (토큰에서 sub 필드 사용)
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return {"user_id": user_id, "token_payload": payload}

async def get_current_active_user(current_user: dict = Depends(get_current_user)):
    """현재 활성 사용자를 가져오는 가드 함수"""
    # 여기서 사용자 상태를 확인할 수 있습니다
    # 예: 계정 비활성화, 삭제된 사용자 등
    return current_user

# 선택적 인증 (토큰이 있으면 사용자 정보 반환, 없으면 None)
async def get_optional_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)):
    """선택적 인증 - 토큰이 없어도 에러를 발생시키지 않음"""
    if credentials is None:
        return None
    
    token = credentials.credentials
    payload = verify_token(token)
    if payload is None:
        return None
    
    user_id: Optional[str] = payload.get("sub")
    if user_id is None:
        return None
    
    return {"user_id": user_id, "token_payload": payload} 